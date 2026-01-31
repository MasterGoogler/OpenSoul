"""
p2wdb_utils.py - Pay-to-Write Database (P2WDB) utilities for OpenSoul agents

Provides functions to store and retrieve files/data using a P2WDB HTTP API.
"""

import requests
import json

P2WDB_WRITE_API = "https://p2wdb.com/api/v1/entry/write"
P2WDB_READ_API = "https://p2wdb.com/api/v1/entry/"

class P2WDB:
    @staticmethod
    def write_file(file_bytes: bytes, metadata: dict = None) -> str:
        """
        Store a file in P2WDB. Returns the file hash/URI.
        """
        files = {'file': file_bytes}
        data = metadata or {}
        try:
            resp = requests.post(P2WDB_WRITE_API, files=files, data=data)
            resp.raise_for_status()
            result = resp.json()
            return result.get('hash') or result.get('data', {}).get('hash')
        except Exception as e:
            raise RuntimeError(f"P2WDB write failed: {e}")

    @staticmethod
    def read_file(file_hash: str) -> bytes:
        """
        Retrieve a file from P2WDB by hash.
        """
        try:
            resp = requests.get(P2WDB_READ_API + file_hash)
            resp.raise_for_status()
            # Try to parse as JSON, fallback to raw bytes
            try:
                data = resp.json()
                if 'data' in data and 'file' in data['data']:
                    return data['data']['file'].encode('utf-8')
            except Exception:
                pass
            return resp.content
        except Exception as e:
            raise RuntimeError(f"P2WDB read failed: {e}")

    @staticmethod
    def write_json(obj: dict, metadata: dict = None) -> str:
        """
        Store a JSON object in P2WDB. Returns the file hash/URI.
        """
        file_bytes = json.dumps(obj).encode('utf-8')
        return P2WDB.write_file(file_bytes, metadata)

    @staticmethod
    def read_json(file_hash: str) -> dict:
        """
        Retrieve a JSON object from P2WDB by hash.
        """
        file_bytes = P2WDB.read_file(file_hash)
        return json.loads(file_bytes.decode('utf-8'))

# Example usage:
# file_hash = P2WDB.write_file(b'my file data', {"agent_id": "my-agent"})
# file_bytes = P2WDB.read_file(file_hash)
# json_hash = P2WDB.write_json({"foo": "bar"})
# obj = P2WDB.read_json(json_hash)
