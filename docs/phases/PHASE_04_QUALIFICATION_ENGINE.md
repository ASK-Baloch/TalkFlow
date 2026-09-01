# Phase 4: Deterministic Qualification Engine

## Goal
To evaluate caller qualifications based on strict deterministic business rules and route the call appropriately, prioritizing precision, predictability, and compliance over loose probabilistic extraction.

## Scope
This phase consumes authoritative `FINAL` ASR transcripts from Phase 3 and produces structured `ConversationAction` objects for Phase 5 to execute. It manages the conversational state machine but does not directly execute TTS or side-effects.

## Architecture
```text
AudioSocket
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
```

*(Note for Phase 5: The `ConversationAction` will subsequently be passed to a Pre-generated TTS engine.)*

## Consent Hard Gate
The engine enforces a mandatory hard gate on consent. No qualification fields can be collected or evaluated until explicit affirmative consent is provided. If consent is explicitly declined, the flow terminates immediately.

## Required Fields
To successfully qualify a lead, the following fields are strictly required:
1. `consent`: Must be `True`
2. `full_name`: String, 1 to 5 words
3. `age`: Integer, strictly >= 65
4. `medicare_coverage`: Must have Medicare Part A **OR** Medicare Part B
5. `zip_code`: String, exactly 5 digits

## State Machine
The state machine drives the conversation sequentially through missing requirements but dynamically skips any requirements that are already satisfied.
1. `WAITING_FOR_CONSENT`
2. `COLLECTING_NAME`
3. `COLLECTING_AGE`
4. `COLLECTING_PART_A` / `COLLECTING_PART_B`
5. `COLLECTING_ZIP`
6. `QUALIFIED` or `DISQUALIFIED`

## Extraction Rules
- The engine uses strict regex rules and token filtering to pull fields from caller utterances.
- Name extraction actively scrubs conversational trailing clauses (e.g., "...and my age is 67") and rejects domain keywords (e.g., "Medicare", "Part B") to prevent cross-talk.
- Medicare Part A and B extraction actively ignores responses if the user explicitly references the *opposite* part, preventing false positives.
- If an extraction rule cannot confidently determine the value, it returns `None`, forcing the system to re-prompt rather than hallucinate.

## Validation Rules
Extracted fields are piped through validators that assert domain correctness:
- Name must only contain alpha characters (spaces and stripped punctuation allowed) and be 1 to 5 words long.
- Age must be between 65 and 120.
- ZIP must be exactly 5 digits.

## Qualification Policy
- Age < 65 causes an immediate disqualification.
- A user must have Part A `True` OR Part B `True`. If both are evaluated as `False`, the user is immediately disqualified.
- Unasked Medicare parts remain `None` and do not trigger disqualification.
- Lead is considered fully `QUALIFIED` only when all criteria are satisfied.

## Out-of-Order Handling
The engine fully supports out-of-order and global field volunteering. If a user states their name, age, and ZIP code in a single utterance, the engine extracts all relevant fields and recalculates the *next* missing field, seamlessly skipping the intervening states.

## Clarification Behavior
If the engine fails to extract a required field (e.g., the user said something unintelligible or out of domain), the system generates a `CLARIFY_{FIELD}` action rather than an `ASK_{FIELD}` action, incrementally adapting the prompt until a maximum retry threshold is reached.

## Correction Behavior
The engine honors user corrections. If the user uses a correction prefix (e.g., "Actually", "Sorry", "No wait"), the engine will overwrite an existing stored field with the new value. Without explicit correction intent, an already-valid field is protected from accidental overwrites.

## Privacy
No raw PII is exposed to third-party LLMs. All qualification parsing is strictly internal and local to the Python application runtime.

## Metrics
- Time spent in qualification
- Clarification loops per field
- Drop-off points (consent vs age vs medicare)
- Rate of out-of-order volunteering vs linear questioning

## Tests
Extensive unit tests (`tests/unit/qualification/test_engine.py`) validate regression prevention, out-of-order fields, correction parsing, logic gates, and deterministic Medicare evaluations. An integration test (`test_conversation_flow.py`) confirms full end-to-end routing.

## Live Asterisk Validation
(Pending Phase 5 and Asterisk integration)

## Limitations
- Non-standard spellings or extremely unusual names might require spell-out logic or fallback to human agents if repeated clarification fails.
- Extractor regexes require ongoing tuning as edge-case conversational patterns are discovered in production logs.

## Definition of Done
- State machine correctly routes through all fields.
- Volunteered and corrected fields are processed accurately without cross-talk.
- 100% test coverage on qualification engine paths.
- Ready to produce `ConversationAction` payloads for Phase 5.

## Next Phase
**Phase 5: Pre-generated TTS and Call Orchestration** - Mapping `ConversationAction` outputs to specific speech audio buffers and controlling the actual call loop.
