"""
merkle_utils.py - Merkle proof utilities for OpenSoul agents

Provides functions to build and verify Merkle proofs for data/log inclusion.
"""

import hashlib
from typing import List

def sha256d(data: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


class MerkleUtils:
    @staticmethod
    def build_merkle_root(leaves: List[bytes]) -> bytes:
        """
        Build a Merkle root from a list of leaves (bytes).
        """
        if not leaves:
            raise ValueError("No leaves provided")
        nodes = leaves[:]
        while len(nodes) > 1:
            if len(nodes) % 2 == 1:
                nodes.append(nodes[-1])
            nodes = [sha256d(nodes[i] + nodes[i+1]) for i in range(0, len(nodes), 2)]
        return nodes[0]

    @staticmethod
    def build_merkle_proof(leaves: List[bytes], index: int) -> List[bytes]:
        """
        Build a Merkle proof for the leaf at the given index.
        Returns a list of sibling hashes (bytes).
        """
        if not (0 <= index < len(leaves)):
            raise IndexError("Index out of range for leaves")
        proof = []
        nodes = leaves[:]
        idx = index
        while len(nodes) > 1:
            if len(nodes) % 2 == 1:
                nodes.append(nodes[-1])
            next_nodes = []
            for i in range(0, len(nodes), 2):
                pair = (nodes[i], nodes[i+1])
                if i == idx or i+1 == idx:
                    sibling = pair[1] if i == idx else pair[0]
                    proof.append(sibling)
                    idx = len(next_nodes)
                next_nodes.append(sha256d(pair[0] + pair[1]))
            nodes = next_nodes
        return proof

    @staticmethod
    def verify_merkle_proof(leaf: bytes, proof: List[bytes], root: bytes, index: int) -> bool:
        """
        Verify a Merkle proof for a given leaf and root.
        Returns True if valid, False otherwise.
        """
        computed = leaf
        idx = index
        for sibling in proof:
            if idx % 2 == 0:
                computed = sha256d(computed + sibling)
            else:
                computed = sha256d(sibling + computed)
            idx //= 2
        return computed == root

    @staticmethod
    def build_merkle_root_hex(leaves_hex: List[str]) -> str:
        """
        Build a Merkle root from a list of hex-encoded leaves. Returns hex string.
        """
        leaves = [bytes.fromhex(h) for h in leaves_hex]
        return MerkleUtils.build_merkle_root(leaves).hex()

    @staticmethod
    def build_merkle_proof_hex(leaves_hex: List[str], index: int) -> List[str]:
        """
        Build a Merkle proof for hex-encoded leaves. Returns list of hex strings.
        """
        leaves = [bytes.fromhex(h) for h in leaves_hex]
        proof = MerkleUtils.build_merkle_proof(leaves, index)
        return [p.hex() for p in proof]

    @staticmethod
    def verify_merkle_proof_hex(leaf_hex: str, proof_hex: List[str], root_hex: str, index: int) -> bool:
        """
        Verify a Merkle proof for hex-encoded leaf/proof/root. Returns True if valid.
        """
        leaf = bytes.fromhex(leaf_hex)
        proof = [bytes.fromhex(h) for h in proof_hex]
        root = bytes.fromhex(root_hex)
        return MerkleUtils.verify_merkle_proof(leaf, proof, root, index)

# Example usage:
# root = MerkleUtils.build_merkle_root([b'a', b'b', b'c'])
# proof = MerkleUtils.build_merkle_proof([b'a', b'b', b'c'], 1)
# MerkleUtils.verify_merkle_proof(b'b', proof, root, 1)
