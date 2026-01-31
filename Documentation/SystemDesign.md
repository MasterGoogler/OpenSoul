# 🏗️ System Design: OpenSoul On-Chain Audit

## 🎯 Project Goal
Create a cheap, immutable, on-chain audit log on Bitcoin SV (BSV) for AI agents to persistently record actions, token usage, costs, and session metrics. Survives context resets, enables agent self-improvement, and supports human auditing.

## 🧩 Architecture Overview
- **UTXO Chain Pattern:** Each agent has a dedicated BSV address. Logs are chained via UTXOs, with each log as a JSON OP_RETURN payload.
- **Session-Based Batching:** Logs are batched and flushed to chain at session end or threshold.
- **Public, Verifiable, and Human-Readable:** All logs are public and can be verified via explorers or APIs.

## 🔗 Why BSV?
- ⚡ Ultra-low fees
- 📦 Large block sizes (store rich JSON)
- 🔗 Immutable, public, and verifiable
- 🌐 Public APIs (WhatsOnChain)

## 📝 Example Log Format
```json
{
   "agent_id": "my-agent-123",
   "session_start": "2026-01-30T12:00:00Z",
   "timestamp": "2026-01-30T12:05:00Z",
   "metrics": [
      {"ts": "2026-01-30T12:01:00Z", "tokens_in": 4500, "tokens_out": 3200, "action": "tool_call", "details": "web_search"}
   ]
}
```
*See `suggestions.md` for a more advanced schema.*

## 🛠️ Tools & Dependencies
- `bsv-sdk` (pip install bsv-sdk)
- `requests`
- WhatsOnChain API
5. **Data Format** (example JSON in OP_RETURN):

   ```json

   {

     "agent_id": "my-agent-123",

