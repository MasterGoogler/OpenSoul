import asyncio
import json
import os
from datetime import datetime

import requests
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput, Script, Opcode
from wallet import Wallet

API_BASE = Wallet.set_api_base(mainnet=True)
CACHE_FILE = "audit_cache.json"  # local file for last_txid + last_utxo info
import asyncio
import json
import os
from datetime import datetime

import requests
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput, Script, Opcode
from wallet import Wallet

API_BASE = Wallet.set_api_base(mainnet=True)
CACHE_FILE = "audit_cache.json"  # local file for last_txid + last_utxo info

class AuditLogger:
    BATCH_FILE = "audit_batch.json"
        # All wallet/key management, payments, address book, etc. are now in wallet.py (Wallet class)
    def __init__(self, priv_wif: str, config: dict = None):
        self.priv_key = PrivateKey(priv_wif)
        self.address = self.priv_key.address(compressed=True)  # P2PKH default
        self.config = config or {"mode": "session", "min_actions": 1, "max_payload_kb": 4, "batch_mode": "memory"}
        self.session_start = datetime.utcnow().isoformat() + "Z"
        self._load_cache()
        self._init_batch()
    """
    Immutable, on-chain audit logger for AI agents using BSV.
    Usage:
        logger = AuditLogger(priv_wif, config={"agent_id": "my-agent", ...})
        logger.log({...})
        await logger.flush()
    """

    def _init_batch(self):
        if self.config.get("batch_mode", "memory") == "file":
            if os.path.exists(self.BATCH_FILE):
                with open(self.BATCH_FILE, "r") as f:
                    try:
                        self.actions = json.load(f)
                    except Exception:
                        self.actions = []
            else:
                self.actions = []
        else:
            self.actions = []

    def _load_cache(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
                if cache.get("address") == self.address:
                    self.last_txid = cache.get("last_txid")
                    self.last_utxo = cache.get("last_utxo")  # {'txid', 'vout', 'value'}
                    return
        self.last_txid = None
        self.last_utxo = None

    def _save_cache(self, txid, utxo):
        cache = {"address": self.address, "last_txid": txid, "last_utxo": utxo}
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)

    def log(self, entry: dict):
        """Add a metric/action to batch. entry e.g. {'tokens_in': int, 'tokens_out': int, ...}"""
        entry["ts"] = datetime.utcnow().isoformat() + "Z"
        self.actions.append(entry)
        if self.config.get("batch_mode", "memory") == "file":
            import fcntl
            with open(self.BATCH_FILE, "w") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(self.actions, f)
                fcntl.flock(f, fcntl.LOCK_UN)

    async def flush(self):
        if self.config.get("batch_mode", "memory") == "file":
            import fcntl
            # Reload from file in case of crash recovery
            if os.path.exists(self.BATCH_FILE):
                with open(self.BATCH_FILE, "r") as f:
                    fcntl.flock(f, fcntl.LOCK_SH)
                    try:
                        self.actions = json.load(f)
                    except Exception:
                        self.actions = []
                    fcntl.flock(f, fcntl.LOCK_UN)
        if not self.actions:
            return  # nothing to log

        # Check config
        if self.config["mode"] == "session" or len(self.actions) >= self.config["min_actions"]:
            await self._write_to_chain()
            self.actions = []  # clear after write
            if self.config.get("batch_mode", "memory") == "file":
                # Clear file after flush
                with open(self.BATCH_FILE, "w") as f:
                    json.dump([], f)

    async def _write_to_chain(self):
        import gzip
        # Get current UTXO (prefer cache, fallback to query)
        utxo = self.last_utxo or await self._query_current_utxo()
        if not utxo:
            raise ValueError("No UTXO found for address - fund it first")

        # Fetch source tx hex
        source_tx_hex = await self._fetch_tx_hex(utxo["txid"])
        source_tx = Transaction.from_hex(source_tx_hex)

        # Build payload
        # Build payload
        payload = {
            "agent_id": self.config.get("agent_id", "default-agent"),
            "session_start": self.session_start,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": self.actions,
        }
        data = json.dumps(payload).encode("utf-8")
        if len(data) > self.config["max_payload_kb"] * 1024:
            # Compress if too large
            data = gzip.compress(data)
            if len(data) > self.config["max_payload_kb"] * 1024:
                raise ValueError("Payload too large even after compression")

        # Build tx
        tx_input = TransactionInput(
            source_transaction=source_tx,
            source_txid=utxo["txid"],
            source_output_index=utxo["vout"],
            unlocking_script_template=P2PKH().unlock(self.priv_key),
        )

        op_return_script = Script() \
            .add(Opcode.OP_RETURN) \
            .push_data(data)
        op_return_out = TransactionOutput(locking_script=op_return_script, satoshis=0)

        # Fee estimate (SDK auto or simple)
        fee_sat = 300  # low estimate; use tx.fee() after build for accuracy
        change_sat = utxo["value"] - fee_sat
        if change_sat <= 546:  # dust limit approx
            raise ValueError("Insufficient for fee")

        change_out = TransactionOutput(
            locking_script=P2PKH().lock(self.address),
            satoshis=change_sat
        )

        tx = Transaction(inputs=[tx_input], outputs=[op_return_out, change_out], version=1)
        tx.sign()  # SDK handles

        # Broadcast
        tx_hex = tx.hex()
        resp = requests.post(f"{API_BASE}/tx/raw", json={"txhex": tx_hex})
        if resp.status_code != 200:
            raise RuntimeError(f"Broadcast failed: {resp.text}")
        txid = resp.json().get("txid") or tx.txid()  # some return txid

        # Update cache
        new_utxo = {"txid": txid, "vout": 1, "value": change_sat}  # change is output 1
        self._save_cache(txid, new_utxo)
        print(f"Logged session to tx {txid}")

    async def _query_current_utxo(self):
        resp = requests.get(f"{API_BASE}/address/{self.address}/unspent")
        utxos = resp.json()
        if not utxos:
            return None
        # Pick latest/confirmed or highest value
        utxo = max(utxos, key=lambda u: u.get("height", 0) or u["value"])
        return {"txid": utxo["txid"], "vout": utxo["vout"], "value": utxo["value"]}

    async def _fetch_tx_hex(self, txid: str):
        # WhatsOnChain often has /tx/{txid}/hex or parse from /tx/{txid}
        resp = requests.get(f"{API_BASE}/tx/{txid}/hex")
        if resp.status_code == 200:
            return resp.text.strip()
        # Fallback: get /tx/{txid}, extract 'hex' if present
        resp = requests.get(f"{API_BASE}/tx/{txid}")
        data = resp.json()
        if "hex" in data:
            return data["hex"]
        raise ValueError(f"Could not fetch hex for {txid}")

    async def get_history(self):
        # Trace back from current UTXO, collect OP_RETURN JSONs
        utxo = await self._query_current_utxo()
        if not utxo:
            return []

        logs = []
        current_txid = utxo["txid"]
        while current_txid:
            tx_data = requests.get(f"{API_BASE}/tx/{current_txid}").json()
            op_return = None
            for out in tx_data.get("vout", []):
                if out["value"] == 0 and "scriptPubKey" in out:
                    script_hex = out["scriptPubKey"]["hex"]
                    if script_hex.startswith("6a"):  # OP_RETURN
                        # Parse data (skip OP_RETURN + push)
                        push_byte = int(script_hex[2:4], 16)
                        data_start = 2 + (1 if push_byte < 76 else 2)  # simple
                        data_hex = script_hex[data_start*2:]
                        try:
                            data = bytes.fromhex(data_hex).decode("utf-8")
                            op_return = json.loads(data)
                        except:
                            op_return = {"raw": data_hex}
                        break
            if op_return:
                logs.append(op_return)

            # Find prev input (assume first input is chain)
            if tx_data.get("vin"):
                prev_txid = tx_data["vin"][0]["txid"]
                current_txid = prev_txid if prev_txid != "0"*64 else None
            else:
                break

        logs.reverse()  # chrono order
        return logs
