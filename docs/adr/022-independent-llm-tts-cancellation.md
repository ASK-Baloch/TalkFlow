# 022: Independent LLM & TTS Cancellation

## Status
Accepted

## Context
During a real-time voice interaction, when a caller interrupts the system (a "barge-in"), the AI must immediately halt its current operation. This means:
1. Stopping the LLM from generating further text.
2. Stopping the TTS engine from synthesizing new audio.
3. Halting the playback of already-synthesized audio chunks.

A naive implementation might chain these operations (e.g., the orchestrator tells the TTS engine to stop, which in turn tells the LLM to stop, or vice versa). However, relying on one ML service to cancel another creates dangerous failure modes. If the TTS engine crashes or becomes unresponsive during a cancellation attempt, the LLM will continue generating tokens indefinitely, consuming resources and potentially causing race conditions when the TTS engine recovers.

## Decision
We will enforce strict ownership boundaries for cancellation:
1. **LLMService and TTSService never control one another.** They remain completely isolated and unaware of each other's existence.
2. **Conversation-level orchestration coordinates cancellation.** The `ConversationTurnController` acts as the sole orchestrator. 
3. **Independent execution.** When an interruption occurs, the controller dispatches parallel cancellation tasks (`LLMService.cancel()`, `TTSService.interrupt()`, `StreamingResponseOrchestrator.interrupt()`). These tasks are executed independently using `asyncio.gather(..., return_exceptions=True)`.

## Consequences

### Positive
- **Fault Tolerance**: If the TTS service hangs or throws an exception during interruption, the LLM service will still be successfully cancelled (and vice-versa). 
- **Decoupling**: Services can be developed, tested, and scaled independently without shared cancellation logic.
- **Predictability**: Cancellation latency is bounded by the slowest individual cancellation, rather than the sum of chained cancellations.

### Negative
- **Orchestration Complexity**: The `ConversationTurnController` must handle the state and error reporting for multiple concurrent cancellation tasks.
- **State Synchronization**: Because the LLM and TTS operate independently, there is a tiny window where the TTS might pull a buffered sentence from the orchestrator right as the orchestrator is being cancelled. We mitigate this using a strict `ResponseGeneration` validation check on the TTS queue.
