# OpenAudit
a toolkit to help our agents remember their actions, using a blockchain as a source of truth.

Just a simple, immutable audit log that the agent can append to (write) and fully retrieve (read) on each new context window. This log captures metrics like token usage, costs, session details, etc., so the agent can self-reflect/improve (e.g., "I've burned 1.2M tokens this week, time to optimize prompts") and humans can audit the trail without trusting any off-chain storage.



