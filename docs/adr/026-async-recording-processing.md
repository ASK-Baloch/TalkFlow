# 26. Async Recording Processing

Date: 2026-09-13

## Status
Accepted

## Context
Once a call ends and the Asterisk server finishes flushing the mixed `.wav` file to its local disk, the file needs to be pulled, validated, and pushed to long-term storage. 

## Decision
The live call records locally on Asterisk. File transfer, validation, hashing, persistence and long-term storage are **asynchronous** operations performed outside the realtime gateway. A dedicated, standalone `recording-worker` consumes completion events from Kafka and handles this pipeline.

## Consequences

### Positive
- **No latency impact:** Pulling a potentially large WAV file over SFTP and uploading it to S3 takes seconds. This does not block or delay the gateway's ability to handle new incoming calls.
- **Resilience to downstream failures:** If S3 is down, Kafka is down, PostgreSQL is down, or the worker crashes, the live calls remain completely unaffected. The source file safely persists on the Asterisk server.
- **Scalability:** The recording processing can be scaled horizontally and independently from the real-time AI audio processing.

### Negative
- Introduces eventual consistency (e.g., a dashboard will say "WAITING_FOR_SOURCE" for a brief period before "READY").
- Requires deploying and monitoring an additional background worker container.
