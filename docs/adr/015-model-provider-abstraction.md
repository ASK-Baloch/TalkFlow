# 15. Model Provider Abstraction

Date: 2026-09-07

## Status

Accepted

## Context

The TalkFlow AI Gateway was tightly coupled to specific Machine Learning implementations (like `FasterWhisper`). Services responsible for business logic, AudioSocket pacing, and qualification workflows were importing ML SDKs directly. This created issues when testing logic in isolation and made it hard to swap models (e.g. replacing a heavy STT with a cloud API or a dummy model).

## Decision

STT and TTS model implementations must exist behind stable TalkFlow provider interfaces (`STTProvider` and `TTSProvider`). Business logic, qualification, AudioSocket transport, and response planning cannot import model SDKs directly. 

Providers will be loaded dynamically using Dependency Injection via a Service Registry, guided by `.env` configurations (e.g., `STT_PROVIDER_CLASS`).

## Consequences

- **Pros:** 
  - Isolated testing (via Dummy providers) is now possible without relying on heavy ML operations.
  - The core Gateway is extremely flexible and can support multiple backends concurrently without changing business logic.
- **Cons:** 
  - Adds a layer of indirection, requiring explicit provider mapping in settings.
