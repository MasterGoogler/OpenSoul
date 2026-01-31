"""
private_data_utils.py - Encrypted/private data storage utilities for OpenSoul agents

Provides functions to store encrypted data on-chain (e.g., encrypted OP_RETURN, sCrypt).
"""

from pgp_utils import PGPManager
from bsv import TransactionOutput, Script, Opcode

class PrivateDataUtils:
    @staticmethod
    def create_encrypted_opreturn(data: str, pgp: PGPManager) -> TransactionOutput:
        encrypted = pgp.encrypt(data)
        script = Script().add(Opcode.OP_RETURN).push_data(encrypted.encode('utf-8'))
        return TransactionOutput(locking_script=script, satoshis=0)

    @staticmethod
    def decrypt_opreturn(encrypted_data: str, pgp: PGPManager) -> str:
        return pgp.decrypt(encrypted_data)

# Example usage:
# out = PrivateDataUtils.create_encrypted_opreturn('secret', pgp)
# msg = PrivateDataUtils.decrypt_opreturn(encrypted_data, pgp)
