"""
pgp_utils.py - PGP encryption/decryption utilities for OpenSoul agents

This module provides functions to encrypt data with a PGP public key and decrypt with a private key.
Uses the 'pgpy' library for OpenPGP operations.
"""

import pgpy
from typing import Union


class PGPManager:
    def __init__(self, public_key_str: str = None, private_key_str: str = None, passphrase: str = None, multi_public_keys: list = None):
        self.public_key = None
        self.private_key = None
        self.passphrase = passphrase
        self.multi_public_keys = []
        if public_key_str:
            self.public_key, _ = pgpy.PGPKey.from_blob(public_key_str)
        if private_key_str:
            self.private_key, _ = pgpy.PGPKey.from_blob(private_key_str)
        if multi_public_keys:
            for key_str in multi_public_keys:
                key, _ = pgpy.PGPKey.from_blob(key_str)
                self.multi_public_keys.append(key)

    def encrypt(self, data: Union[str, bytes], recipients: list = None) -> str:
        """
        Encrypt data for one or more recipients. If recipients is provided, it should be a list of PGPKey objects or ASCII-armored public key strings.
        If not provided, uses self.public_key or self.multi_public_keys.
        """
        msg = pgpy.PGPMessage.new(data if isinstance(data, str) else data.decode('utf-8'))
        keys = []
        if recipients:
            for k in recipients:
                if isinstance(k, str):
                    key, _ = pgpy.PGPKey.from_blob(k)
                    keys.append(key)
                else:
                    keys.append(k)
        elif self.multi_public_keys:
            keys = self.multi_public_keys
        elif self.public_key:
            keys = [self.public_key]
        else:
            raise ValueError("No public key(s) loaded for encryption")
        encrypted = msg
        for key in keys:
            encrypted = key.encrypt(encrypted)
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
