# Security and Data Privacy

## ML Network Isolation
- All machine learning components (Chatterbox TTS worker, vLLM inference server) run in independent Docker containers connected to a private bridge network.
- The AI Gateway connects to these workers internally. None of the ML worker ports are exposed publicly.

## Generative Fallback Security (Phase 8)
- **Constrained Execution**: The LLM used for conversational fallback (Qwen) does not possess tools, function calling capabilities, or access to backend systems. It strictly outputs text.
- **State Machine Authority**: The LLM cannot update the caller's qualification state or modify field data. The deterministic qualification engine retains absolute authority.
- **Prompt Injection Defense**: System prompts explicitly enforce boundaries, instructing the model to remain in character and refuse inappropriate queries.
- **Information Sanitization**: The conversation history provided to the LLM is restricted to the last N turns.

## Audio Processing
- Caller audio is processed temporarily in memory for Voice Activity Detection and Streaming ASR. Raw audio files are not persisted to disk in production.
- Telephony connectivity occurs via the AudioSocket protocol over private infrastructure or secure SSH tunnels.
