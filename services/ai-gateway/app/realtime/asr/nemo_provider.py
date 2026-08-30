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
        self._partial_hyp = None
        self._accumulated_text = ""
        
        # Target ~320ms chunks (16000 * 0.320 = 5120 samples)
        self._chunk_samples = 5120
        
    def push_audio(self, audio: np.ndarray) -> None:
        if audio.size > 0:
            self._chunks.append(audio.copy())
            
    def get_partial(self) -> AsrDecodeResult:
        if not self._chunks:
            text = self._accumulated_text
            if self._partial_hyp:
                hyp = self._partial_hyp[0] if isinstance(self._partial_hyp, tuple) else self._partial_hyp
                if isinstance(hyp, list) and len(hyp) > 0:
                    text = (text + " " + hyp[0].text).strip()
            return AsrDecodeResult(text=text, language="en", language_probability=1.0)
            
        audio = np.concatenate(self._chunks)
        
        while len(audio) >= self._chunk_samples:
            chunk = audio[:self._chunk_samples]
            audio = audio[self._chunk_samples:]
            
            # Process the chunk with the current partial hypothesis state
            self._partial_hyp = self.provider.transcribe_chunk(
                chunk,
                partial_hypothesis=self._partial_hyp
            )
            
        # Save remaining audio
        self._chunks = [audio] if audio.size > 0 else []
        
        # Get the current text
        text = self._accumulated_text
        if self._partial_hyp:
            hyp = self._partial_hyp[0] if isinstance(self._partial_hyp, tuple) else self._partial_hyp
            if isinstance(hyp, list) and len(hyp) > 0:
                text = (text + " " + hyp[0].text).strip()
                
        return AsrDecodeResult(
            text=text, 
            language="en", 
            language_probability=1.0
        )
        
    def finalize(self) -> AsrDecodeResult:
        # Process any remaining audio smaller than chunk_samples
        if self._chunks:
            audio = np.concatenate(self._chunks)
            if len(audio) > 0:
                self._partial_hyp = self.provider.transcribe_chunk(
                    audio,
                    partial_hypothesis=self._partial_hyp
                )
        
        res = self.get_partial()
        self.close()
        return res
        
    def close(self) -> None:
        self._chunks.clear()
        self._partial_hyp = None


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
        boost_enabled = os.getenv("ASR_PHRASE_BOOST_ENABLED", "true").lower() == "true"
        
        if boost_enabled and context_hints and len(context_hints) > 0:
            boost_score = float(os.getenv("ASR_PHRASE_BOOST_SCORE", "10.0"))
            try:
                import copy
                from omegaconf import open_dict
                
                # Clone default cfg to preserve native pad/blank IDs
                cfg = copy.deepcopy(self.model.cfg.decoding)
                with open_dict(cfg):
                    strategy = cfg.strategy
                    if not hasattr(cfg, strategy):
                        setattr(cfg, strategy, {})
                    
                    strategy_cfg = getattr(cfg, strategy)
                    strategy_cfg.word_vocab = context_hints
                    strategy_cfg.word_score = boost_score
                    
                self.model.change_decoding_strategy(cfg)
                logger.info("ASR phrase boosting ACTIVE for %d contexts (score=%.1f)", len(context_hints), boost_score)
            except Exception as e:
                logger.error("Failed to apply RNNT phrase boosting: %s", e)
                raise RuntimeError(f"Phrase boosting initialization failed: {e}") from e
        else:
            try:
                # Reset to raw strategy if no hints exist
                self.model.change_decoding_strategy(self.model.cfg.decoding)
            except Exception:
                pass
                
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
        except Exception as e:
            logger.error("Error transcribing chunk with NeMo: %s", e)
            return partial_hypothesis
