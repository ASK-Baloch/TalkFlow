# 23. Speech Normalization Boundary

Date: 2026-09-11

## Status

Accepted

## Context

As TalkFlow transitioned from purely pre-generated Phase 5 deterministic prompts to Phase 9 dynamically generated LLM speech, text formatting issues emerged. Specifically, large language models generate readable numbers ("75001") and markdown ("**Medicare**") that text-to-speech engines struggle to vocalize naturally or explicitly. 

Initially, there was a risk that normalizing text for TTS would corrupt the `display_text` seen on dashboards or leak into the LLM's conversational history, polluting the model's contextual understanding of the user's data (e.g., passing "seven five zero zero one" back into context instead of "75001").

Additionally, tying normalization to the core business logic (such as `TurnController` or Qualification rules) would deeply entangle the application's conversational state with presentation-layer formatting.

## Decision

We will implement a strict boundary where TalkFlow stores business/display values separately from the text rendered for speech. 

1. **Separation of Concerns**: The `PlannedResponse` model will explicitly maintain two fields: `display_text` (canonical/LLM-generated) and `tts_text` (spoken representation).
2. **Pipeline Position**: The `SpeechNormalizer` executes after response planning (where text is chunked by the `SentenceAssembler`) and immediately before dynamic TTS rendering.
3. **State Independence**: The normalizer functions as a pure transform layer. It receives context hints (like `expected_field="zip_code"`) but holds no qualification state and does not participate in call coordination, cancellation, or barge-in tracking.

## Consequences

- **Positive**: LLM conversational history and dashboards remain perfectly clean and accurate.
- **Positive**: Decoupling the normalizer from the `TurnController` prevents business logic regressions when adjusting pronunciation rules.
- **Positive**: Normalization logic can safely be reused offline to generate future deterministic prompt assets.
- **Negative**: Adds a fast but necessary synchronous string-manipulation step prior to TTS delivery.
