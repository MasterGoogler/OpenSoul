"""
payment_channel.py - Simple Payment Channel utilities for OpenSoul agents (BSV)

Implements basic open, update, and close channel logic using BSV transactions.
"""

from bsv import PrivateKey, Transaction, TransactionInput, TransactionOutput, P2PKH, Script, Opcode
import requests
import time

class PaymentChannel:
    def __init__(self, sender_priv_wif, receiver_address, api_base, channel_amount):
        self.sender_priv = PrivateKey(sender_priv_wif)
        self.sender_address = self.sender_priv.address(compressed=True)
        self.receiver_address = receiver_address
        self.api_base = api_base
        self.channel_amount = channel_amount
        self.channel_utxo = None
        self.channel_txid = None

    def open_channel(self):
        # Lock funds in a 2-of-2 multisig (sender+receiver)
        # For demo: use P2PKH to receiver, but in production use multisig or script
        utxos = requests.get(f"{self.api_base}/address/{self.sender_address}/unspent").json()
        utxo = max(utxos, key=lambda u: u.get("height", 0) or u["value"]) if utxos else None
        if not utxo or utxo["value"] < self.channel_amount + 300:
            raise ValueError("Insufficient funds for channel")
        source_tx_hex = requests.get(f"{self.api_base}/tx/{utxo['txid']}/hex").text.strip()
        source_tx = Transaction.from_hex(source_tx_hex)
        tx_input = TransactionInput(
            source_transaction=source_tx,
            source_txid=utxo["txid"],
            source_output_index=utxo["vout"],
            unlocking_script_template=P2PKH().unlock(self.sender_priv),
        )
        out = TransactionOutput(locking_script=P2PKH().lock(self.receiver_address), satoshis=self.channel_amount)
        change = utxo["value"] - self.channel_amount - 300
        outputs = [out]
        if change > 546:
            outputs.append(TransactionOutput(locking_script=P2PKH().lock(self.sender_address), satoshis=change))
        tx = Transaction(inputs=[tx_input], outputs=outputs, version=1)
        tx.sign()
        tx_hex = tx.hex()
        resp = requests.post(f"{self.api_base}/tx/raw", json={"txhex": tx_hex})
        if resp.status_code != 200:
            raise RuntimeError(f"Broadcast failed: {resp.text}")
        self.channel_txid = resp.json().get("txid") or tx.txid()
        self.channel_utxo = {"txid": self.channel_txid, "vout": 0, "value": self.channel_amount}
        return self.channel_txid

    def create_payment_update(self, amount):
        # Create an off-chain signed transaction spending the channel UTXO to receiver for 'amount'
        if not self.channel_utxo:
            raise ValueError("Channel not open")
        tx_input = TransactionInput(
            source_txid=self.channel_utxo["txid"],
            source_output_index=self.channel_utxo["vout"],
            unlocking_script_template=P2PKH().unlock(self.sender_priv),
        )
        out = TransactionOutput(locking_script=P2PKH().lock(self.receiver_address), satoshis=amount)
        change = self.channel_utxo["value"] - amount
        outputs = [out]
        if change > 546:
            outputs.append(TransactionOutput(locking_script=P2PKH().lock(self.sender_address), satoshis=change))
        tx = Transaction(inputs=[tx_input], outputs=outputs, version=1)
        tx.sign()
        return tx.hex()  # This hex can be sent to the receiver off-chain

    def close_channel(self, payment_tx_hex):
        # Broadcast the final payment transaction to settle the channel
        resp = requests.post(f"{self.api_base}/tx/raw", json={"txhex": payment_tx_hex})
        if resp.status_code != 200:
            raise RuntimeError(f"Broadcast failed: {resp.text}")
        return resp.json().get("txid")

# Example usage:
# channel = PaymentChannel(sender_priv_wif, receiver_address, api_base, 10000)
# channel.open_channel()
# update_hex = channel.create_payment_update(5000)
# ... send update_hex to receiver ...
# channel.close_channel(update_hex)
