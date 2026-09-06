# TalkFlow Roadmap

## Completed Phases
- **Phase 1:** AudioSocket Echo loop and foundational IO.
- **Phase 2:** Voice Activity Detection (VAD) via Silero integration.
- **Phase 3:** Streaming ASR via Faster-Whisper.
- **Phase 4:** Qualification Engine (Extracting fields, deterministic state machine).
- **Phase 5:** Pre-generated TTS Integration (Playback caching and pacing).
- **Phase 6:** Provider Streaming TTS (Model isolation, dynamic Chatterbox generation).

## Upcoming Phases

### Phase 7: Interruption and Barge-In
- Implementing caller barge-in handling to gracefully halt AudioSocket TTS playback when VAD detects the user interrupting.
- Clearing out-of-date TTS queues and handling state resets without dropping the AudioSocket connection.

### Phase 8: Conversational LLM (Qwen Integration)
- Introducing the Qwen LLM for dynamic dialogue generation, replacing deterministic rule-based qualification scripts with natural, context-aware back-and-forth.
- Chunked generation passing partial sentences into the TTS engine to drop TTFA significantly.

### Phase 9: Telephony Edge Resiliency
- Enhancing jitter buffers and connection resilience to gracefully handle degraded AudioSocket PBX links.

### Phase 10: Multi-tenant Scaling
- Expanding the backend to handle large concurrency across multiple concurrent remote AudioSockets, sharding model workers and caching components.
