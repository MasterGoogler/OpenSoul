import asyncio
import os

logger = AuditLogger(priv_wif=os.getenv("BSV_PRIV_WIF"), config={"mode": "session"})

# During agent session
logger.log({"tokens_in": 4500, "tokens_out": 3200, "action": "tool_call", "details": "web_search"})
logger.log({"tokens_in": 1200, "tokens_out": 800, "action": "response_gen"})

# At end of session
await logger.flush()

# On next startup
history = await logger.get_history()
print("Past sessions:", history)
