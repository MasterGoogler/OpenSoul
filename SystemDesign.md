# BSV On-Chain Audit Log System for AI Agents

**Project Goal**  
Create a cheap, immutable, on-chain audit log on Bitcoin SV (BSV) that AI agents can use to persistently record actions, token usage, costs, and other metrics. This log survives context window resets, allowing agents to "remember" past sessions for self-improvement and enabling human auditing.

**Date of Discussion**: January 2026  
**Core Idea**: Use a UTXO-linked chain of transactions with OP_RETURN data to store JSON logs. Each log entry spends the previous change UTXO, adds an OP_RETURN payload, and returns change to the same address. This creates an append-only, discoverable chain.

**Why BSV?**  
- Extremely low fees (fractions of a cent per tx even in 2026).  
- Large block sizes → cheap storage of JSON payloads (up to several KB per tx).  
- Immutable, public, verifiable trail.  
- Public APIs (e.g., WhatsOnChain) for querying UTXOs and tx data.

## System Design Overview

### Core Mechanism: UTXO Chain Pattern
1. **Agent Address**: One dedicated BSV address per agent (controlled by a private key).  

2. **Logging**:
   - Batch metrics/actions into a JSON payload.
   - Spend current UTXO (previous change output).
   - Add OP_RETURN output with JSON data.
   - Send change back to same address.
    
3. **Reading**:
   - Query unspent UTXOs for address → start from latest.
   - Trace backwards via input prevout → extract each OP_RETURN → collect logs.
   - Reverse for chronological order.
    
4. **Configurability**:
   - At least one log per context session.
   - Optional: flush mid-session on thresholds (e.g., token count, action count).
    
5. **Data Format** (example JSON in OP_RETURN):
   ```json
   {
     "agent_id": "my-agent-123",
     "session_start": "2026-01-30T12:00:00Z",
     "timestamp": "2026-01-30T12:05:00Z",
     "metrics": [
       {"ts": "2026-01-30T12:01:00Z", "tokens_in": 4500, "tokens_out": 3200, "action": "tool_call", "details": "web_search"},
       ...
     ]
   }

6. **Advantages**
- Immutable audit trail (on-chain forever).
- No external indexer needed beyond public APIs.
- Agent can compute running totals (e.g., cumulative tokens) by summing history.
- Human-readable via explorers (WhatsOnChain shows OP_RETURN data).

7. **Tools & Dependencies (2026 Context)**
- Library: bsv-sdk (pip install bsv-sdk; v1.0.10+)
- API: WhatsOnChain (https://api.whatsonchain.com/v1/bsv/main)
    - Endpoints: /address/{addr}/unspent, /tx/{txid}, /tx/{txid}/hex, /tx/raw (broadcast)
- Local Cache: JSON file for last txid/UTXO to avoid full scans on every write.
- Security: Private key via env var or secrets manager.



8. 

9. asdf
10. asdf
11. asdfa
12. asdf

   
   

