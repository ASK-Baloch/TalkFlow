import asyncio
import itertools
from dataclasses import dataclass, field
from time import perf_counter_ns

import numpy as np

from .metrics import asr_metrics
from .types import (
    TranscriptEvent,
    TranscriptType,
)


@dataclass(order=True)
class AsrJob:
    priority: int

    sequence: int

    connection_id: str = field(compare=False)

    session_uuid: str | None = field(compare=False)

    utterance_id: str = field(compare=False)

    transcript_type: TranscriptType = field(compare=False)

    revision: int = field(compare=False)

    audio: np.ndarray = field(compare=False)

    beam_size: int = field(compare=False)
    
    stream: 'AsrStream' = field(compare=False, default=None)

    created_ns: int = field(
        default_factory=perf_counter_ns,
        compare=False,
    )
    
    worker_start_ns: int = field(default=0, compare=False)
    decode_start_ns: int = field(default=0, compare=False)
    decode_done_ns: int = field(default=0, compare=False)
    emit_ns: int = field(default=0, compare=False)
    acoustic_end_ns: int = field(default=0, compare=False)

class AsrScheduler:
    def __init__(
        self,
        *,
        provider,
        maxsize: int,
        workers: int = 1,
    ):
        self.provider = provider

        self.queue = asyncio.PriorityQueue(maxsize=maxsize)

        self.workers = workers

        self._tasks = []

        self._sequence = itertools.count()

        self.result_handler = None
        
        # Track pending partials per connection
        self._pending_partials = {}
        self._active_partials = 0
        self._queue_lock = asyncio.Lock()

    async def start(self):
        for index in range(self.workers):
            self._tasks.append(asyncio.create_task(self._worker_loop(index)))

    async def stop(self):
        for task in self._tasks:
            task.cancel()

        await asyncio.gather(
            *self._tasks,
            return_exceptions=True,
        )

        self._tasks.clear()

    async def submit(
        self,
        job,
    ) -> bool:
        async with self._queue_lock:
            if job.transcript_type == TranscriptType.PARTIAL:
                if self._active_partials >= 1:
                    asr_metrics.queue_overflows += 1
                    return False
                    
                # Coalesce: drop older pending partial for this connection
                conn = job.connection_id
                if conn in self._pending_partials:
                    old_job = self._pending_partials[conn]
                    # We can't easily remove from PriorityQueue, so we mark it stale
                    old_job.stale = True
                    asr_metrics.queue_overflows += 1
                    
                self._pending_partials[conn] = job
                self._active_partials += 1
                # Hardcode priority for partial
                job.priority = 10
            elif job.transcript_type == TranscriptType.FINAL_TENTATIVE:
                # Replace pending partial, but do NOT remove from pending_partials if we want to track it
                conn = job.connection_id
                if conn in self._pending_partials:
                    self._pending_partials[conn].stale = True
                    del self._pending_partials[conn]
                job.priority = 1
            else:
                # FINAL job
                # Cancel any pending partial
                conn = job.connection_id
                if conn in self._pending_partials:
                    self._pending_partials[conn].stale = True
                    del self._pending_partials[conn]
                    
                # Hardcode priority for final
                job.priority = 0

            if self.queue.full():
                if job.transcript_type == TranscriptType.PARTIAL:
                    asr_metrics.queue_overflows += 1
                    return False
                    
            job.stale = False
            await self.queue.put(job)

        asr_metrics.jobs_submitted += 1

        return True

    async def _worker_loop(
        self,
        worker_index: int,
    ):
        while True:
            job = await self.queue.get()
            
            if getattr(job, 'stale', False):
                if job.transcript_type == TranscriptType.PARTIAL:
                    async with self._queue_lock:
                        self._active_partials -= 1
                self.queue.task_done()
                continue
                
            async with self._queue_lock:
                if job.transcript_type == TranscriptType.PARTIAL:
                    # Remove from pending if it's the one we are processing
                    if self._pending_partials.get(job.connection_id) is job:
                        del self._pending_partials[job.connection_id]

            queue_wait_ms = (perf_counter_ns() - job.created_ns) / 1_000_000

            started = perf_counter_ns()

            try:
                job.worker_start_ns = perf_counter_ns()
                
                # Use the stateful stream if available, otherwise fallback to provider
                beam_size = job.beam_size
                    
                job.decode_start_ns = perf_counter_ns()
                
                if job.stream:
                    # Update stream beam_size if needed
                    job.stream.beam_size = beam_size
                    if job.transcript_type == TranscriptType.PARTIAL:
                        result = await asyncio.to_thread(job.stream.get_partial)
                    else:
                        job.stream.close()
                        result = await asyncio.to_thread(
                            self.provider.transcribe,
                            job.audio,
                            beam_size=beam_size,
                            context_hints=job.stream.context_hints
                        )
                else:
                    if job.transcript_type in (TranscriptType.FINAL, TranscriptType.FINAL_TENTATIVE):
                        import hashlib
                        import soundfile as sf
                        import numpy as np
                        
                        buffer_bytes = job.audio.tobytes()
                        buffer_hash = hashlib.sha256(buffer_bytes).hexdigest()
                        
                        logger.info("FINAL ASR FORENSIC: sample_count=%s, sample_rate=%s, duration=%.3fs, dtype=%s, peak=%.4f, RMS=%.4f, SHA256=%s",
                                    len(job.audio), 16000, len(job.audio)/16000, job.audio.dtype, 
                                    float(np.max(np.abs(job.audio))), float(np.sqrt(np.mean(job.audio**2))), buffer_hash)
                        
                        try:
                            sf.write(f"/app/test_set/FINAL-ASR-INPUT-{job.utterance_id}.wav", job.audio, 16000)
                            logger.info("FINAL ASR FORENSIC: Saved exact buffer to /app/test_set/FINAL-ASR-INPUT-%s.wav", job.utterance_id)
                        except Exception as e:
                            logger.error("FINAL ASR FORENSIC: Failed to save wav: %s", e)
                        
                        logger.info("FINAL ASR FORENSIC: Running LIVE Original Transcribe")
                        result = await asyncio.to_thread(
                            self.provider.transcribe,
                            job.audio,
                            beam_size=beam_size,
                        )
                        logger.info("FINAL ASR FORENSIC: LIVE ORIGINAL OUTPUT = '%s'", result.text if hasattr(result, 'text') else str(result))
                        
                        logger.info("FINAL ASR FORENSIC: Running REPLAY Transcribe")
                        replay_result = await asyncio.to_thread(
                            self.provider.transcribe,
                            job.audio,
                            beam_size=beam_size,
                        )
                        logger.info("FINAL ASR FORENSIC: IMMEDIATE REPLAY OUTPUT = '%s'", replay_result.text if hasattr(replay_result, 'text') else str(replay_result))
                    else:
                        result = await asyncio.to_thread(
                            self.provider.transcribe,
                            job.audio,
                            beam_size=beam_size,
                        )

                job.decode_done_ns = perf_counter_ns()
                decode_ms = (job.decode_done_ns - job.decode_start_ns) / 1_000_000
                
                from .normalization import get_domain_normalizer
                
                # We can retrieve context hints from stream if it's available
                context_hints = job.stream.context_hints if hasattr(job.stream, 'context_hints') else None
                
                norm_started = perf_counter_ns()
                normalizer = get_domain_normalizer()
                normalized_text, corrections = normalizer.normalize(result.text, context_hints=context_hints)
                norm_ms = (perf_counter_ns() - norm_started) / 1_000_000

                job.emit_ns = perf_counter_ns()

                event = TranscriptEvent.create(
                    connection_id=job.connection_id,
                    session_uuid=job.session_uuid,
                    utterance_id=job.utterance_id,
                    transcript_type=job.transcript_type,
                    raw_text=result.text,
                    normalized_text=normalized_text,
                    revision=job.revision,
                    audio_duration_ms=(job.audio.size / 16000 * 1000),
                    decode_ms=decode_ms,
                    queue_wait_ms=queue_wait_ms,
                    normalization_ms=norm_ms,
                )
                
                # Attach job timings to event for detailed logging
                event.job_created_ns = job.created_ns
                event.worker_start_ns = job.worker_start_ns
                event.decode_start_ns = job.decode_start_ns
                event.decode_done_ns = job.decode_done_ns
                event.emit_ns = job.emit_ns
                event.acoustic_end_ns = job.acoustic_end_ns

                if self.result_handler:
                    await self.result_handler(event)

            except Exception:
                asr_metrics.decode_errors += 1
                logger.exception("ASR worker error")

            finally:
                if job.transcript_type == TranscriptType.PARTIAL and not getattr(job, 'stale', False):
                    async with self._queue_lock:
                        self._active_partials -= 1
                self.queue.task_done()
