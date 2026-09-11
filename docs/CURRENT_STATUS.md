# Current Status

**Current Phase:** Phase 10 (Speech Normalization) completed.

## Recently Completed
- Implemented `SpeechNormalizer` to dynamically convert business text (like ZIP codes, phone numbers, currencies, and generic numbers) into strict spoken formats for TTS consumption.
- Introduced strict separation between canonical `display_text` and spoken `tts_text` to protect LLM context windows and logs.
- Configured a purely memory-resident `PronunciationLexicon` for loading explicit domain pronunciations at startup (e.g., "Medicare Part A") safely out-of-code.
- Maintained complete decoupling from the `TurnController` so normalization functions as a stateless transform layer that respects Phase 9's parallel barge-in cancellation.
- Built a robust, fast regression QA corpus testing suite.
- (Phase 9) Transitioned the LLM response pipeline to a full streaming architecture using server-sent events (SSE).
- (Phase 9) Integrated generation invalidation to prevent stale text chunks from being spoken post-interruption.

## Known Constraints
- **Dynamic TTS Missing:** The dynamic TTS worker is not currently running in the local Docker environment, so LLM responses fallback to the dummy TTS provider temporarily to avoid timeouts. The architecture fully supports streaming to a real dynamic endpoint when available.

## Next Active Phase
- Transitioning into Phase 11, focusing on Telephony Edge Resiliency (enhancing jitter buffers and connection resilience to gracefully handle degraded AudioSocket PBX links) and Multi-tenant Scaling.
