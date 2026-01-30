**Open Items & Future Enhancements**

- Auto load the OpenSoul for the model, when it opens a new context.

-Accurate dynamic fee calculation (tx.fee() after build).
-Cumulative totals (load history on flush, add running sums to payload).
-Threshold-based flushing (e.g., every 10k tokens).
-Payload compression (gzip + base64) for larger logs.
-Better UTXO filtering (ignore dust).
-Testnet support.
-Error handling & retries.
-Multi-agent support (multiple chains or tagged logs).
-Genesis funding script.

**Notes from discussion**

-Notes from Discussion:Start with one log per session; expand later.
-No mutable state—just append-only metrics.
-Use cache for efficiency, but always fall back to full chain trace.
-Fund the address with a tiny amount initially (e.g., 1000 sats) + genesis log


This document serves as a living system design guide. Clone, fork, and iterate!


