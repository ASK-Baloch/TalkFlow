# Phase 10: Speech Normalization

## Goal
Improve TTS pronunciation reliability for dynamic LLM responses by translating business text into explicit spoken forms (e.g., expanding ZIP codes, normalizing currency/phone numbers) without corrupting conversational history.

## Pipeline Position
Normalization occurs synchronously on dynamic text *after* the `SentenceAssembler` produces a logically complete segment and `ResponsePlanner` wraps it into a `PlannedResponse`, but *before* the TTS worker begins generation.

```
Qwen Token Stream
 ↓
SentenceAssembler
 ↓
ResponsePlanner (yields PlannedResponse)
 ↓
ResponseSpeechProcessor (updates tts_text)
 ↓
TTS Worker (consumes tts_text)
```

## `display_text` vs `tts_text`
A key design principle is the strict separation between what is read by an LLM/dashboard (`display_text`) and what is sent to speech synthesis (`tts_text`). Normalization modifies **only** `tts_text`. This ensures conversational context arrays and user-facing logs retain original canonical text (like "$10.50"), while the TTS engine receives explicit spoken forms ("ten dollars and fifty cents").

## Business-State Separation
The `SpeechNormalizer` has no access to qualification state or core business logic (`TurnController`). It operates independently as a pure text transformation layer, receiving context (like `expected_field="zip_code"`) rather than querying the application state. Qualification business logic depends on raw LLM/ASR values, not spoken ones.

## Normalization Rules
Rules execute in a strictly defined order to prevent collisions (e.g., expanding a phone number shouldn't trigger arbitrary number expansion later):
1. **Punctuation/Markdown cleanup**: Strips formatting like `**` or excess symbols.
2. **Lexicon replacements**: Exact/case-sensitive configurable replacements (e.g., "Medicare Part A").
3. **ZIP handling**: Translates "75001" to "seven five zero zero one" when `expected_field="zip_code"`.
4. **Phone handling**: Spells out standard phone strings into individual digit words.
5. **Currency/Percentage handling**: "$20" → "twenty dollars", "50%" → "fifty percent".
6. **Generic numbers**: Conditionally converts remaining isolated integers.
7. **Whitespace collapse**: Flattens out redundant spaces.
8. **Provider Adapters**: Hooks for provider-specific formatting (like custom tags).

## Pronunciation Lexicon
To avoid hardcoding domain terms into regex, TalkFlow uses a JSON-based lexicon loaded exactly once at startup (`config/pronunciation/en-US.json`). This configures deterministic overrides for terms like "Medicare Part B", ensuring they never break dynamically generated speech. Callers and LLMs are explicitly prevented from modifying this configuration.

## Provider Adapter
Phase 10 includes a generalized `SpeechProviderAdapter` interface that applies provider-specific text transformations as the final normalization step. This ensures `tts_text` is cleanly formatted for the selected dynamic TTS engine (e.g., `ChatterboxTTSProvider`) without tightly coupling normalizer rules to any single vendor's SDK.

## Phase 5 Integration
Phase 10 rules apply exclusively to dynamic TTS. Pre-generated Phase 5 deterministic prompt assets (like `ask_zip.wav`) bypass runtime normalization completely. If deterministic prompts need pronunciation fixes, they should be regenerated offline using the same normalization rules to maintain architectural consistency.

## Phase 9 Streaming Integration
The `ResponseSpeechProcessor` processes text only after it is emitted as a complete segment by the Phase 9 `SentenceAssembler`. Token-by-token normalization is explicitly prohibited as it breaks contextual lookahead requirements. 

## Barge-In Non-Interference
Interruption logic built in Phase 9 seamlessly wraps Phase 10. If an interruption occurs mid-normalization or during TTS generation, `TurnController` cancels generation and the TTS queue. Normalization holds no blocking state and does not participate in barge-in handling, honoring the decoupled design.

## Error Behavior
If normalization throws an unexpected error, it will log the stack trace, increment the `speech_normalization_failures_total` metric, and fail safely by assigning `tts_text = display_text`. The call will not drop. Normalization is an enhancement, not a critical path failure point.

## Metrics
The gateway tracks specific metrics for monitoring normalization performance and coverage, avoiding raw text logs:
- `speech_normalization_total`
- `speech_normalization_changed_total`
- `speech_normalization_failures_total`
- `speech_normalization_ms_p50` / `p95`
- Sub-rule totals (e.g., `speech_rule_zip_total`, `speech_rule_lexicon_total`)

## Tests & QA Corpus
The rules are validated through `tests/unit/speech/test_qa_corpus.py`. This test suite loads the production lexicon via `.env` configuration and runs assertions on a static corpus of tricky phrases (ZIP codes, age confirmations, Markdown cleanup) to ensure domain integrity and zero regressions.

## Definition of Done
Phase 10 is considered complete when:
- Normalization safely separates `display_text` and `tts_text`.
- The synchronous processing adds minimal latency (sub-1ms).
- Integration testing verifies streaming compatibility and zero coupling to business logic.
- An automated QA corpus regression suite guards the rules.
