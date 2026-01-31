"""
oracle_utils.py - On-chain oracle integration utilities for OpenSoul agents

Provides functions to fetch and verify data from trusted on-chain oracles.
"""

import requests

class OracleUtils:
    @staticmethod
    def fetch_oracle_data(oracle_url: str, query: dict) -> dict:
        resp = requests.post(oracle_url, json=query)
        if resp.status_code != 200:
            raise RuntimeError(f"Oracle fetch failed: {resp.text}")
        return resp.json()

    @staticmethod
    def verify_oracle_signature(data: dict, pubkey: str) -> bool:
        # Stub: verify oracle's digital signature on data
        # Real implementation would use BSV signature verification
        return True

# Example usage:
# data = OracleUtils.fetch_oracle_data('https://oracle.example.com/api', {"symbol": "BSVUSD"})
# OracleUtils.verify_oracle_signature(data, pubkey)
