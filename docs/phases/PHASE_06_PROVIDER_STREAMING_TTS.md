# Phase 6: Provider Streaming TTS

## Overview
Phase 6 decoupled business logic from concrete ML dependencies by introducing a provider abstraction for Speech-To-Text (STT) and Text-To-Speech (TTS). It also introduced dynamic, generative TTS using an isolated Chatterbox ML worker, paving the way for conversational interactions.

## Architecture
- **Provider Interfaces**: `TTSProvider` and `STTProvider` abstract away the underlying logic. The AI Gateway relies on these interfaces, loaded dynamically based on environment variables.
- **Dependency Injection**: A service registry wires up `AsrService` and `TTSService` with their configured providers (e.g. `FasterWhisperSTTProvider`, `PregeneratedTTSProvider`, `ChatterboxHttpTTSProvider`).
- **Worker Isolation**: The dynamic TTS ML pipeline (Chatterbox) is deployed as a standalone HTTP microservice rather than directly inside the AI Gateway.
- **Dynamic TTS Routing**: Requests for dynamic text synthesize raw PCM audio from the standalone TTS worker, which the Gateway then chunks and streams into the AudioSocket pacing loop.

## Key Outcomes
- Fully eliminated direct model SDK imports (e.g. FasterWhisper, Chatterbox) from Gateway business services.
- Isolated ML runtime environments to protect the Gateway from heavy VRAM/CPU operations and library version conflicts.
- Implemented and benchmarked Chatterbox generative TTS, establishing baseline Real-Time Factor (RTF) metrics and identifying Time-To-First-Audio (TTFA) bottlenecks.
