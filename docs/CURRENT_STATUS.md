# Current Status

**Current Phase:** Phase 11 (Call Recording) completed.

## Recently Completed
- Implemented `recording-worker` to asynchronously poll and pull completed call recordings from Asterisk via SFTP.
- Configured Asterisk `MixMonitor` to reliably record both legs of the live conversation natively.
- Created PostgreSQL `call_recordings` schema and migration to track file state, checksums, and lifecycle.
- Fully decoupled real-time live streaming audio from the recording process, isolating edge node latency and potential failures.
- Added cryptographic validation (SHA-256) of incoming recordings to guarantee file integrity.
- Handled SFTP security with strict `read-only` constraints for the `talkflow_recordings` user to ensure no worker can corrupt Asterisk's disk.
- (Phase 10) Implemented `SpeechNormalizer` to dynamically convert business text (like ZIP codes, phone numbers, currencies, and generic numbers) into strict spoken formats for TTS consumption.
- (Phase 10) Configured a purely memory-resident `PronunciationLexicon` for loading explicit domain pronunciations at startup safely out-of-code.

## Known Constraints
- **Dynamic TTS Missing:** The dynamic TTS worker is not currently running in the local Docker environment, so LLM responses fallback to the dummy TTS provider temporarily to avoid timeouts. The architecture fully supports streaming to a real dynamic endpoint when available.
- **Recording Outbox:** If Kafka restarts or an event drops right after a call ends, the recording is safe on Asterisk, but an outbox/reconciliation cron is needed eventually to sync these orphaned recordings into the database.

## Next Active Phase
- Transitioning into Phase 12 (PostgreSQL Data Model) and Phase 13 (Telephony Edge Resiliency) focusing on enhancing jitter buffers and connection resilience to gracefully handle degraded AudioSocket PBX links.
