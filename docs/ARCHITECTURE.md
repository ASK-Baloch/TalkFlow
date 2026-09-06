# TalkFlow Architecture

## System Overview
TalkFlow is a real-time conversational AI system designed to interface directly with telephony endpoints (e.g. Asterisk) over the AudioSocket protocol. 

The architecture is built heavily around real-time streaming, strict ML isolation, and provider-based dependency injection. 

## Core Components

### 1. Canonical Flow
```text
Asterisk / AudioSocket
        ↓
Silero VAD
        ↓
Streaming ASR
        ↓
FINAL transcript
        ↓
Deterministic Qualification Engine
        ↓
ConversationAction
        ↓
Response Catalog
        ↓
Pre-generated PCM cache
        ↓
AudioSocket
        ↓
Caller
```
The core orchestration service managing the conversational loop.
- **Service Registry & Dependency Injection**: Provides a stable provider abstraction (`STTProvider`, `TTSProvider`) so the Gateway is decoupled from specific ML model SDKs.
- **Voice Activity Detection (VAD)**: Utilizes Silero VAD to detect speech presence, enabling the system to smartly capture user utterances and reject background noise.
- **Streaming ASR Service**: Consumes audio from the VAD and coordinates decoding. The core implementation relies on Faster-Whisper, supporting both final and partial transcription streams.
- **Qualification Engine**: The business logic tier responsible for analyzing transcripts, extracting fields (e.g. name, age, zipcode, consent), and deciding the next action in the conversational flow without hardcoded branching.
- **TTS Pacing & Playback**: Receives text to speak and utilizes TTS providers (pre-generated or dynamic) to fetch PCM audio. A pacing loop carefully chunks the audio into 20ms frames and transmits it back over AudioSocket exactly at the speed of spoken audio, avoiding PBX buffer overflow.

### 3. ML Workers
Heavy neural generation runs out-of-process to protect the real-time Gateway.
- **Chatterbox TTS Worker**: An independent HTTP microservice housing the generative neural TTS engine. The AI Gateway sends text over the local network, and the worker synthesizes and returns full PCM streams, isolating PyTorch/CUDA demands from the core connection loop.

## Design Principles
- **Strict Decoupling**: Business logic never touches model SDKs directly.
- **Isolate ML**: Heavy inference (generative TTS) runs in separate processes.
- **Paced Output**: Never push audio faster than real-time to avoid overwhelming the PBX.
