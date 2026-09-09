# 21. Qwen3-8B-AWQ vLLM Fallback Model

Date: 2026-09-09

## Status
Accepted

## Context
TalkFlow primarily drives conversations using a deterministic state machine to ensure compliance, precise field extraction (age, medicare parts, etc.), and sub-second latency via pre-generated TTS responses. However, when users ask complex, out-of-domain questions or require elaborate clarifications (e.g., "What is Medicare Part A?"), the deterministic engine falls back to a simplistic "I didn't quite get that" response. 

To improve the conversational experience for unhandled edge cases, we need a fallback mechanism that leverages a Large Language Model (LLM) to answer these specific questions seamlessly without adding unnecessary latency to the primary fast-path flows.

## Decision
TalkFlow uses **Qwen/Qwen3-8B-AWQ** served through **vLLM** as a conversational fallback model.

## Constraints
* **Non-thinking mode**: The LLM runs in standard generation mode to ensure the lowest Time-To-First-Token (TTFT). Chain-of-thought/thinking modes are disabled to prevent unacceptable latency spikes during realtime voice calls.
* **Does not control qualification**: The LLM operates strictly as a fallback responder. It does not update state variables, extract business fields, or make qualification decisions. The deterministic state machine maintains full authority over conversation state.
* **Short responses**: The model is prompted and configured to generate concise, single-sentence responses that sound natural in a voice conversation. Max output tokens are strictly constrained.
* **Provider abstraction**: The model may be replaced later through `LLMProvider` (specifically using `OpenAICompatibleLLMProvider` or `DummyLLMProvider`) without changing the core business logic.
* **Separate inference process**: The vLLM engine runs in a separate isolated container/process, ensuring the AI gateway's real-time event loop (ASR/TTS/WebSockets) is never blocked by GPU inference.

## Consequences
* **Positive**: The system can intelligently handle complex queries and gracefully recover from out-of-domain questions without breaking character.
* **Positive**: Abstracting the LLM through a provider interface ensures we are not locked into Qwen and can easily test dummy providers.
* **Negative**: Fallback responses incur LLM generation latency and dynamic TTS latency, making them significantly slower than the primary pre-generated TTS path.
* **Negative**: Running vLLM requires additional GPU resources on the deployment host.
