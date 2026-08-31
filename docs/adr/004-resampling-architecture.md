# ADR 004: Current Resampling Architecture

## Status
Accepted

## Context
Audio is streamed from telephony over AudioSocket at 8kHz, but Faster-Whisper ASR requires 16kHz audio. We need to document the exact hot-path for this resampling to ensure no unnecessary intermediate hops exist.

## Decision
The current production architecture implements the following audio resampling path:

`AudioSocket (PCM bytes)` -> `NumPy int16` -> `NumPy float32 (8kHz)` -> `soxr.ResampleStream` -> `NumPy float32 (16kHz)` -> `ASR Provider`

### Details
- Audio is decoded from PCM bytes to int16.
- It is scaled to `float32` in the range `[-1.0, 1.0]`. A slight `0.9` gain reduction is applied to prevent Sinc resampling overshoot (Gibbs phenomenon).
- `StreamingResampler` uses `soxr.ResampleStream` to continuously resample chunks.
- Output is clipped to strictly enforce `[-1.0, 1.0]` bounds for ASR stability.

**stateful streaming continuity not yet proven**

## Consequences
- We do not rely on external services, Kafka, base64 encoding, or JSON wrappers to move audio between the socket and the ASR module.
- Any future changes to this architecture MUST prove continuous statefulness across chunks to prevent clicking or artifacts at chunk boundaries.
