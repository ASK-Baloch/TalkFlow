from __future__ import annotations
import logging
import os
import tempfile
import numpy as np
import soundfile as sf

from .provider import AsrDecodeResult, AsrProvider, AsrStream

logger = logging.getLogger("talkflow.asr.nemo")


class NemoStream(AsrStream):
    def __init__(self, provider: NemoProvider, beam_size: int, context_hints: list[str] | None = None):
        self.provider = provider
        self.beam_size = beam_size
        self.context_hints = context_hints
        
        self.model = provider.model
        
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


class NemoProvider(AsrProvider):
    def __init__(self, *, model_path: str, device: str):
        self.device = device
        
        logger.info("Loading NeMo ASR model from %s on %s...", model_path, device)
        
        try:
            import nemo.collections.asr as nemo_asr
        except ImportError:
            raise ImportError(
                "nemo_toolkit[asr] is not installed. Please install it to use NemoProvider."
            )

        # Restore model from .nemo file
        self.model = nemo_asr.models.EncDecRNNTBPEModel.restore_from(model_path)
        
        # Parakeet checkpoints sometimes lack validation_ds, which crashes the transcribe dataloader
        from omegaconf import OmegaConf
        if getattr(self.model.cfg, "validation_ds", None) is None:
            self.model.cfg.validation_ds = OmegaConf.create({})
        
        if device == "cuda":
            import torch
            if torch.cuda.is_available():
                self.model = self.model.cuda()
            else:
                logger.warning("CUDA requested but not available. Falling back to CPU.")
                self.model = self.model.cpu()
        else:
            self.model = self.model.cpu()
            
        self.model.eval()
        
        logger.info("NeMo ASR model ready")

    def open_stream(self, *, beam_size: int, context_hints: list[str] | None = None) -> AsrStream:
        return NemoStream(self, beam_size, context_hints)

    def transcribe(
        self,
        audio: np.ndarray,
        *,
        beam_size: int,
        context_hints: list[str] | None = None,
    ) -> AsrDecodeResult:
        if audio.size == 0:
            return AsrDecodeResult(text="", language="en", language_probability=1.0)
            
        try:
            duration = len(audio) / 16000.0
            rms = np.sqrt(np.mean(audio**2)) if len(audio) > 0 else 0
            
            logger.info(
                f"ASR INPUT\n"
                f"samples={len(audio)}\n"
                f"duration={duration:.3f}\n"
                f"sample_rate=16000\n"
                f"dtype={audio.dtype}\n"
                f"min={np.min(audio):.4f}\n"
                f"max={np.max(audio):.4f}\n"
                f"mean={np.mean(audio):.4f}\n"
                f"rms={rms:.4f}"
            )
            
            # Save exactly one ASR input WAV for debugging (override each time)
            try:
                import soundfile as sf
                sf.write("/app/debug/asr_input.wav", audio, 16000, subtype='PCM_16')
            except Exception as e:
                logger.warning("Failed to write debug/asr_input.wav: %s", e)
                
            # Pass the numpy array directly to avoid WAV IO overhead!
            results = self.model.transcribe(audio=audio)
            
            if not results:
                text = ""
            else:
                if isinstance(results, tuple) and len(results) > 0:
                    transcripts = results[0]
                else:
                    transcripts = results
                    
                if isinstance(transcripts, list) and len(transcripts) > 0:
                    text = transcripts[0]
                else:
                    text = transcripts
                    
            if hasattr(text, 'text'):
                text = text.text
            elif hasattr(text, 'text_no_timesteps'):
                text = text.text_no_timesteps
            else:
                text = str(text)
                
            text = text.strip()
            
            return AsrDecodeResult(
                text=text,
                language="en", 
                language_probability=1.0,
            )
        except Exception as e:
            logger.error("Error transcribing with NeMo: %s", e)
            return AsrDecodeResult(text="", language="en", language_probability=1.0)
