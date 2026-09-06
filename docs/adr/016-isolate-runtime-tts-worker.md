# 16. Isolate Runtime TTS Worker

Date: 2026-09-07

## Status

Accepted

## Context

Dynamic neural Text-to-Speech (TTS) generation using models like Chatterbox is a heavy operation, demanding significant CPU and GPU VRAM. Originally, ML models were embedded alongside the real-time AI Gateway server, competing for resources and risking thread locks on the `asyncio` event loop. Additionally, loading these models forces the Gateway to depend on heavy, conflicting PyTorch distributions natively.

## Decision

Runtime neural TTS executes outside the primary real-time gateway process. It operates as an independent HTTP microservice (the TTS Worker). The AI Gateway interacts with this worker over the network (localhost/Docker networking) via the `ChatterboxHttpTTSProvider`.

## Consequences

- **Pros:** 
  - Isolates ML dependencies and CUDA memory, avoiding dependency conflicts.
  - Limits failure domains: a TTS generation crash (e.g. out of memory) will not crash the real-time Gateway managing the Asterisk AudioSockets.
  - Frees the Gateway's main loop from blocking CPU-bound generation calls.
- **Cons:** 
  - Adds network overhead and complexity of managing another microservice.
