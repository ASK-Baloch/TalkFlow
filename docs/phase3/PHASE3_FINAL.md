# Phase 3 Final Report: ASR Model Selection & Optimization

**Status:** CONDITIONAL PASS — PERFORMANCE EXCEPTION

## Decision
ASR architecture, queue scheduling, speculative final safety, regression framework, and the selected model are sufficiently mature to unblock development of the qualification engine (Phase 4).

## Known Exception
- **Performance:** Local RTX 2050 `acoustic-end -> final P50` is **1002.9ms**, approximately 203ms above the original Phase 3 target of <=800ms.
- Queue contention itself *is* resolved (Final queue P50 is 0.1ms).

## Frozen Configuration

| Component | Value/Version |
|-----------|---------------|
| **Model Identifier** | `large-v3-turbo-ct2` (Whisper large-v3-turbo) |
| **CT2 Version** | `4.4.0` (as per environment) |
| **faster-whisper Version** | `1.0.3` (as per environment) |
| **Compute Type** | `int8_float16` |
| **Language** | `en` |
| **Decoding Settings** | `beam_size=1`, `condition_on_previous_text=False`, `word_timestamps=False` |
| **State Prompt Routing** | Active (e.g. `initial_prompt="TalkFlow"`, dynamic hints) |
| **VAD Configuration** | Silero VAD, 512ms `min_silence_duration_ms` for PENDING_END, 1200ms `min_silence_duration_ms` for SPEECH_END |
| **ASR_WORKERS** | `2` |
| **Partial Interval** | 480ms |
| **Partial Admission Rules** | Strict priority queue; max `1` active/queued partial globally (others coalesced/dropped). |
| **Speculative-Final** | Executed at `PENDING_END`. Promoted to `FINAL` if text matches upon `SPEECH_END`. |
| **Normalization Rules** | Active (numbers, zip codes, states, abbreviations). |
| **Semantic Extractor** | Active. |
| **Manifest** | `phase3_v1` (Frozen 37-sample subset in `n:\TalkFlow\services\ai-gateway\phase3_human_review`). |

## Measured Benchmark Results
*Note: This is a 37-sample regression/engineering validation set. Do NOT claim 98%, near-perfect, or production-grade statistical accuracy.*

- **WER:** 17.5%
- **Medicare:** 7/9
- **Medicaid positives:** 0 samples
- **Part A:** 6/6
- **Part B:** 4/5
- **Negation:** 3/3
- **ZIP:** 2/2
- **Humana:** 0/1
- **Aetna:** 0/1
- **UnitedHealthcare:** 1/1
- **Blue Cross:** 1/1
- **TalkFlow:** 7/10
- **Medicare/Medicaid confusion:** 1/9
- **Part A/B confusion:** 0/9

## Speculative Breakdown (Diagnostic Only)

### FINAL_TENTATIVE Speculative Hits (N=16)
- `acoustic_end_to_final` P50: 980.8 ms
- `acoustic_end_to_final` P95: 1555.2 ms
- `queue` P50/P95: 0.1 ms / 761.4 ms
- `compute` P50/P95: 869.0 ms / 1187.0 ms

### Standard FINAL Fallbacks (N=1)
- `acoustic_end_to_final` P50/P95: 1628.0 ms
- `queue` P50/P95: 0.2 ms
- `compute` P50/P95: 1124.5 ms

*(Note: N=17/20 accounted for in diagnostic parse; the remaining 3 were either dropped due to VAD truncation or logged differently).*
