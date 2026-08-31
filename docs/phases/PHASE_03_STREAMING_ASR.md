# Phase 3: Streaming ASR

## Terminology
The current ASR implementation uses **incremental partial ASR**, not a true streaming decoder. Faster-Whisper partials are produced by repeatedly decoding a growing utterance buffer. This is incremental decoding, not stateful decoder streaming. Future backends (e.g. Parakeet/Nemotron) may be benchmarked as true streaming backends, but currently, Faster-Whisper serves as the production baseline.

## Architecture & Configuration
- **Provider**: Faster-Whisper (via `FasterWhisperProvider` abstraction)
- **Model**: Whisper large-v3-turbo-ct2 (CTranslate2)
- **Device**: CUDA
- **Compute Type**: `int8_float16`
- **Input Pipeline**: AudioSocket (8kHz PCM) -> NumPy buffer -> Resampling -> 16kHz float32 -> ASR Provider. (No Kafka, JSON, or Base64 in the critical hot path).
- **Incremental Partial Strategy**: The system schedules repeated partial decodes on the growing buffer.
- **FINAL Strategy**: Once VAD detects speech end, a FINAL job is queued.
- **Speculative FINAL Strategy**: A `FINAL_TENTATIVE` is queued during the VAD grace period to hide latency.
- **Queue Architecture**: `asyncio.PriorityQueue` manages `PARTIAL` (priority 10), `FINAL_TENTATIVE` (priority 1), and `FINAL` (priority 0) jobs.
- **Worker Configuration**: Configurable via `ASR_WORKERS`.
- **Latency Metrics**: Measured using `partial_ttft`, `decode_ms`, `queue_ms`, `acoustic_end_to_final_ms`, and `committed_end_to_final_ms`.
- **Accuracy Methodology**: Evaluated via general WER, domain-term accuracy, and exact digit/ZIP accuracy. (e.g. "seven five zero zero one" vs "75001").
- **Known Limitations**: Incremental decoding involves repeated compute. Pure streaming backends will be evaluated later.
- **Cold Start Warmup**: A 3-pass warmup using `asr_final_beam_size` and a real `.wav` fixture is executed before accepting connections to eliminate lazy initialization latency.

## Hot Path
1. AudioSocket receives chunk (8kHz PCM).
2. Bytes converted directly to NumPy array.
3. Resampled to 16kHz float32.
4. Sent directly to ASR provider.

There are NO intermediate hops like Kafka, base64 encoding, JSON marshalling, HTTP, or filesystem writes in the hot path. Partial transcripts remain local. Only finalized transcripts may eventually be published to Kafka in future phases.

## Real Call Benchmark Procedure
To benchmark, use `scripts/simulate_rapid_turns.py <pause_ms>`.
For each phrase, the test logs:
- utterance ID, speech start, first partial, committed speech end, final transcript
- Latency breakdown: `queue_ms`, `decode_ms`, `acoustic_end_to_final_ms`, `committed_end_to_final_ms`, `rtf`
Repeat samples to calculate P50, P95, and max.

## Definition of Done
Production GPU requirement met and benchmarked. Latencies fall within acceptable thresholds. No regressions in audio parsing, finalization, or speculative decoding.
