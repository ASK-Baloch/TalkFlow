# Phase 5: Pre-generated TTS

## Goal
Establish a zero-latency telephony-ready audio playback pipeline using statically pre-generated responses. This ensures a stable, high-quality fallback and sets up the AudioSocket chunking and pacing loop without the complexity of real-time ML generation.

## Architecture
The system stores pre-generated PCM files. When a `ConversationAction` is emitted by the Qualification Engine, it looks up the corresponding audio asset, loads it into memory via caching layers, and streams it back over AudioSocket at exactly real-time pacing to the caller.

## Response Catalog
A finite deterministic list of scripted responses mapped directly to the qualification state machine transitions.

## Voice
`af_heart` (from the Kokoro generator) serving as the baseline voice persona.

## Script Version
Version 1.0 of the TalkFlow qualification scripts, mapping directly to `ask_name`, `ask_age`, etc.

## Model Version
Kokoro v1.0, used entirely offline.

## Generator Process
An offline script runs the text prompts through the Kokoro SDK to synthesize raw audio waveforms.

## Source Sample Rate
Kokoro natively outputs at 24 kHz.

## 8k Telephony Conversion
The offline generator uses high-quality internal resampling (e.g., SoX/ffmpeg) to convert the 24 kHz source audio down to 8000 Hz, strictly matching the Asterisk telephony channel.

## PCM Encoding
The audio is exported as raw 16-bit signed integer PCM, little-endian, mono. No headers (e.g. WAV headers) are streamed.

## Redis Cache
Assets can be loaded into Redis for ultra-fast, distributed in-memory lookups during live calls, preventing disk I/O bottlenecks under concurrency.

## Local Fallback
A local disk fallback `TtsAssetCache` exists to serve assets directly from the `assets/tts/talkflow-chatterbox-v1` directory if Redis is unavailable or misses.

## AudioSocket Framing
Raw bytes are packed into the custom AudioSocket framing format (payload type `0x10`) with a 3-byte header defining type and length.

## 20ms Pacing
Audio is sliced into exactly 320-byte chunks (representing 20ms of 8kHz 16-bit audio) and pushed into the network socket using an `asyncio.sleep()` timing loop to prevent Asterisk queue overflows.

## Action Mapping
The `TTSService` maps logical strings like `"ask_age"` to the specific pre-generated asset UUID.

## Latency Metrics
Because the audio is pre-generated, the time from Qualification decision to the first audio byte hitting the socket (TTFB) is strictly network-bound (Redis lookup + OS socket dispatch), usually < 100ms.

## Voice QA
Since the audio is static, the voice performance is guaranteed perfect for every call. No runtime mispronunciations.

## Regression Tests
Unit and integration tests run against the `PregeneratedTTSProvider` to ensure asset caching and stream yielding work without ML dependencies.

## Live Asterisk Tests
End-to-end SSH tunnel validation verifies that Asterisk successfully receives and plays the 20ms paced packets to live callers without degradation.

## Limitations
The system cannot generate dynamic responses (e.g., repeating the user's unique name back to them).

## Definition of Done
The system can successfully conduct a fully scripted qualification call (greeting -> ask age -> ask zip -> qualify -> transfer) entirely via pre-generated AudioSocket streaming.

## Phase 6 Boundary
Phase 6 will introduce `ChatterboxHttpTTSProvider` to synthesize dynamic text at runtime, utilizing this exact same 20ms pacing loop for network transmission.
