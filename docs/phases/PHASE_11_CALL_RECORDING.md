# Phase 11: Call Recording

## Goal
To securely and reliably capture, validate, and store full-duplex call audio without impacting the real-time AI conversation flow.

## Architecture
Call recording is separated into two decoupled domains:
1. **Synchronous Capture (Asterisk Edge):** Asterisk `MixMonitor` captures the live audio streams and saves them to local disk as a WAV file.
2. **Asynchronous Processing (Recording Worker):** A standalone worker service pulls the file, validates it, and stores it in long-term storage.

### MixMonitor Decision
We chose to rely on Asterisk's native `MixMonitor` rather than attempting to duplicate, sync, and mix AudioSocket frames inside the `ai-gateway`. This decision completely isolates the AI gateway from the responsibility of stream alignment and provides a robust backup in case the AI services crash.

### Safe UUID Naming
Recordings are named strictly using the Call UUID (`<uuid>.wav`). This prevents naming collisions and simplifies tracking across systems. It also allows standardizing SFTP paths and long-term storage bucket keys.

### Directory Permissions
Asterisk writes files to `/var/spool/asterisk/monitor/talkflow`. This directory is exposed over SFTP using the `talkflow_recordings` user, which is configured with **read-only** access. This prevents a compromised worker from mutating or deleting files on the telephony edge.

### Asterisk Changes
Asterisk dialplan (`extensions.conf`) was updated to start `MixMonitor` just before connecting the channel to AudioSocket.

### Async Event Flow
1. Call ends.
2. `ai-gateway` publishes a `call_id` and `ended_at` payload to the `talkflow.recording.requests.v1` Kafka topic.
3. `recording-worker` consumes the event.
4. Worker transitions DB status to `WAITING_FOR_SOURCE`.
5. Worker polls SFTP until the Asterisk `.wav` file is fully flushed and size-stable.

### Kafka Topics
- `talkflow.recording.requests.v1`: Used for enqueueing the final processing request for a completed call.

### SFTP Design
The recording worker uses `asyncssh` to poll and securely transfer files over SFTP from the remote Asterisk host. 

### Host Verification
The worker strictly verifies the remote Asterisk server using an `asterisk_known_hosts` secret file to prevent man-in-the-middle (MITM) attacks.

### Storage Abstraction
A `StorageProvider` protocol allows saving the validated recording locally or remotely. The provider is determined via environment variables.

### Local Storage
For development and simple deployments, local storage writes to `storage/recordings/` inside the container/host path.

### S3 Production Option
An S3 storage adapter allows pushing the validated `.wav` file into AWS S3 (or any S3-compatible service) for highly durable long-term storage in production.

### PostgreSQL Table
A dedicated `call_recordings` table stores:
- `call_id` (Primary Key)
- `status` (Enum: WAITING_FOR_SOURCE, FETCHING, VALIDATING, STORING, READY, FAILED)
- `storage_provider`, `storage_key`
- `size_bytes`, `duration_ms`
- `sample_rate`, `channels`
- `sha256` checksum

### Lifecycle Statuses
1. `WAITING_FOR_SOURCE`: Polling Asterisk for file stability.
2. `FETCHING`: Downloading over SFTP.
3. `VALIDATING`: Verifying headers, size, and calculating checksum.
4. `STORING`: Pushing to the long-term storage provider.
5. `READY`: Complete.
6. `FAILED`: Terminal failure.

### Checksum Validation
An SHA-256 checksum is calculated during validation and stored in the database. This guarantees file integrity for auditing and downstream consumers.

### Retries & Idempotency
- Kafka events can be replayed safely.
- Files are downloaded to a unique `/tmp` directory.
- `FAILED` statuses allow for manual intervention or cron-based retries.
- Asterisk files are not deleted until the status is successfully marked as `READY`.

### Retention Policy
The `recording-worker` has permissions to optionally delete the source file on the Asterisk server *only after* a successful upload, preventing Asterisk's disk from filling up. (Currently omitted until outbox is added).

### Security
- SFTP read-only user (`talkflow_recordings`).
- `asterisk_known_hosts` and `asterisk_recording_key` are managed via Docker secrets.
- Encrypted SSH private key requires passphrase (`ASTERISK_SFTP_PASSPHRASE`).
- Cryptographic hashing (SHA-256) of audio files.

### Failure Isolation
If the `recording-worker`, Kafka, PostgreSQL, or Local Storage fail, it has **zero impact** on live calls. Asterisk continues writing the files locally to its spool, preserving the raw data.

### Metrics
Worker timing, file size, duration, and status transitions can easily be aggregated via SQL.

### Tests
- Offline worker test.
- Offline Kafka test.
- Missing UUID test (timeout -> FAILED).
- Corrupt file test (Permission denied over SFTP, or validation failure -> FAILED).

### Live Call Validation
Tested in production-like conditions: MixMonitor successfully records the user and bot simultaneously, creating a perfectly mixed WAV file of the conversation.

### Definition of Done
- Asterisk natively records via MixMonitor.
- Async `recording-worker` implemented.
- Secure SFTP transfer configured.
- Validates headers and checks sizes.
- PostgreSQL schema tracks lifecycle.
- Zero impact to live call latency.
- Resiliency verified through fault-injection testing.
