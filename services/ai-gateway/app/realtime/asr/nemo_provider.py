from __future__ import annotations

import logging

import numpy as np

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
        
        # Parakeet Unified EN 0.6B is not a cache-aware streaming model.
        # It does not maintain acoustic encoder state across calls.
        # We process the entire accumulated buffer on each partial request.
        return self.provider.transcribe(audio, beam_size=self.beam_size, context_hints=self.context_hints)
        
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
            # Change decoding strategy if needed
            from omegaconf import OmegaConf, open_dict
            
            if not hasattr(self, '_current_beam_size'):
                self._current_beam_size = None
                self._current_strategy = None
                
            if beam_size > 1:
                target_strategy = "beam"
            else:
                target_strategy = "greedy_batch"
                
            if self._current_beam_size != beam_size or self._current_strategy != target_strategy:
                cfg = OmegaConf.create(OmegaConf.to_container(self.model.cfg.decoding, resolve=True))
                
                if target_strategy == "beam":
                    cfg.strategy = "beam"
                    with open_dict(cfg):
                        if not hasattr(cfg, "beam"):
                            cfg.beam = OmegaConf.create({})
                        cfg.beam.beam_size = beam_size
                        cfg.preserve_word_confidence = True
                else:
                    cfg.strategy = "greedy_batch"
                    
                self.model.change_decoding_strategy(cfg)
                self._current_beam_size = beam_size
                self._current_strategy = target_strategy
            
            import hashlib
            cfg_yaml = OmegaConf.to_yaml(self.model.cfg.decoding)
            cfg_hash = hashlib.sha256(cfg_yaml.encode()).hexdigest()[:8]
            logger.info("Transcribe START: strategy=%s, beam=%s, config_hash=%s", self._current_strategy, self._current_beam_size, cfg_hash)
            
            results = self.model.transcribe(audio=audio, return_hypotheses=(beam_size > 1))
            
            logger.info("Transcribe END: strategy=%s, beam=%s, config_hash=%s", self._current_strategy, self._current_beam_size, cfg_hash)
            
            if not results:
                text_obj = ""
            else:
                text_obj = results
                # Recursively unwrap lists and tuples to get the first element
                while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0:
                    text_obj = text_obj[0]
                    
            if hasattr(text_obj, 'text'):
                if hasattr(text_obj, 'word_confidence'):
                    pass
                
                text_str = text_obj.text
            elif hasattr(text_obj, 'text_no_timesteps'):
                text_str = text_obj.text_no_timesteps
            else:
                text_str = str(text_obj)
                
            text_str = text_str.strip()
            
            return AsrDecodeResult(
                text=text_str,
                language="en", 
                language_probability=1.0,
            )
        except Exception as e:  # noqa: BLE001
            logger.error("Error transcribing with NeMo: %s", e)
            return AsrDecodeResult(text="", language="en", language_probability=1.0)

    def transcribe_chunk(
        self,
        audio: np.ndarray,
        *,
        partial_hypothesis=None,
    ):
        if audio.size == 0:
            return partial_hypothesis
            
        try:
            if partial_hypothesis is None:
                results = self.model.transcribe(audio=audio, return_hypotheses=True)
            else:
                results = self.model.transcribe(audio=audio, return_hypotheses=True, partial_hypothesis=partial_hypothesis)
            return results
        except Exception as e:  # noqa: BLE001
            logger.error("Error transcribing chunk with NeMo: %s", e)
            return partial_hypothesis
