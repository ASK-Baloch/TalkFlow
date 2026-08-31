from __future__ import annotations
import logging
import os
import sys

if os.name == "nt":
    import site

    search_paths = set(sys.path + site.getsitepackages() + [site.getusersitepackages()])
    for path in search_paths:
        nvidia_path = os.path.join(path, "nvidia")
        if os.path.isdir(nvidia_path):
            for pkg in os.listdir(nvidia_path):
                bin_path = os.path.join(nvidia_path, pkg, "bin")
                if os.path.isdir(bin_path):
                    try:
                        os.add_dll_directory(bin_path)
                        os.environ["PATH"] = bin_path + os.pathsep + os.environ.get("PATH", "")
                    except Exception:
                        pass

import numpy as np
from faster_whisper import WhisperModel

from .provider import AsrDecodeResult, AsrProvider, AsrStream

logger = logging.getLogger("talkflow.asr.faster_whisper")


class FasterWhisperStream(AsrStream):
    def __init__(self, provider: FasterWhisperProvider, beam_size: int, context_hints: list[str] | None = None):
        self.provider = provider
        self.beam_size = beam_size
        self.context_hints = context_hints
        
        # Whisper doesn't have true RNN-T recurrent state, so we must buffer audio
        self._chunks = []
        
    def push_audio(self, audio: np.ndarray) -> None:
        if audio.size > 0:
            self._chunks.append(audio.copy())
            
    def get_partial(self) -> AsrDecodeResult:
        if not self._chunks:
            return AsrDecodeResult(text="", language="en", language_probability=1.0)
            
        audio = np.concatenate(self._chunks)
        return self.provider.transcribe(
            audio, 
            beam_size=self.beam_size, 
            context_hints=self.context_hints
        )
        
    def finalize(self) -> AsrDecodeResult:
        res = self.get_partial()
        self.close()
        return res
        
    def close(self) -> None:
        self._chunks.clear()


class FasterWhisperProvider(AsrProvider):
    def __init__(
        self,
        *,
        model_name: str,
        device: str,
        compute_type: str,
        language: str,
        condition_on_previous_text: bool,
        word_timestamps: bool,
        initial_prompt: str,
    ):
        self.language = language

        self.condition_on_previous_text = condition_on_previous_text

        self.word_timestamps = word_timestamps
        self.initial_prompt = initial_prompt

        import time
        import torch
        
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available.")
            
        logger.info(
            ("Loading Faster-Whisper model=%s device=%s (CUDA available=%s) compute_type=%s"),
            model_name,
            device,
            torch.cuda.is_available(),
            compute_type,
        )

        t0 = time.perf_counter_ns()
        self.model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
        )
        t1 = time.perf_counter_ns()
        load_time_ms = (t1 - t0) / 1_000_000

        logger.info("Faster-Whisper model ready in %.1fms (CTranslate2)", load_time_ms)
        
    def open_stream(self, *, beam_size: int, context_hints: list[str] | None = None) -> AsrStream:
        return FasterWhisperStream(self, beam_size, context_hints)

    def transcribe(
        self,
        audio: np.ndarray,
        *,
        beam_size: int,
        context_hints: list[str] | None = None,
    ) -> AsrDecodeResult:
        # Build initial prompt combining base prompt and hints
        prompt = self.initial_prompt
        if context_hints:
            hints_str = " ".join(context_hints)
            prompt = f"{prompt} {hints_str}".strip()
            
        segments, info = self.model.transcribe(
            audio,
            language=self.language,
            beam_size=beam_size,
            vad_filter=False,
            condition_on_previous_text=(self.condition_on_previous_text),
            word_timestamps=(self.word_timestamps),
            initial_prompt=(prompt),
        )

        # Important:
        # faster-whisper returns a lazy generator.
        segments = list(segments)

        text = " ".join(
            segment.text.strip() for segment in segments if segment.text.strip()
        ).strip()

        return AsrDecodeResult(
            text=text,
            language=getattr(
                info,
                "language",
                None,
            ),
            language_probability=getattr(
                info,
                "language_probability",
                None,
            ),
        )
