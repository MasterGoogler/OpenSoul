Step-by-Step Build PlanEnvironment SetupPython 3.10+ (3.12 recommended).
Install deps:

pip install bsv-sdk requests

Create a project dir:

mkdir bsv-audit-logger && cd bsv-audit-logger
touch audit_logger.py test_logger.py

Private Key & AddressGenerate a new key for testing (or use an existing WIF securely via .env).python

from bsv import PrivateKey
priv = PrivateKey()  # random new key
print("WIF:", priv.wif())
print("Address:", priv.address())

Fund it: Send ~10,000-50,000 sats (0.0001-0.0005 BSV) from any wallet (e.g., MoneyButton, ElectrumSV, or exchange). Confirm on whatsonchain.com/address/{your_addr}. This creates the initial UTXO(s).

Implement the AuditLogger Class
Paste this updated version into audit_logger.py. Changes from previous:Uses await tx.broadcast() (SDK-native, simpler/no manual POST).
Auto-change handling via change=True (SDK deducts fee automatically).
Better OP_RETURN via Script.
Added dry_run option to print hex instead of broadcast (for testing without funds).
Minor robustness (e.g., better parsing, error handling stubs).

python

import asyncio
import json
import os
from datetime import datetime
import requests
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput, Script, Opcode

API_BASE = "https://api.whatsonchain.com/v1/bsv/main"
CACHE_FILE = "audit_cache.json"

class AuditLogger:
    def __init__(self, priv_wif: str, config: dict = None, dry_run: bool = False):
        self.priv_key = PrivateKey(priv_wif)
        self.address = self.priv_key.address(compressed=True)
        self.config = config or {"mode": "session", "min_actions": 1, "max_payload_kb": 4}
        self.actions = []  # batch for current session
        self.session_start = datetime.utcnow().isoformat() + "Z"
        self.dry_run = dry_run
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
                if cache.get("address") == str(self.address):
                    self.last_txid = cache.get("last_txid")
                    self.last_utxo = cache.get("last_utxo")
                    return
        self.last_txid = None
        self.last_utxo = None

    def _save_cache(self, txid, utxo):
        cache = {"address": str(self.address), "last_txid": txid, "last_utxo": utxo}
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)

    def log(self, entry: dict):
        entry["ts"] = datetime.utcnow().isoformat() + "Z"
        self.actions.append(entry)

    async def flush(self):
        if not self.actions:
            return
        if self.config["mode"] == "session" or len(self.actions) >= self.config["min_actions"]:
            await self._write_to_chain()
            self.actions = []

    async def _write_to_chain(self):
        utxo = self.last_utxo or await self._query_current_utxo()
        if not utxo:
            raise ValueError(f"No UTXO for {self.address} - fund it first!")

        # Fetch source tx hex
        source_tx_hex = await self._fetch_tx_hex(utxo["txid"])
        source_tx = Transaction.from_hex(source_tx_hex)

        # Payload
        payload = {
            "agent_id": "your-agent-id",  # customize
            "session_start": self.session_start,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": self.actions,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        if len(data_bytes) > self.config["max_payload_kb"] * 1024:
            raise ValueError("Payload exceeds limit - add compression later")

        # Build tx
        tx_input = TransactionInput(
            source_transaction=source_tx,
            source_txid=utxo["txid"],
            source_output_index=utxo["vout"],
            unlocking_script_template=P2PKH().unlock(self.priv_key),
        )

        op_return_script = Script() \
            .add(Opcode.OP_RETURN) \
            .push_data(data_bytes)
        op_return_out = TransactionOutput(locking_script=op_return_script, satoshis=0)

        change_out = TransactionOutput(
            locking_script=P2PKH().lock(self.address),
            change=True  # SDK auto-calcs value after fee
        )

        tx = Transaction(inputs=[tx_input], outputs=[op_return_out, change_out], version=1)
        tx.fee()  # calc fee
        tx.sign()

        if self.dry_run:
            print("Dry run hex:", tx.hex())
            print("Would broadcast txid:", tx.txid())
            return tx.txid()

        await tx.broadcast()
        txid = tx.txid()
        print(f"Broadcast success: {txid}")

        # Update cache (assume change is output index 1)
        new_utxo = {"txid": txid, "vout": 1, "value": utxo["value"] - 300}  # approx, SDK handles real
        self._save_cache(txid, new_utxo)
        return txid

    async def _query_current_utxo(self):
        resp = requests.get(f"{API_BASE}/address/{self.address}/unspent")
        if resp.status_code != 200:
            raise RuntimeError(f"UTXO query failed: {resp.text}")
        utxos = resp.json()
        if not utxos:
            return None
        # Latest by height or value
        utxo = max(utxos, key=lambda u: u.get("height", 0) or u["value"])
        return {"txid": utxo["txid"], "vout": utxo["vout"], "value": utxo["value"]}

    async def _fetch_tx_hex(self, txid: str):
        resp = requests.get(f"{API_BASE}/tx/{txid}/hex")
        if resp.status_code == 200:
            return resp.text.strip()
        resp = requests.get(f"{API_BASE}/tx/{txid}")
        data = resp.json()
        if "hex" in data:
            return data["hex"]
        raise ValueError(f"Failed to fetch hex for {txid}")

    async def get_history(self):
        utxo = await self._query_current_utxo()
        if not utxo:
            return []
        logs = []
        current_txid = utxo["txid"]
        while current_txid and current_txid != "0" * 64:
            tx_data = requests.get(f"{API_BASE}/tx/{current_txid}").json()
            op_return = None
            for out in tx_data.get("vout", []):
                if out.get("value") == 0 and "scriptPubKey" in out:
                    script_hex = out["scriptPubKey"]["hex"]
                    if script_hex.startswith("6a"):
                        # Parse pushdata
                        op = int(script_hex[2:4], 16)
                        if op < 76:
                            data_start = 2
                        else:
                            data_start = 2 + (op - 75)  # rough for OP_PUSHDATA1/2
                        data_hex = script_hex[data_start * 2:]
                        try:
                            data = bytes.fromhex(data_hex).decode("utf-8")
                            op_return = json.loads(data)
                        except Exception as e:
                            op_return = {"parse_error": str(e), "raw": data_hex}
                        break
            if op_return:
                logs.append(op_return)
            # Prev input (assume chain input is first)
            if tx_data.get("vin"):
                prev_txid = tx_data["vin"][0].get("txid")
                current_txid = prev_txid if prev_txid else None
            else:
                break
        logs.reverse()
        return logs

Test It
Create test_logger.py:python

import asyncio
from audit_logger import AuditLogger
import os

async def main():
    logger = AuditLogger(priv_wif=os.getenv("BSV_PRIV_WIF"), dry_run=True)  # dry_run first!
    logger.log({"tokens_in": 4500, "tokens_out": 3200, "action": "query"})
    logger.log({"tokens_in": 1200, "tokens_out": 800, "action": "tool_call"})
    await logger.flush()
    history = await logger.get_history()
    print("History:", json.dumps(history, indent=2))

if __name__ == "__main__":
    asyncio.run(main())

Set BSV_PRIV_WIF=your_wif_here in env.
Run with dry_run=True → see hex/txid without spending.
Once happy, set dry_run=False and test real broadcast (after funding).

Next Iterations (After First Successful Log)Add cumulative totals: in _write_to_chain, call await self.get_history() and sum tokens.
Threshold mode: e.g., if total tokens > 10k, flush mid-session.
Testnet: Check SDK docs for network config (likely PrivateKey.from_wif(wif, network='test') or global setting). Use testnet faucets.
Error handling: Add retries for API calls, confirmation check (poll /tx/{txid}/status).
Genesis log: Add a init_chain() method for first OP_RETURN if no UTXO.

Run the test script, share output/errors (e.g., if broadcast fails, check funds/fee), and we can debug/refine live. What's your first test case—dry run or real tx? 

