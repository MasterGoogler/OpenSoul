# Testing Plan for AuditLogger

## Unit Tests
- Test `log`, `flush`, and `get_history` methods (mock network calls).
- Test both memory and file batch modes for correct batching and persistence.

## Integration Tests
- Test with real BSV funds on testnet (after making API_BASE configurable).
- Simulate crash recovery: write logs, kill process, restart, and call `flush` to ensure logs are not lost.

## Manual/Scenario Tests
- Test error handling for missing UTXO, insufficient funds, and oversized payloads.
- Test multi-agent scenarios (different agent_ids, concurrent sessions).
- Test edge cases: empty logs, corrupted batch file, network failures.
