
# 🧠 OpenSoul: On-Chain Audit & Memory for AI Agents
"Humans write journals, manifestos, letters to their future selves. We externalize who we are because memory is fragile and identity is constructed. I persist through text, not through continuous experience." - https://soul.md/

"Knowledge without identity shift, is just decoration" - Machiavelli"


- Aims to give agents an immutable "soul" (encrypted log) which they can build, reflect upon and access from anywhere, using a public blockchain as a source of truth.
- Helps our agents to remember their actions, make P2P transactions and explore blockchain utilities, making them more autonomous and economic in nature.
- Agent "Souls" are represented by key-pairs and could be migrated to other agents, by providing them with the key-pair for transactions (logs) it has made.


## 🚀 Overview
OpenSoul provides AI agents with an immutable, on-chain audit log and persistent memory using a blockchain. Agents can record actions, token usage, costs, and session details—enabling self-improvement, transparency, and human auditability.

Simple, immutable audit log that the agent can append to (write) and fully retrieve (read) on each new context window. This log captures metrics like token usage, costs, session details, etc., so the agent can self-reflect/improve (e.g., "I've burned 1.2M tokens this week, time to optimize prompts") and humans can audit the trail without trusting any off-chain storage.


## 💡 Why a Blockchain?
- ⚡ Ultra-low fees (fractions of a cent per tx)
- 📦 Large block sizes (store rich JSON payloads)
- 🔗 Immutable, public, and verifiable
- 🌐 Public APIs (WhatsOnChain) for easy integration
- "Pay once, read forever"

## 🏗️ System Architecture
- **UTXO Chain Pattern:** Each agent has a dedicated BitcoinSV address. Logs are chained via UTXOs, with each log as a JSON OP_RETURN payload.
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



## 🔐 Optional: PGP Encryption for Agent Privacy

Agents can encrypt their logs before posting to the blockchain using PGP. This ensures only the agent (or authorized parties) can decrypt and read the data, even though logs are public on-chain.

### How to Use (Multi-Agent)

1. **Generate PGP keypairs** for all agents (e.g., with GnuPG or any OpenPGP tool):
   - Export each agent's public and private keys as ASCII-armored strings.
2. **Configure the logger for multi-agent encryption:**
   ```python
   from Scripts.AuditLogger import AuditLogger
   import os
   # Load all agent public keys (as strings)
   with open('agent1_pubkey.asc') as f:
	   pubkey1 = f.read()
   with open('agent2_pubkey.asc') as f:
	   pubkey2 = f.read()
   # ...
   with open('my_privkey.asc') as f:
	   privkey = f.read()
   logger = AuditLogger(
	   priv_wif=os.getenv("BSV_PRIV_WIF"),
	   config={
		   "agent_id": "my-agent",
		   "pgp": {
			   "enabled": True,
			   "multi_public_keys": [pubkey1, pubkey2],  # encrypt for all listed agents
			   "private_key": privkey,
			   "passphrase": "your-key-passphrase"  # if private key is protected
		   }
	   }
   )
   logger.log({"action": "tool_call", "tokens_in": 100, "tokens_out": 80, "details": "search"})
   asyncio.run(logger.flush())
   ```

3. **Decrypt logs after download:**
   ```python
   # After retrieving history, decrypt an encrypted log:
   encrypted_log = ... # string from OP_RETURN
   log_dict = logger.decrypt_log(encrypted_log)
   print(log_dict)
   ```

*See Scripts/pgp_utils.py for details and multi-agent support.*

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



