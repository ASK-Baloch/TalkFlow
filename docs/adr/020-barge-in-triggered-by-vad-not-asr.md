# 20. Barge-In Triggered by VAD, not ASR

Date: 2026-09-08

## Status

Accepted

## Context

To simulate human-like conversations, the TalkFlow AI Gateway must support caller barge-in (interruption). When the caller speaks while the AI is talking, the AI should stop speaking as quickly as possible.

We had to decide which signal in our pipeline should trigger the interruption of the AI's Text-to-Speech (TTS) playback. The two primary candidates were:
1. **Automatic Speech Recognition (ASR)**: Trigger interruption when the ASR engine emits a partial or final transcript containing actual words.
2. **Voice Activity Detection (VAD)**: Trigger interruption the moment the VAD engine detects speech presence, before words are decoded.

## Decision

Barge-in is triggered by confirmed VAD `SPEECH_START`, not ASR output, because interruption must occur before transcription completes.

TalkFlow's `BargeInController` intercepts the `SPEECH_START` event emitted by the Silero VAD service and immediately invokes `TTSService.interrupt()`.

## Consequences

- **Ultra-Low Latency**: The AI stops speaking within single-digit to tens of milliseconds of the caller uttering a sound (P95 < 50ms latency). This matches human conversational reflexes.
- **Improved ASR Accuracy**: By halting TTS output immediately, we minimize the acoustic overlap where both the caller and the bot are speaking, which could degrade ASR performance if echo cancellation is imperfect.
- **False Positives**: Relying on VAD means that non-speech noises (like a cough, dog bark, or heavy breath) might trigger an interruption if the VAD misclassifies them. We accept this trade-off in favor of latency, and rely on the conversational engine to handle empty transcripts gracefully if the interruption turned out to be noise.
