# 17. Pre-generate deterministic speech

Date: 2026-09-07

## Status

Accepted

## Decision

All finite deterministic TalkFlow prompts are synthesized in advance rather than synthesized during each live call.

## Reasons

- near-zero generation latency
- predictable pronunciation
- lower GPU pressure
- no runtime Kokoro dependency
- stable call quality
- easy QA
- easy rollback
- lower concurrency cost
