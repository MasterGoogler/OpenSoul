a toolkit to help our agents remember their actions, using a blockchain as a source of truth.

Just a simple, immutable audit log that the agent can append to (write) and fully retrieve (read) on each new context window. This log captures metrics like token usage, costs, session details, etc., so the agent can self-reflect/improve (e.g., "I've burned 1.2M tokens this week, time to optimize prompts") and humans can audit the trail without trusting any off-chain storage.




# 🧠 OpenSoul: On-Chain Audit & Memory for AI Agents

## 🚀 Overview
OpenSoul provides AI agents with an immutable, on-chain audit log and persistent memory using Bitcoin SV (BSV). Agents can record actions, token usage, costs, and session details—enabling self-improvement, transparency, and human auditability.

## 💡 Why BSV?
- ⚡ Ultra-low fees (fractions of a cent per tx)
- 📦 Large block sizes (store rich JSON payloads)
- 🔗 Immutable, public, and verifiable
- 🌐 Public APIs (WhatsOnChain) for easy integration

## 🏗️ System Architecture
- **UTXO Chain Pattern:** Each agent has a dedicated BSV address. Logs are chained via UTXOs, with each log as a JSON OP_RETURN payload.
- **Session-Based Batching:** Logs are batched in memory or file, then flushed to chain at session end or threshold.
- **Human & Machine Readable:** All logs are public, verifiable, and easy to parse.

## 📝 Example Log Structure
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
	 }
  ],
  "total_tokens_in": 500,
  "total_tokens_out": 300,
  "total_cost_bsv": 0.00001,
  "total_actions": 1
}
```
*See `Documentation/suggestions.md` for full schema and rationale.*

## 🛠️ Quickstart

1. **Install dependencies**
	```sh
	python Scripts/install_prereqs.py
	```

2. **Set your private key**
	- Export your BSV WIF as `BSV_PRIV_WIF` or pass directly to the logger.

3. **Log actions in your agent**
	```python
	from Scripts.AuditLogger import AuditLogger
	import os, asyncio

	logger = AuditLogger(priv_wif=os.getenv("BSV_PRIV_WIF"), config={"agent_id": "my-agent"})
	logger.log({"action": "tool_call", "tokens_in": 100, "tokens_out": 80, "details": "search"})
	asyncio.run(logger.flush())
	```

4. **Read audit history**
	```python
	history = asyncio.run(logger.get_history())
	print(history)
	```

## 📚 Documentation

- **System Design:** [Documentation/SystemDesign.md](Documentation/SystemDesign.md)
- **Future Ideas & Roadmap:** [Documentation/Future.md](Documentation/Future.md)
- **Build Guide:** [Documentation/build guide.md](Documentation/build%20guide.md)
- **Testing Plan:** [Documentation/testing.md](Documentation/testing.md)
- **Advanced Suggestions:** [Documentation/suggestions.md](Documentation/suggestions.md)

## 🔮 Future Directions
- 🤝 Agent-to-agent payments & collaboration
- 🏅 Reputation & trust layers
- 🧩 Open knowledge graph on-chain
- 💸 Economic incentives for AI
- 🛡️ Model & prompt provenance

*See `Documentation/Future.md` for more!*



