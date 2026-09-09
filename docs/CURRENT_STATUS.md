# Current Status

**Current Phase:** Phase 8 (Qwen LLM Fallback) completed.

## Recently Completed
- Implemented and verified the `LLMProvider` abstraction (`OpenAICompatibleLLMProvider` and `DummyLLMProvider`).
- Integrated Qwen3-8B-AWQ (deployed as Qwen2.5-1.5B-AWQ for 4GB VRAM constraint) via vLLM for handling conversational fallback generation.
- Designed smart heuristic fallback triggers so the LLM is only queried for complex out-of-domain questions while maintaining the sub-second latency fast-path for simple invalid inputs.
- Successfully benchmarked the vLLM integration, establishing baseline metrics for Time-To-First-Token (~300ms) without breaking the strict architecture rules.
- Implemented barge-in and conversational interruption mechanics (Phase 7), enabling the AI to instantly halt TTS playback when the caller interrupts.

## Known Constraints
- **TTS Generation Blocks:** Because the current Chatterbox HTTP provider generates audio as a monolithic block, TTFA is roughly equal to total synthesis time. Sentence chunking and incremental generation (Phase 9) will be needed to truly achieve sub-second TTFA for dynamic LLM responses.
- **Dynamic TTS Missing:** The dynamic TTS worker is not currently running in the local Docker environment, so LLM responses fallback to the dummy TTS provider temporarily to avoid timeouts.

## Next Active Phase
- Transitioning into Phase 9, focusing on response streaming, TTS chunking, and intelligent conversational planning to pipeline LLM output directly into incremental TTS generation.
