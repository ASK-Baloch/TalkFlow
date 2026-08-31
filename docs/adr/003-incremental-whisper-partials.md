# ADR 003: Incremental Whisper Partials

## Status
Accepted

## Context
Phase 3 requires emitting partial ASR transcripts to support low-latency application responses and voice activity visualization. We need to decide how to generate these partials using our baseline model, Whisper large-v3-turbo (via CTranslate2).

## Decision
Faster-Whisper is selected as the Phase 3 production baseline.
Partial transcripts will be generated using repeated incremental decoding of the continuously growing utterance buffer.

This is explicitly NOT considered a true stateful streaming decoder, but rather an "incremental partial ASR" strategy.

## Reason
- **Accuracy**: Whisper provides excellent out-of-the-box accuracy for general domain speech and our specific vocabulary.
- **Stability**: The CTranslate2 abstraction and Faster-Whisper wrapper are stable and mature.
- **Domain Performance**: The model meets our strict domain-term and numeric accuracy requirements.
- **Abstraction**: Our provider architecture allows us to substitute a true streaming provider later without impacting the application.

## Consequences
- **Repeated Compute**: Decoding the growing buffer repeatedly results in overlapping, redundant compute.
- **Revision**: Partials may fluctuate or be revised as more context becomes available.
- **FINAL Authority**: The FINAL transcript event remains the authoritative source of truth.
- **Future Benchmarks**: Future true-streaming providers (e.g. Parakeet/Nemotron) can be integrated and benchmarked independently against this baseline.
