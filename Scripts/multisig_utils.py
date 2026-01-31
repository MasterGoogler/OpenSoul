"""
multisig_utils.py - Multi-signature wallet utilities for OpenSoul agents (BSV)

Provides functions for m-of-n address creation and multi-sig transaction signing.
"""


from bsv import PrivateKey, Script, Opcode, Transaction, TransactionInput, TransactionOutput, P2PKH
import requests
from typing import List, Optional

class MultisigWallet:
    @staticmethod
    def get_utxos(address: str, api_base: str = "https://api.whatsonchain.com/v1/bsv/main") -> list:
        """Query UTXOs for a given address (P2SH, P2PKH, or script)."""
        resp = requests.get(f"{api_base}/address/{address}/unspent")
        if resp.status_code != 200:
            raise RuntimeError(f"UTXO query failed: {resp.text}")
        return resp.json()

    @staticmethod
    def fund_script_address(from_priv_wif: str, script_address: str, amount: int, api_base: str = "https://api.whatsonchain.com/v1/bsv/main") -> str:
        """Send BSV to a script/multisig address to fund it."""
        priv = PrivateKey(from_priv_wif)
        from_address = priv.address(compressed=True)
        utxos = MultisigWallet.get_utxos(from_address, api_base)
        utxo = max(utxos, key=lambda u: u.get("height", 0) or u["value"]) if utxos else None
        if not utxo or utxo["value"] < amount + 300:
            raise ValueError("Insufficient funds")
        source_tx_hex = requests.get(f"{api_base}/tx/{utxo['txid']}/hex").text.strip()
        source_tx = Transaction.from_hex(source_tx_hex)
        tx_input = TransactionInput(
            source_transaction=source_tx,
            source_txid=utxo["txid"],
            source_output_index=utxo["vout"],
            unlocking_script_template=P2PKH().unlock(priv),
        )
        out = TransactionOutput(locking_script=P2PKH().lock(script_address), satoshis=amount)
        change = utxo["value"] - amount - 300
        outputs = [out]
        if change > 546:
            outputs.append(TransactionOutput(locking_script=P2PKH().lock(from_address), satoshis=change))
        tx = Transaction(inputs=[tx_input], outputs=outputs, version=1)
        tx.sign()
        tx_hex = tx.hex()
        resp = requests.post(f"{api_base}/tx/raw", json={"txhex": tx_hex})
        if resp.status_code != 200:
            raise RuntimeError(f"Broadcast failed: {resp.text}")
        return resp.json().get("txid") or tx.txid()

    @staticmethod
    def create_multisig_address(pubkeys: List[str], m: int) -> str:
        """
        Create an m-of-n multisig P2SH address from a list of public keys.
        """
        script = MultisigWallet.create_redeem_script(pubkeys, m)
        return script.address(network='main')


    @staticmethod
    def create_redeem_script(pubkeys: List[str], m: int) -> Script:
        script = Script()
        script.add(Opcode.OP_n(m))
        for pub in pubkeys:
            script.push_data(bytes.fromhex(pub))
        script.add(Opcode.OP_n(len(pubkeys)))
        script.add(Opcode.OP_CHECKMULTISIG)
        return script

    @staticmethod
    def create_timelock_script(pubkey: str, locktime: int) -> Script:
        script = Script()
        script.add(locktime)
        script.add(Opcode.OP_CHECKLOCKTIMEVERIFY)
        script.add(Opcode.OP_DROP)
        script.add(Opcode.OP_DUP)
        script.add(Opcode.OP_HASH160)
        script.push_data(bytes.fromhex(pubkey))
        script.add(Opcode.OP_EQUALVERIFY)
        script.add(Opcode.OP_CHECKSIG)
        return script

    @staticmethod
    def create_conditional_script(pubkey1: str, pubkey2: str) -> Script:
        script = Script()
        script.add(Opcode.OP_IF)
        script.push_data(bytes.fromhex(pubkey1))
        script.add(Opcode.OP_CHECKSIG)
        script.add(Opcode.OP_ELSE)
        script.push_data(bytes.fromhex(pubkey2))
        script.add(Opcode.OP_CHECKSIG)
        script.add(Opcode.OP_ENDIF)
        return script


    @staticmethod
    def sign_multisig_tx(tx: Transaction, priv_keys: List[PrivateKey], redeem_script: Script):
        """
        Sign a multisig transaction with the given private keys and redeem script.
        Each input must be signed by at least m keys.
        """
        # This is a simplified example; actual implementation may require more handling
        for i, txin in enumerate(tx.inputs):
            sigs = []
            for priv in priv_keys:
                sig = tx.sign_input(i, priv, redeem_script)
                sigs.append(sig)
            # Combine signatures and set scriptSig (depends on SDK)
            # ...
        return tx

    @staticmethod
    def electrumsv_compat_export(pubkeys: List[str], m: int) -> dict:
        """
        Export multisig wallet info in ElectrumSV-compatible format.
        """
        return {
            "type": "multisig",
            "m": m,
            "n": len(pubkeys),
            "pubkeys": pubkeys
        }

    @staticmethod
    def handcash_compat_note():
        """
        HandCash currently does not support custom scripts or multisig. Use for reference only.
        """
        return "HandCash does not support custom scripts or multisig. Use P2PKH for compatibility."

# Example usage:
# pubkeys = [pub1, pub2, pub3]
# addr = MultisigWallet.create_multisig_address(pubkeys, 2)
# redeem_script = MultisigWallet.create_redeem_script(pubkeys, 2)
# MultisigWallet.sign_multisig_tx(tx, [priv1, priv2], redeem_script)
