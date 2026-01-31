"""
pgp_utils.py - PGP encryption/decryption utilities for OpenSoul agents

This module provides functions to encrypt data with a PGP public key and decrypt with a private key.
Uses the 'pgpy' library for OpenPGP operations.
"""

import pgpy
from typing import Union

class PGPManager:
    def __init__(self, public_key_str: str = None, private_key_str: str = None, passphrase: str = None):
        self.public_key = None
        self.private_key = None
        self.passphrase = passphrase
        if public_key_str:
            self.public_key, _ = pgpy.PGPKey.from_blob(public_key_str)
        if private_key_str:
            self.private_key, _ = pgpy.PGPKey.from_blob(private_key_str)

    def encrypt(self, data: Union[str, bytes]) -> str:
        if not self.public_key:
            raise ValueError("Public key not loaded")
        msg = pgpy.PGPMessage.new(data if isinstance(data, str) else data.decode('utf-8'))
        encrypted = self.public_key.encrypt(msg)
        return str(encrypted)

    def decrypt(self, encrypted_data: str) -> str:
        if not self.private_key:
            raise ValueError("Private key not loaded")
        if self.private_key.is_protected and self.passphrase:
            with self.private_key.unlock(self.passphrase):
                msg = pgpy.PGPMessage.from_blob(encrypted_data)
                return self.private_key.decrypt(msg).message
        else:
            msg = pgpy.PGPMessage.from_blob(encrypted_data)
            return self.private_key.decrypt(msg).message

# Example usage:
# pgp = PGPManager(public_key_str=..., private_key_str=..., passphrase=...)
# encrypted = pgp.encrypt('my secret data')
# decrypted = pgp.decrypt(encrypted)
