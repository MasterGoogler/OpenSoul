# 🧪 Testing Plan

## ✅ Unit Tests
- Test `log`, `flush`, and `get_history` (mock network)
- Test memory and file batch modes

## 🔗 Integration Tests
- Test with real BSV funds on testnet
- Simulate crash recovery

## 🧩 Manual/Scenario Tests
- Error handling (missing UTXO, insufficient funds, oversized payloads)
- Multi-agent scenarios
- Edge cases (empty logs, corrupted batch file, network failures)
