# ADR 014: Final-Transcript-Only Decisions

## Status
Accepted

## Context
Our streaming ASR engine emits two types of transcripts: `PARTIAL` (interim guesses while the caller is still speaking) and `FINAL` (the confident, committed text once the caller pauses or finishes). We need to determine which events should trigger state machine mutations.

## Decision
Qualification state is updated exclusively from authoritative `FINAL` ASR transcripts, completely ignoring `PARTIAL` transcripts for business logic mutations.

## Reasons
Using partials for irreversible state decisions is dangerous. A partial transcript like:
> *"I don't..."*

could easily evolve into a final transcript of:
> *"I don't have Part B."*

or even:
> *"I don't think that's right, but yes I have Part B."*

Relying on interim transcripts for deterministic field extraction introduces race conditions where incomplete thoughts trigger erroneous state transitions, false disqualifications, or corrupted data. By restricting mutations to `FINAL` transcripts, we ensure the qualification engine operates only on stable, complete caller utterances.
