import unittest
from wallet import Wallet

class TestWallet(unittest.TestCase):
    def test_generate_keypair(self):
        kp = Wallet.generate_keypair()
        self.assertIn('wif', kp)
        self.assertIn('address', kp)
        self.assertTrue(kp['wif'].startswith('L') or kp['wif'].startswith('K'))
        self.assertTrue(kp['address'].startswith('1') or kp['address'].startswith('3'))

    def test_wif_to_address(self):
        kp = Wallet.generate_keypair()
        addr = Wallet.wif_to_address(kp['wif'])
        self.assertEqual(addr, kp['address'])

    # More tests can be added for balance, tx history, etc. with mocks

if __name__ == '__main__':
    unittest.main()
