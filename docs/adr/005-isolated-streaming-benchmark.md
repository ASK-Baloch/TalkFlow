# ADR 005: Isolated Streaming Backend Benchmark

## Status
Accepted

## Context
Phase 3 requires low-latency ASR, currently met by Faster-Whisper using an incremental partial strategy. True stateful streaming backends (e.g., Parakeet/Nemotron) may offer lower latencies and better compute efficiency by avoiding repeated incremental decoding. However, replacing the current stable Faster-Whisper provider is risky.

## Decision
Parakeet/Nemotron (or any other true-streaming backend) must be benchmarked entirely separately from the current production codebase in an isolated environment. 

We will explicitly NOT replace Faster-Whisper in the main runtime until the alternative provider is proven.

## Reason
We must preserve the current baseline's accuracy and functional stability while evaluating new providers. An isolated benchmark ensures that changes required for a true streaming abstraction do not pollute or regress the existing implementation.

## Consequences
- The Faster-Whisper architecture remains untouched for now.
- The new benchmark must capture identical metrics for direct comparison:
  - general WER
  - TalkFlow domain-term accuracy
  - ZIP exact accuracy
  - age exact accuracy
  - Part A/Part B exact accuracy
  - partial TTFT
  - final latency (queue_ms, decode_ms, acoustic_end_to_final_ms, committed_end_to_final_ms)
  - RTF
  - VRAM usage
  - GPU utilization
  - concurrent capacity (ASR workers)
