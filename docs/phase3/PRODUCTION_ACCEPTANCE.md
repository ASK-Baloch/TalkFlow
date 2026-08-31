# Production Acceptance Requirements

This document outlines the strict production requirements for deploying the Phase 3 frozen ASR architecture into a production environment. 

> [!WARNING]
> Do **NOT** extrapolate the Phase 3 local RTX 2050 measurements to production hardware. Production hardware must be independently benchmarked before launch.

## 1. Corpus Expansion
Production acceptance must include a substantially larger real telephone corpus. The 37-sample subset used in Phase 3 is exclusively for regression and architecture validation, and does not provide statistical confidence for production.

## 2. Mandatory Production Measurements
The following metrics **must** be explicitly measured on the target production hardware and deployment environment prior to launch:

- **Critical-field accuracy:** E.g., Medicare vs Medicaid, ZIP codes, names, Part A/B correctly transcribed.
- **Latency:** True `acoustic-end -> final` P50 and P95 latency distributions.
- **Concurrency & Throughput:** Sustained performance under simultaneous live calls.
- **Hardware Utilization:**
  - GPU Utilization
  - VRAM Consumption (especially under concurrent worker load)
