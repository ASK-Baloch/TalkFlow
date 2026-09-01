# ADR 013: Deterministic Qualification Engine

## Status
Accepted

## Context
We need a mechanism to gather, validate, and evaluate qualification data (Consent, Name, Age, Medicare, ZIP) from callers over real-time SIP streams.

## Decision
Medicare consent and qualification decisions are implemented in deterministic, regex-based application logic rather than delegated to a generative LLM.

## Reasons
- **Predictability**: A deterministic state machine guarantees a finite, bounded conversation graph.
- **Auditability**: Explicit code paths make it trivial to explain why a caller was qualified or disqualified.
- **Lower Latency**: Running regex and static policies locally eliminates the multi-second network round-trip of querying an LLM.
- **Lower Cost**: Completely avoids per-token API charges for the qualification phase.
- **Easier Testing**: Unit tests can be written to assert precise output states based on given input strings.
- **Consistent Campaign Compliance**: Assures rigorous adherence to compliance scripts and consent protocols.
- **Less Hallucination Risk**: Prevents LLMs from "hallucinating" false positives from ambiguous or unrelated background noise.
- **Simpler Debugging**: Deterministic outputs enable straightforward, line-by-line debugging of conversational state logic.
