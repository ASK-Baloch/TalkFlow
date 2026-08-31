# Phase 3 Known Limitations

This document captures the known limitations and unresolved issues at the end of Phase 3 (Model Selection Benchmark).

## 1. Accuracy Limitations
The frozen evaluation was conducted on a strictly-defined 37-sample regression set. The following issues were measured and remain unsolved:

- **Medicare**: 7/9
- **Part B**: 4/5
- **Humana**: 0/1
- **Aetna**: 0/1
- **TalkFlow**: 7/10
- **Medicaid Positives**: 0 samples

> [!WARNING]
> These issues **must remain visible** and **must NOT be described as solved**. The corpus is an engineering validation set, and we cannot claim production-grade statistical accuracy from it.

## 2. Medicaid Prompting Error
- **007.wav**: There was a manifest/category routing error affecting the prompt. Do NOT permanently classify this as a model failure or model success until the corrected prompt configuration is rerun on that WAV.
- We currently have **no measured positive-recall estimate** for Medicaid, as there were 0 valid positive samples in the set.

## 3. Performance Exception
- **Local RTX 2050 Latency**: `acoustic-end -> final P50` is currently measuring at **1002.9ms**.
- This is approximately **203ms above** the original Phase 3 target of <=800ms.
- While queue contention is fundamentally resolved via admission control and 2-worker scaling, the physical hardware limitations and `512ms` VAD grace period currently bottleneck the theoretical minimum.
