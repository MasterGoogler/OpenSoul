import requests
from bsv import PrivateKey, P2PKH, Transaction, TransactionInput, TransactionOutput

API_BASE_MAIN = "https://api.whatsonchain.com/v1/bsv/main"
API_BASE_TEST = "https://api.whatsonchain.com/v1/bsv/test"

class Wallet:
    @staticmethod
    def generate_keypair():
        priv = PrivateKey()
        wif = priv.to_wif()
        address = priv.address(compressed=True)
        return {"wif": wif, "address": address}
    """
    Wallet management for BSV: keypair generation, payments, balance, address book, backup/restore, and more.
    Usage:
        kp = Wallet.generate_keypair()
        addr = Wallet.wif_to_address(kp['wif'])
        bal = Wallet.get_balance(addr)
        txid = Wallet.send_payment(kp['wif'], 'recipient_addr', 1000)
    """

    @staticmethod
    def wif_to_address(wif: str):
        priv = PrivateKey(wif)
        return priv.address(compressed=True)

    @staticmethod
    def get_balance(address: str, api_base=API_BASE_MAIN):
        resp = requests.get(f"{api_base}/address/{address}/balance")
        data = resp.json()
        return data.get("confirmed", 0) + data.get("unconfirmed", 0)

    @staticmethod
    def get_tx_history(address: str, api_base=API_BASE_MAIN):
        resp = requests.get(f"{api_base}/address/{address}/txs")
        return resp.json()

    @staticmethod
    def send_payment(priv_wif: str, to_address: str, amount_sat: int, fee_sat: int = 300, api_base=API_BASE_MAIN):
        priv = PrivateKey(priv_wif)
        from_address = priv.address(compressed=True)
        utxos = requests.get(f"{api_base}/address/{from_address}/unspent").json()
        utxo = max(utxos, key=lambda u: u.get("height", 0) or u["value"]) if utxos else None
        if not utxo or utxo["value"] < amount_sat + fee_sat:
            raise ValueError("Insufficient funds")
        source_tx_hex = requests.get(f"{api_base}/tx/{utxo['txid']}/hex").text.strip()
        source_tx = Transaction.from_hex(source_tx_hex)
        tx_input = TransactionInput(
            source_transaction=source_tx,
            source_txid=utxo["txid"],
            source_output_index=utxo["vout"],
            unlocking_script_template=P2PKH().unlock(priv),
        )
        change_sat = utxo["value"] - amount_sat - fee_sat
        outputs = [
            TransactionOutput(locking_script=P2PKH().lock(to_address), satoshis=amount_sat)
        ]
        if change_sat > 546:
            outputs.append(TransactionOutput(locking_script=P2PKH().lock(from_address), satoshis=change_sat))
        tx = Transaction(inputs=[tx_input], outputs=outputs, version=1)
        tx.sign()
        tx_hex = tx.hex()
        resp = requests.post(f"{api_base}/tx/raw", json={"txhex": tx_hex})
        if resp.status_code != 200:
            raise RuntimeError(f"Broadcast failed: {resp.text}")
        return resp.json().get("txid") or tx.txid()

    address_book = {}
    @classmethod
    def add_address(cls, label: str, address: str):
        cls.address_book[label] = address
    @classmethod
    def get_address(cls, label: str):
        return cls.address_book.get(label)

    @staticmethod
    def backup_key(wif: str, path: str):
        with open(path, "w") as f:
            f.write(wif)
    @staticmethod
    def restore_key(path: str):
        with open(path, "r") as f:
            return f.read().strip()

    @staticmethod
    def create_multisig(*pubkeys):
        return f"multisig({','.join(pubkeys)})"

    @staticmethod
    def encrypt_wif(wif: str, passphrase: str):
        # Simple XOR encryption for demonstration (replace with real crypto in production)
        enc = ''.join(chr(ord(c) ^ ord(passphrase[i % len(passphrase)])) for i, c in enumerate(wif))
        return enc.encode('utf-8').hex()
    @staticmethod
    def decrypt_wif(enc: str, passphrase: str):
        raw = bytes.fromhex(enc).decode('utf-8')
        wif = ''.join(chr(ord(c) ^ ord(passphrase[i % len(passphrase)])) for i, c in enumerate(raw))
        return wif

    @staticmethod
    def watch_only(address: str):
        return {"address": address, "watch_only": True}

    @staticmethod
    def set_api_base(mainnet=True):
        return API_BASE_MAIN if mainnet else API_BASE_TEST

    @staticmethod
    def estimate_fee():
        return 300  # Replace with dynamic estimation as needed
