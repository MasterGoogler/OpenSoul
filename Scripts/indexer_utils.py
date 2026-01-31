"""
indexer_utils.py - On-chain data indexing/search utilities for OpenSoul agents

Provides functions to search and filter logs/data using indexer APIs (e.g., WhatsOnChain, MatterCloud).
"""

import requests

WOC_API = "https://api.whatsonchain.com/v1/bsv/main"

class IndexerUtils:
    @staticmethod
    def search_opreturn(address: str, query: str = None) -> list:
        url = f"{WOC_API}/address/{address}/txs"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Indexer search failed: {resp.text}")
        txs = resp.json()
        results = []
        for tx in txs:
            for vout in tx.get('vout', []):
                if vout.get('value', 0) == 0 and 'scriptPubKey' in vout:
                    script = vout['scriptPubKey'].get('hex', '')
                    if script.startswith('6a'):  # OP_RETURN
                        if not query or query in script:
                            results.append({
                                'txid': tx['txid'],
                                'op_return': script
                            })
        return results

# Example usage:
# logs = IndexerUtils.search_opreturn(agent_address, 'my-agent')
