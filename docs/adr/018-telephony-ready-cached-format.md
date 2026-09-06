# 18. Telephony-ready cached format

Date: 2026-09-07

## Status

Accepted

## Decision

Pre-generated responses are stored as 8 kHz mono signed PCM16 little-endian so no runtime audio conversion is required before AudioSocket playback.

## Reason

```text
Kokoro
 ↓ once
HQ resampling
 ↓ once
8k PCM

runtime
 ↓
copy bytes
 ↓
AudioSocket
```
