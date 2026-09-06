# Current Status

**Current Phase:** Phase 6 (Provider Streaming TTS) completed.

## Recently Completed
- Established Provider-based Dependency Injection for TTS and STT (`TTSProvider`, `STTProvider`), removing tight coupling to ML SDKs inside the AI Gateway.
- Integrated the standalone Chatterbox TTS Worker running as an isolated HTTP microservice.
- Benchmarked generative TTS latency (Time-To-First-Audio), finding that short conversational bursts (3-8 words) significantly improve response latency (2s - 3s RTF limits).
- Successfully completed live end-to-end integration testing over the local SSH tunnel to the Asterisk PBX.
- The pipeline correctly handles live caller audio via AudioSocket -> VAD -> STT -> Qualification -> TTS (Pregenerated + Dynamic).

## Known Constraints
- **TTS Generation Blocks:** Because the current Chatterbox HTTP provider generates audio as a monolithic block, TTFA is roughly equal to total synthesis time. Sentence chunking and incremental generation (Phase 8/Qwen integration) will be needed to truly achieve sub-second TTFA for long sentences.
- **Interruption:** Barge-in functionality (interrupting a playing TTS prompt with new speech) is currently disabled (`TTS_INTERRUPT_ENABLED=false`).

## Next Active Phase
- Transitioning into Phase 7, focusing on interruption / barge-in mechanics, allowing the AI to immediately halt its TTS pacing output when the caller interrupts.
