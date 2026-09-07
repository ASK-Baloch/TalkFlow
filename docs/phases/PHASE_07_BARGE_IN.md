# Phase 7: Barge-In (Interruption)

## Goal
Implement robust caller barge-in capabilities, allowing callers to interrupt the AI's playback naturally, simulating a human-like conversation flow.

## Architecture
TalkFlow's barge-in architecture relies on a strict decoupling of event detection and playback cancellation:

```text
Asterisk / AudioSocket
        ↓
VAD ──────────── SPEECH_START
        ↓               │
Streaming ASR           │
        ↓               ↓
Qualification     BargeInController
        ↓               ↓
Planner            TTSService.interrupt()
        ↓               ↓
TTSProvider      cancel playback
        ↓               ↓
20 ms PCM frames ← generation invalidation
        ↓
Asterisk
```

### SPEECH_START Trigger
Barge-in is triggered instantly upon receiving a `SPEECH_START` event from the Voice Activity Detection (VAD) service. This is prioritized over waiting for the Automatic Speech Recognition (ASR) to emit partial or final transcripts. Triggering on VAD ensures that the interruption happens within milliseconds of the caller speaking, maintaining acoustic realism.

### Why VAD Remains Active During Playback
The VAD continuously processes inbound audio from the caller even while the AI is speaking. The telephony architecture (Asterisk AudioSocket) natively provides full-duplex audio. TalkFlow listens to the caller's inbound stream for the presence of speech, so it can detect an interruption precisely when the caller starts talking.

### Why ASR Remains Active During Playback
Alongside VAD, the streaming ASR remains active during playback. By processing the audio in real-time, the ASR buffers the "pre-roll" audio (the beginning of the caller's sentence that triggered the barge-in). When the caller finishes speaking, the ASR can emit a complete transcript without truncating the beginning of the utterance.

## Interruption Mechanisms

### 20 ms Frame Cancellation
TTS playback is paced carefully by yielding 20ms PCM frames matching the real-time consumption rate of the PBX. When an interruption occurs, the playback loop immediately halts its frame-yielding process, preventing any buffered audio from being transmitted to the caller.

### Generation IDs
To prevent race conditions where a slow TTS generation task attempts to play audio *after* an interruption has occurred, TalkFlow utilizes monotonic `PlaybackGeneration` IDs. Every new interruption increments the global session generation ID. If a TTS playback request is dequeued, it must match the current generation ID; otherwise, it is treated as stale and dropped.

### Queue Flushing
When an interruption occurs, any pending TTS playback requests in the session's queue are flushed. This ensures that queued prompts (such as secondary follow-up questions) are not accidentally played after the caller has already taken their turn.

### Provider Cancellation Interface
When a playback is halted, `TTSService.interrupt()` invokes the `provider.cancel()` interface. This allows underlying dynamic providers (e.g., Chatterbox TTS) to abort expensive neural generation tasks if they are still running, conserving compute resources.

### Chatterbox Cancellation Limitation
Currently, `ChatterboxHttpTTSProvider` has a limitation where it does not support native streaming cancellation mid-generation, because its HTTP endpoint only returns the PCM payload once the entire synthesis completes. While the gateway drops the audio frame playback (acoustically stopping the bot), the remote Chatterbox worker still finishes generating the discarded audio.

## Stale-Audio Protection
Stale-audio protection guarantees that if an ASR final transcript was in-flight during an interruption, or if a TTS task was delayed, the newly generated audio is verified against the `PlaybackGeneration` ID before transmission. If `drop_stale_audio` is enabled, mismatched generations are dropped.

## Metrics
Barge-in introduces several new metrics to track interruption latency and correctness:
- `interrupted_playbacks_total`: Total number of playbacks successfully halted.
- `queue_flushes_total`: Total number of queued prompts discarded during an interruption.
- `stale_requests_dropped_total`: Playback requests dropped due to generation mismatch.

## Testing & Validation

### Test Matrix
- **Automated Integration Tests**: `tests/integration/tts/test_barge_in.py` uses deterministic audio frames (via `DummyTTSProvider`) to emit `SPEECH_START` and measure cross-module cancellation flow accurately.
- **Provider Abstraction Integrity**: Ensure that swapping providers (e.g., dummy STT to Faster-Whisper, dummy TTS to Chatterbox) requires only configuration changes.

### Live Asterisk Test
A live Asterisk call should demonstrate the following:
1. AI starts playing a long prompt (e.g., "Before we continue, may I ask you a few questions...").
2. Caller speaks ("I don't know").
3. AI stops speaking within single-digit to tens of milliseconds (P95 < 50ms latency from SPEECH_START).
4. AI waits for the caller to finish speaking.
5. AI replies to the new utterance without playing the rest of the old prompt.

## Definition of Done
- `BargeInController` successfully triggers `TTSService.interrupt()` on VAD `SPEECH_START`.
- Paced playback correctly stops yielding frames.
- Monotonic generation IDs prevent stale audio playback.
- Queue is flushed on interruption.
- Metrics accurately reflect barge-in events.
- All unit and integration tests pass cleanly.
