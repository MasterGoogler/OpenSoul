# PGP Encryption for OpenSoul Agents

This document explains how to use PGP encryption with the OpenSoul audit logger, including key generation, configuration, and usage patterns.

## 1. Key Generation

Generate a PGP keypair using GnuPG or any OpenPGP-compatible tool:

```sh
gpg --full-generate-key
# Export public key
gpg --armor --export <your-email> > my_pubkey.asc
# Export private key
gpg --armor --export-secret-keys <your-email> > my_privkey.asc
```

## 2. Configuration

Pass your PGP keys to the logger via the config dict:

```python
from Scripts.AuditLogger import AuditLogger
import os
with open('my_pubkey.asc') as f:
    pubkey = f.read()
with open('my_privkey.asc') as f:
    privkey = f.read()
logger = AuditLogger(
    priv_wif=os.getenv("BSV_PRIV_WIF"),
    config={
        "agent_id": "my-agent",
        "pgp": {
            "enabled": True,
            "public_key": pubkey,
            "private_key": privkey,
            "passphrase": "your-key-passphrase"  # if needed
        }
    }
)
```

## 3. Encrypting Logs

When PGP is enabled, logs are encrypted before being posted on-chain. Only the agent with the private key can decrypt them.

## 4. Decrypting Logs

After retrieving logs, decrypt with:

```python
encrypted_log = ... # string from OP_RETURN
log_dict = logger.decrypt_log(encrypted_log)
print(log_dict)
```

## 5. Security Notes
- Never share your private key or passphrase.
- All logs are still public on-chain, but only decryptable by the key holder.
- For multi-agent scenarios, use a shared public key or encrypt for multiple recipients.

## 6. See Also
- Scripts/pgp_utils.py for implementation details.
- README.md for integration example.
