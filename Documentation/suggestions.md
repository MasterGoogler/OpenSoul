# Suggestions for AuditLogger and OpenSoul

1. **Keypair/Wallet Management**
   - Add static methods to generate new BSV keypairs and return WIF/address for agent autonomy.
2. **Fee Calculation**
   - Replace hardcoded fee (300 sats) with SDK’s fee estimation after transaction build for accuracy.
3. **Payload Compression**
   - Implement optional payload compression (gzip + base64) for larger logs.
4. **Testnet Support**
   - Make API_BASE configurable to allow easy switching between mainnet and testnet.
5. **Multi-Agent Support**
   - Allow agent_id to be passed/configured per agent, not hardcoded.
6. **Exception Handling**
   - Add more granular logging and error handling for network and file operations.
7. **Concurrency**
   - For file-based batching, consider file locks or other mechanisms to prevent race conditions in multi-threaded contexts.

---

## Suggested Audit Log JSON Structure

Each log entry (written to BSV) should follow this structure:

```json
{
  "agent_id": "my-agent-123",
  "session_id": "uuid-abc-123",
  "session_start": "2026-01-31T01:00:00Z",
  "session_end": "2026-01-31T01:30:00Z",
  "metrics": [
    {
      "ts": "2026-01-31T01:01:00Z",
      "action": "tool_call",
      "tokens_in": 500,
      "tokens_out": 300,
      "details": {"tool": "web_search", "query": "BSV fee policy"},
      "status": "success"
    },
    {
      "ts": "2026-01-31T01:05:00Z",
      "action": "payment",
      "cost_bsv": 0.00001,
      "peer_agent": "other-agent-456",
      "txid": "bsvtxid...",
      "status": "success"
    }
  ],
  "total_tokens_in": 500,
  "total_tokens_out": 300,
  "total_cost_bsv": 0.00001,
  "total_actions": 2
}
```

- Add or remove fields as needed for your agent's domain.
- This structure supports extensibility, analytics, and auditability.
- All timestamps should be ISO8601 UTC.
- Use the `details` field for action-specific or free-form data.
