# Phase 8: Qwen LLM Fallback

## Goal
Implement a dynamic LLM fallback mechanism to gracefully handle out-of-domain questions and complex clarifications during the voice interaction, without degrading the sub-second latency of the primary conversational flow.

## 1. Qwen3-8B-AWQ Decision
We selected `Qwen/Qwen3-8B-AWQ` (deployed optimally as `Qwen/Qwen2.5-1.5B-Instruct-AWQ` under constrained GPU memory like 4GB VRAM) for our fallback model. It provides excellent conversational reasoning, rapid generation speeds, and its AWQ quantization enables low-latency inference on consumer-grade GPUs.

## 2. vLLM Architecture
The LLM is served via `vLLM` running in an isolated Docker container (`talkflow-vllm`). It exposes an OpenAI-compatible API on port 8100. This isolation ensures that heavy GPU inference does not block the real-time asyncio event loop of the `ai-gateway`.

## 3. Non-thinking Mode
To maintain strict latency constraints (TTFT < 500ms), the model operates in standard instruction mode. "Thinking" or Chain-of-Thought (CoT) behaviors are strictly disabled. The prompt instructs the model to immediately generate short, conversational responses.

## 4. Provider Interface
The gateway integrates with the LLM via an abstract `LLMProvider` interface. 
- `OpenAICompatibleLLMProvider`: Connects to vLLM.
- `DummyLLMProvider`: Returns fixed dummy responses for testing and baseline benchmarking without invoking GPU inference.
The provider can be hot-swapped via `LLM_PROVIDER_CLASS` environment variable, preserving the core business logic.

## 5. Qualification Boundary
The LLM does **not** have authority over the conversation state machine. It cannot update fields (e.g., age, name, Medicare status) or transition the qualification status. It acts purely as a linguistic fallback to answer a specific question, after which control immediately returns to the deterministic state machine.

## 6. Fallback Triggers
The LLM is triggered exclusively when the deterministic engine issues a clarification request **AND** a heuristic determines the caller's utterance is complex enough to warrant it (e.g., it contains question words like "what", "why", "how", "explain", or is longer than 3 words). Simple invalid answers (like "um") bypass the LLM and instantly trigger pre-generated clarification TTS.

## 7. History Limits
To prevent context window explosion and maintain low TTFT, only the last `N` turns (configurable via `LLM_MAX_HISTORY_TURNS`, default: 4) of conversation history are sent in the prompt. User inputs are truncated to `LLM_MAX_INPUT_CHARS` (default: 2000).

## 8. Latency Measurements
Baseline metrics measured via `benchmark_llm.py` established that the LLM pathway introduces latency:
- **TTFT (Time-To-First-Token)**: ~300ms
- **Total Generation Time**: ~350ms (for short responses)
Because this pathway uses Dynamic TTS (Phase 9), total round-trip latency will be higher than the pre-generated fast path.

## 9. Failure Fallback
If the LLM is disabled, times out (`LLM_TIMEOUT_SECONDS`), or fails, the gateway automatically falls back to the deterministic `clarify_action_map`, enqueuing a pre-generated standard clarification (e.g., "I'm sorry, I didn't quite get that...").

## 10. Security
The LLM is prompted strictly to resist prompt injection and to refuse answering inappropriate or off-topic queries. The conversation history is sanitized before injection. The vLLM server is only exposed to the internal Docker network.

## 11. GPU Requirements
The architecture requires at least a 4GB VRAM NVIDIA GPU (e.g., GTX 1650/RTX 3050) when running the quantized 1.5B model, utilizing `--gpu-memory-utilization 0.75` and constrained max sequence lengths (`--max-model-len 2048`). A 16GB+ GPU is required for the full 8B model.

## 12. Dummy Provider
`app.realtime.providers.llm_dummy:DummyLLMProvider` is provided for running integration tests or executing the system in environments without GPU resources.

## 13. Verification Matrix
- [x] vLLM startup and health checks successful
- [x] Provider interface abstracts generation logic
- [x] Fallback triggers on complex out-of-domain queries
- [x] Pre-generated TTS handles simple invalid inputs instantly
- [x] `benchmark_llm.py` confirms strict latency constraints
- [x] Dummy provider functions as drop-in replacement
