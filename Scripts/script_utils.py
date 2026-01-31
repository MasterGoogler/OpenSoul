"""
script_utils.py - BSV script/smart contract utilities for OpenSoul agents

Provides templates and helpers for custom scripts (e.g., time locks, conditional payments).
"""

from bsv import Script, Opcode

class ScriptUtils:
    @staticmethod
    def create_timelock_script(pubkey: str, locktime: int) -> Script:
        # Example: P2PKH with CLTV (CheckLockTimeVerify)
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
        # Example: If/Else script
        script = Script()
        script.add(Opcode.OP_IF)
        script.push_data(bytes.fromhex(pubkey1))
        script.add(Opcode.OP_CHECKSIG)
        script.add(Opcode.OP_ELSE)
        script.push_data(bytes.fromhex(pubkey2))
        script.add(Opcode.OP_CHECKSIG)
        script.add(Opcode.OP_ENDIF)
        return script

# Example usage:
# timelock_script = ScriptUtils.create_timelock_script(pubkey, 1700000000)
# cond_script = ScriptUtils.create_conditional_script(pub1, pub2)
