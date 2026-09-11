# 24. Pronunciation Lexicon

Date: 2026-09-11

## Status

Accepted

## Context

Different TTS models have varying quirks when pronouncing domain-specific terminology (e.g., "Medicare Part A" vs "Medicare part ah", or specific acronyms). Relying strictly on regex search-and-replace for domain terms results in bloated, brittle code scattered across the business logic. 

Furthermore, hardcoding these terms within the application source requires code deployments for simple pronunciation tweaks and makes it difficult to maintain language-specific variations.

## Decision

We will implement a configuration-driven `PronunciationLexicon`. 

1. **JSON Configuration**: Domain pronunciation fixes are stored in a versioned JSON lexicon (e.g., `config/pronunciation/en-US.json`).
2. **Startup Loading**: The lexicon is strictly loaded into memory exactly once at application startup during the FastAPI lifespan to guarantee zero disk I/O latency during live streaming calls.
3. **Immutability**: The lexicon acts as trusted configuration. Neither caller transcripts nor LLM outputs are permitted to dynamically append or modify pronunciation rules. 
4. **Missing Lexicon Policy**: If the production lexicon file is missing, the gateway will intentionally fail to start up rather than silently defaulting to an unknown pronunciation state.

## Consequences

- **Positive**: Pronunciation rules are isolated from Python code, making it easy for non-engineers to update terms.
- **Positive**: Highly performant (loaded strictly into memory).
- **Positive**: Prevents malicious or accidental prompt injection from altering system-wide pronunciation rules.
- **Negative**: Requires careful environment variable mapping (e.g., Docker volumes) to ensure the configuration file is reliably present at startup.
