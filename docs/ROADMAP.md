# TalkFlow Roadmap

## Completed Phases
- **Phase 1:** AudioSocket Echo loop and foundational IO.
- **Phase 2:** Voice Activity Detection (VAD) via Silero integration.
- **Phase 3:** Streaming ASR via Faster-Whisper.
- **Phase 4:** Qualification Engine (Extracting fields, deterministic state machine).
- **Phase 5:** Pre-generated TTS Integration (Playback caching and pacing).
- **Phase 6:** Provider Streaming TTS (Model isolation, dynamic Chatterbox generation).
- **Phase 7:** Interruption and Barge-In (Halt TTS playback on user interruption, clear queues).
- **Phase 8:** Qwen LLM Fallback (vLLM integration for handling out-of-domain complex questions via OpenAI-compatible provider).
- **Phase 9:** Streaming Response Orchestration (Chunked SSE generation passing partial sentences into the TTS engine to drop TTFA significantly, plus independent barge-in cancellation).
- **Phase 10:** Speech Normalization (Separating `display_text` vs `tts_text`, expanding ZIPs/phones, and applying JSON pronunciation lexicons synchronously before TTS).

## Upcoming Phases

### Phase 11: Telephony Edge Resiliency
- Enhancing jitter buffers and connection resilience to gracefully handle degraded AudioSocket PBX links.

### Phase 12: Multi-tenant Scaling
- Expanding the backend to handle large concurrency across multiple concurrent remote AudioSockets, sharding model workers and caching components.
