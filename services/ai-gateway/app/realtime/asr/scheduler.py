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
        if self.queue.full():
            if job.transcript_type == TranscriptType.PARTIAL:
                asr_metrics.queue_overflows += 1
                return False

        await self.queue.put(job)

        asr_metrics.jobs_submitted += 1

        return True

    async def _worker_loop(
        self,
        worker_index: int,
    ):
        while True:
            job = await self.queue.get()

            queue_wait_ms = (perf_counter_ns() - job.created_ns) / 1_000_000

            started = perf_counter_ns()

            try:
                # Use the stateful stream if available, otherwise fallback to provider
                if job.stream:
                    if job.transcript_type == TranscriptType.PARTIAL:
                        result = await asyncio.to_thread(job.stream.get_partial)
                    else:
                        result = await asyncio.to_thread(job.stream.finalize)
                else:
                    result = await asyncio.to_thread(
                        self.provider.transcribe,
                        job.audio,
                        beam_size=job.beam_size,
                    )

                decode_ms = (perf_counter_ns() - started) / 1_000_000
                
                from .normalization import get_domain_normalizer
                
                # We can retrieve context hints from stream if it's available
                context_hints = job.stream.context_hints if hasattr(job.stream, 'context_hints') else None
                
                norm_started = perf_counter_ns()
                normalizer = get_domain_normalizer()
                normalized_text, corrections = normalizer.normalize(result.text, context_hints=context_hints)
                norm_ms = (perf_counter_ns() - norm_started) / 1_000_000

                event = TranscriptEvent.create(
                    connection_id=job.connection_id,
                    session_uuid=job.session_uuid,
                    utterance_id=job.utterance_id,
                    transcript_type=job.transcript_type,
                    text=normalized_text,
                    revision=job.revision,
                    audio_duration_ms=(job.audio.size / 16000 * 1000),
                    decode_ms=decode_ms,
                    queue_wait_ms=queue_wait_ms,
                    normalization_ms=norm_ms,
                )

                if self.result_handler:
                    await self.result_handler(event)

            except Exception:
                asr_metrics.decode_errors += 1
                logger.exception("ASR worker error")

            finally:
                self.queue.task_done()
