from __future__ import annotations

import uuid
from time import perf_counter_ns

from .audio import (
    StreamingResampler,
    pcm16le_to_float32,
)
from .buffer import (
    AudioRingBuffer,
    UtteranceBuffer,
)


class AsrSession:
    def __init__(
        self,
        *,
        connection_id: str,
        input_sample_rate: int,
        sample_rate: int,
        pre_roll_ms: int,
    ):
        self.connection_id = connection_id

        self.session_uuid = None

        self.sample_rate = sample_rate

        self.resampler = StreamingResampler(
            input_rate=input_sample_rate,
            output_rate=sample_rate,
        )

        self.pre_roll = AudioRingBuffer(
            sample_rate=sample_rate,
            max_ms=pre_roll_ms,
        )

        self.utterance = UtteranceBuffer()

        self.utterance_id = None

        self.revision = 0
        self.finalized = False

        self.speaking = False

        self.partial_inflight = False
        self.first_partial_emitted = False

        self.last_partial_audio_ms = 0.0

        self.speech_start_ns = None
        self.speech_end_ns = None
        
        self.asr_stream = None

    def process_pcm(
        self,
        payload: bytes,
    ):
        audio8 = pcm16le_to_float32(payload)

        audio16 = self.resampler.process(audio8)

        if not self.speaking:
            self.pre_roll.append(audio16)
        else:
            self.utterance.append(audio16)
            if self.asr_stream:
                self.asr_stream.push_audio(audio16)

    def start_utterance(self, asr_stream=None):
        self.speaking = True

        self.utterance_id = str(uuid.uuid4())

        self.revision = 0
        self.finalized = False

        self.partial_inflight = False
        self.first_partial_emitted = False

        self.last_partial_audio_ms = 0.0

        self.speech_start_ns = perf_counter_ns()

        self.utterance.clear()
        
        # Capture pre-roll and push it to the new stream
        pre_roll_audio = self.pre_roll.snapshot()
        self.utterance.append(pre_roll_audio)
        
        self.asr_stream = asr_stream
        if self.asr_stream and pre_roll_audio.size > 0:
            self.asr_stream.push_audio(pre_roll_audio)

    def finish_utterance(self):
        self.speaking = False

        self.speech_end_ns = perf_counter_ns()

    def reset_utterance(self):
        self.utterance.clear()

        self.pre_roll.clear()

        self.utterance_id = None

        self.revision = 0
        self.finalized = False

        self.partial_inflight = False
        self.first_partial_emitted = False

        self.speech_start_ns = None
        self.speech_end_ns = None
        
        if self.asr_stream:
            try:
                self.asr_stream.close()
            except Exception:
                pass
            self.asr_stream = None
