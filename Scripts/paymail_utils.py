"""
paymail_utils.py - Paymail integration utilities for OpenSoul agents

Provides functions for Paymail address resolution and peer-to-peer messaging.
"""

import requests

class PaymailUtils:
    @staticmethod
    def resolve_paymail(paymail: str) -> str:
        # Use Paymail Discovery protocol
        user, domain = paymail.split('@')
        url = f"https://{domain}/.well-known/bsvalias/id/{user}@{domain}"
        resp = requests.get(url)
        if resp.status_code != 200:
            raise RuntimeError(f"Paymail resolution failed: {resp.text}")
        return resp.json().get('address')

    @staticmethod
    def send_message(paymail: str, message: str) -> bool:
        # Stub: send a message to a Paymail address (requires compatible server)
        # Real implementation would use Paymail P2P or peer channels
        return True

# Example usage:
# address = PaymailUtils.resolve_paymail('alice@moneybutton.com')
# PaymailUtils.send_message('bob@handcash.io', 'Hello!')
