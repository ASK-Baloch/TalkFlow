# TalkFlow

TalkFlow is a real-time conversational AI system designed to interface directly with telephony endpoints (e.g., Asterisk) over the AudioSocket protocol.

## Project Context
The system is being built in phases to ensure strict separation of concerns, high performance, and robust fault tolerance.

**Current State**: Phase 11 (Call Recording) has been successfully completed. 
The system now fully supports:
- Streaming ASR (Faster-Whisper)
- Voice Activity Detection (Silero VAD)
- Real-time TTS (Chatterbox Generative TTS and Kokoro-based Pre-generated TTS)
- Streaming Orchestration with LLM Fallbacks (Qwen via vLLM)
- Barge-in and Interruption Handling
- Speech Normalization (Display vs. Spoken Text)
- Secure, async Native Call Recording via Asterisk MixMonitor

**Next Phase**: Phase 12 (Telephony Edge Resiliency)

*For more details, please see the `docs/` directory.*
