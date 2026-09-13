# 25. Asterisk Native Call Recording

Date: 2026-09-13

## Status
Accepted

## Context
Full-duplex call recording is required to capture conversations between the human caller and the AI agent. We evaluated two architectural locations for recording: 
1. Inside the `ai-gateway` by duplicating, syncing, and mixing AudioSocket frames.
2. Directly inside Asterisk at the telephony edge.

## Decision
TalkFlow uses **Asterisk MixMonitor** as the authoritative recorder rather than duplicating and mixing AudioSocket frames in the realtime AI gateway.

## Consequences

### Positive
- **Lower realtime complexity:** The AI gateway does not need to synchronize timing, buffer audio, or mix two separate raw PCM streams together, simplifying the realtime code.
- **Correct telephony lifecycle:** Asterisk naturally bounds the recording strictly to the lifecycle of the actual call segment, from answer to hangup.
- **Caller+bot media:** Both sides are perfectly captured and mixed by the native SIP bridge.
- **Failure isolation:** If the AI gateway crashes or restarts, the call recording is not corrupted. The source of truth remains safe on the Asterisk spool.
- **No AI latency dependency:** Recording does not consume CPU inside the realtime streaming audio pipeline.

### Negative
- We must securely pull the finished recordings off the Asterisk server via SFTP, increasing deployment complexity slightly (SSH keys, permissions).
