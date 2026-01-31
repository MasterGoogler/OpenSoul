import unittest
from AuditLogger import AuditLogger

class TestAuditLogger(unittest.TestCase):
    def test_log_and_batch(self):
        logger = AuditLogger(priv_wif='L1aW4aubDFB7yfras2S1mMEWB5p1n1w5hQmQf5Qk4bG7xJ1m3v7C', config={"batch_mode": "memory"})
        logger.log({"tokens_in": 100, "tokens_out": 50, "action": "test"})
        self.assertEqual(len(logger.actions), 1)

    # More tests can be added for flush, file batching, etc. with mocks

if __name__ == '__main__':
    unittest.main()
