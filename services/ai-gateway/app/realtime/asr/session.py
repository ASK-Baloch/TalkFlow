from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from time import perf_counter_ns

from .audio import (
    StreamingResampler,
    pcm16le_to_float32,
)
from .buffer import (
    AudioRingBuffer,
    UtteranceBuffer,
)
from .types import TranscriptEvent


@dataclass
class UtteranceState:
    utterance_id: str
    revision: int = 0
    finalized: bool = False
    tentative_inflight: bool = False
    tentative_result: TranscriptEvent | None = None
    final_emitted: bool = False
    cancelled: bool = False
    created_ns: int = field(default_factory=perf_counter_ns)
    speech_start_ns: int | None = None
    speech_end_ns: int | None = None
    acoustic_end_ns: int | None = None
    partial_inflight: bool = False
    first_partial_emitted: bool = False
    last_partial_audio_ms: float = 0.0


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
        self.input_sample_rate = input_sample_rate

        self.resampler = StreamingResampler(
            input_rate=input_sample_rate,
            output_rate=sample_rate,
        )

        self.pre_roll = AudioRingBuffer(
            sample_rate=sample_rate,
            max_ms=pre_roll_ms,
        )

        self.utterance = UtteranceBuffer()
        
        self.pre_roll_8k = AudioRingBuffer(
            sample_rate=input_sample_rate,
            max_ms=pre_roll_ms,
        )
        
        self.utterance_8k = UtteranceBuffer()

        self.active_utterance_id: str | None = None
        self.utterances: dict[str, UtteranceState] = {}
        
        self.speaking = False
        
        self.asr_stream = None
        self.context_hints: list[str] = []

    def set_context_hints(self, hints: list[str]) -> None:
        """Dynamically update contextual phrases for the active or next ASR stream."""
        self.context_hints = hints
        if self.asr_stream:
            self.asr_stream.context_hints = hints

    def process_pcm(
        self,
        payload: bytes,
    ):
        audio8 = pcm16le_to_float32(payload)

        audio16 = self.resampler.process(audio8)

        if not self.speaking:
            self.pre_roll.append(audio16)
            self.pre_roll_8k.append(audio8)
        else:
            self.utterance.append(audio16)
            self.utterance_8k.append(audio8)
            if self.asr_stream:
                self.asr_stream.push_audio(audio16)

    def start_utterance(self, asr_stream=None):
        self.speaking = True

        new_id = str(uuid.uuid4())
        self.active_utterance_id = new_id
        
        # Cleanup: Keep only last 10 completed utterances to prevent unbounded memory
        completed = [u for u in self.utterances.values() if u.final_emitted or u.cancelled]
        if len(completed) > 10:
            completed.sort(key=lambda u: u.created_ns)
            for old_u in completed[:-10]:
                del self.utterances[old_u.utterance_id]

        new_utterance = UtteranceState(
            utterance_id=new_id,
            speech_start_ns=perf_counter_ns()
        )
        self.utterances[new_id] = new_utterance

        self.utterance.clear()
        self.utterance_8k.clear()
        
        # Capture pre-roll and push it to the new stream
        pre_roll_audio = self.pre_roll.snapshot()
        self.utterance.append(pre_roll_audio)
        
        pre_roll_audio_8k = self.pre_roll_8k.snapshot()
        self.utterance_8k.append(pre_roll_audio_8k)
        
        self.asr_stream = asr_stream
        if self.asr_stream and pre_roll_audio.size > 0:
            self.asr_stream.push_audio(pre_roll_audio)

    def finish_utterance(self):
        self.speaking = False

        if self.active_utterance_id and self.active_utterance_id in self.utterances:
            active = self.utterances[self.active_utterance_id]
            active.speech_end_ns = perf_counter_ns()
            
        import os

        import soundfile as sf
        os.makedirs("/app/test_set", exist_ok=True)
        if self.active_utterance_id:
            try:
                sf.write(f"/app/test_set/{self.active_utterance_id}_8k.wav", self.utterance_8k.snapshot(), self.input_sample_rate)
                sf.write(f"/app/test_set/{self.active_utterance_id}_16k.wav", self.utterance.snapshot(), self.sample_rate)
            except OSError as e:
                print(f"Failed to save audio for utterance {self.active_utterance_id}: {e}")

    def reset_utterance(self):
        self.utterance.clear()
        self.utterance_8k.clear()

        self.pre_roll.clear()
        self.pre_roll_8k.clear()

        self.active_utterance_id = None
        self.speaking = False
        
        if self.asr_stream:
            try:
                self.asr_stream.close()
            except Exception as e:  # noqa: BLE001
                print(f"Error closing asr stream: {e}")
            self.asr_stream = None

    def get_utterance(self, utterance_id: str) -> UtteranceState | None:
        return self.utterances.get(utterance_id)
