# 19. Barge-In Generation Invalidation

Date: 2026-09-08

## Status

Accepted

## Context

In TalkFlow Phase 7, we introduced caller barge-in (interruption). When a caller interrupts the bot, the AI Gateway stops the current Text-to-Speech (TTS) playback and flushes any queued audio responses.

However, stopping the current playback task and flushing the queue does not address in-flight asynchronous operations. For example, if the Automatic Speech Recognition (ASR) service was currently processing a delayed transcript, or the Qualification Engine was formulating a response right before the interruption, a new TTS playback request might be added to the queue *after* the interruption but *derived from stale context*.

Simple task cancellation alone does not protect against late provider results that slip into the TTS queue, which would cause the bot to speak a response to something the user said several seconds ago, completely ignoring the interruption.

## Decision

TalkFlow uses monotonic per-call `PlaybackGeneration` IDs to invalidate stale queued or generated TTS after caller barge-in.

When a barge-in event occurs, the session's monotonic generation ID is incremented. When a TTS playback request is enqueued, it is stamped with the generation ID current at the time of creation.

When the TTS worker dequeues a request to play it, the worker first checks the request's generation against the session's current generation. If the IDs do not match (i.e., a barge-in occurred in the interim), the audio is considered stale and is immediately dropped.

## Consequences

- **Acoustic Realism**: Ensures the bot does not speak out of turn with responses to stale context.
- **Robustness**: Provides a rock-solid, race-condition-free mechanism to protect against late asynchronous ML results bleeding into new conversational turns.
- **Complexity**: Requires all TTS enqueueing mechanisms to properly fetch and attach the current generation ID to the `PlaybackRequest`.
- **Metrics**: Allows us to track `stale_requests_dropped_total` to measure how often delayed async results are safely neutralized by the system.
