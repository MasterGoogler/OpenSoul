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

## 2. Configuration (Multi-Agent)

Pass all agent public keys to the logger via the config dict for multi-recipient encryption:

```python
from Scripts.AuditLogger import AuditLogger
import os
# Load all agent public keys (as strings)
with open('agent1_pubkey.asc') as f:
    pubkey1 = f.read()
with open('agent2_pubkey.asc') as f:
    pubkey2 = f.read()
# ...
with open('my_privkey.asc') as f:
    privkey = f.read()
logger = AuditLogger(
    priv_wif=os.getenv("BSV_PRIV_WIF"),
    config={
        "agent_id": "my-agent",
        "pgp": {
            "enabled": True,
            "multi_public_keys": [pubkey1, pubkey2],  # encrypt for all listed agents
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
