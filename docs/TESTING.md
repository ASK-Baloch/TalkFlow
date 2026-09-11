# TalkFlow Testing Strategy

## Overview
The testing architecture is designed to validate the strict isolation boundaries between our real-time streaming components. Because the system relies heavily on `asyncio` concurrency and independent failure domains, tests are focused heavily on cancellation behavior and event propagation.

## Verification Matrix

### 1. ConversationTurnController (Cancellation Independence)
Validates that `TurnInterruptionResult` accurately reflects what components were cancelled during a barge-in, and proves that one component crashing does not hang the other components.

| Scenario | LLM Cancellation | TTS Interruption | Response Orchestrator Interruption | Expected Outcome |
| :--- | :--- | :--- | :--- | :--- |
| Standard Barge-in | Success | Success | Success | Clean turn interruption, all tasks halted. |
| LLM Hangs/Crashes | Fails | Success | Success | TTS halts playback instantly; orchestrator stops polling. |
| TTS Provider Unreachable | Success | Fails | Success | LLM stops generating text immediately; orchestrator stops. |

### 2. StreamingResponseOrchestrator
Validates the dynamic generation pipeline handling SSE streaming text from the LLM provider.

- **Sentence/Clause Assembly**: Validates that raw tokens are chunked perfectly on boundaries (`.`, `?`, `!`, `\n`) by the `SentenceStreamAssembler` before pushing to TTS.
- **Stale Token Rejection**: Ensures any tokens received *after* a generation invalidation (due to barge-in) are instantly dropped and not pushed to the TTS queue.

### 3. VAD & ASR Isolation
Validates that `SPEECH_START` and `SPEECH_END` events properly coordinate state changes.
- **VAD Triggers**: The `ConversationTurnController` should be interrupted precisely on `SPEECH_START`.
- **False Positives**: Short VAD blips that do not yield an ASR transcript must properly flush and reset without crashing the pipeline.

## E2E Integration Testing
The repository uses a mock `run_test_client.py` for headless integration.
1. Establishes a raw TCP connection mimicking Asterisk AudioSocket (Port 9019).
2. Transmits 160-frame (20ms) 8k PCM payloads mimicking a real phone caller.
3. Observes the response TTS frames flowing back in real-time.
4. Simulates barge-ins by halting the mock stream and observing immediate connection flush.

## 4. QA Speech Corpus
Validates the `SpeechNormalizer` logic to ensure domain terms (Medicare Part A, ZIP codes, phones) are properly separated into `tts_text` without altering canonical `display_text`.
- **Lexicon Loading:** Asserts the configuration-driven JSON lexicon properly loads exactly once and translates accurately without case-sensitivity errors.
- **Order of Operations:** Asserts that general numbers don't inadvertently corrupt explicit ZIP codes or phone numbers by applying tightly ordered regex passes.
