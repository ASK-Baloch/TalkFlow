# ruff: noqa
import os

import librosa
import numpy as np
import scipy.io.wavfile as wav
from omegaconf import OmegaConf, open_dict


def analyze_wav(path, name):
    print(f"\n=== AUDIO ANALYSIS: {name} ===")
    print(f"Path: {path}")
    
    if not os.path.exists(path):
        print("FILE NOT FOUND")
        return
        
    sr, data = wav.read(path)
    
    # Convert to float for analysis
    if data.dtype == np.int16:
        float_data = data.astype(np.float32) / 32768.0
    else:
        float_data = data
        
    duration = len(data) / sr
    samples = len(data)
    
    peak = np.max(np.abs(float_data))
    rms = np.sqrt(np.mean(float_data**2))
    dc_offset = np.mean(float_data)
    
    clipping_samples = np.sum(np.abs(data) >= 32767) if data.dtype == np.int16 else np.sum(np.abs(float_data) >= 1.0)
    clip_pct = (clipping_samples / samples) * 100
    
    # Simple silence detection
    non_silent = librosa.effects.split(float_data, top_db=40)
    if len(non_silent) > 0:
        leading_silence = non_silent[0][0] / sr
        trailing_silence = (samples - non_silent[-1][1]) / sr
    else:
        leading_silence = duration
        trailing_silence = 0
        
    # Approximate SNR (signal to noise)
    # Estimate noise from the first 100ms or leading silence
    noise_len = min(int(sr * 0.1), non_silent[0][0] if len(non_silent) > 0 else 100)
    if noise_len > 0:
        noise_rms = np.sqrt(np.mean(float_data[:noise_len]**2))
        if noise_rms > 0:
            snr = 20 * np.log10(rms / noise_rms)
        else:
            snr = float('inf')
    else:
        snr = 0.0

    print(f"Sample Rate: {sr} Hz")
    print(f"Duration: {duration:.3f} s")
    print(f"Samples: {samples}")
    print(f"Peak Amplitude: {peak:.4f}")
    print(f"RMS: {rms:.4f}")
    print(f"DC Offset: {dc_offset:.6f}")
    print(f"Clipping: {clipping_samples} samples ({clip_pct:.2f}%)")
    print(f"Leading Silence: {leading_silence:.3f} s")
    print(f"Trailing Silence: {trailing_silence:.3f} s")
    print(f"Approx SNR: {snr:.1f} dB")


def run_decoder_matrix(successful_path, failed_path):
    print("\n=== SAME-WAV DECODER MATRIX ===")
    
    try:
        import nemo.collections.asr as nemo_asr
    except ImportError:
        print("NeMo is not installed.")
        return
        
    print("Loading Parakeet Model...")
    model_path = "/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo"
    model = nemo_asr.models.EncDecRNNTBPEModel.restore_from(model_path)
    
    if getattr(model.cfg, "validation_ds", None) is None:
        model.cfg.validation_ds = OmegaConf.create({})
        
    import torch
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    
    default_cfg = OmegaConf.to_container(model.cfg.decoding, resolve=True)
    
    configs = [
        {"name": "greedy", "beam": 1, "strategy": "greedy_batch"},
        {"name": "fast_final", "beam": 1, "strategy": "greedy_batch"},
        {"name": "malsd_b2", "beam": 2, "strategy": "malsd_batch"},
        {"name": "malsd_b4", "beam": 4, "strategy": "malsd_batch"},
    ]
    
    wavs = [
        ("successful", successful_path),
        ("failed", failed_path)
    ]
    
    import time
    
    # Warmup
    print("Warming up models...")
    for label, path in wavs:
        if not os.path.exists(path): continue
        import soundfile as sf
        audio, _ = sf.read(path)
        for c in configs:
            cfg = OmegaConf.create(default_cfg)
            cfg.strategy = c["strategy"]
            if c["beam"] > 1:
                with open_dict(cfg):
                    if not hasattr(cfg, cfg.strategy):
                        setattr(cfg, cfg.strategy, OmegaConf.create({}))
                    getattr(cfg, cfg.strategy).beam_size = c["beam"]
            model.change_decoding_strategy(cfg)
            model.transcribe(audio=audio, return_hypotheses=(c["beam"] > 1))
            
    print("\nDecoder               Transcript            decode_ms")
    print("---------------------------------------------------------------------------")
    
    for label, path in wavs:
        if not os.path.exists(path): continue
        import soundfile as sf
        audio, _ = sf.read(path)
        
        for c in configs:
            cfg = OmegaConf.create(default_cfg)
            cfg.strategy = c["strategy"]
            if c["beam"] > 1:
                with open_dict(cfg):
                    if not hasattr(cfg, cfg.strategy):
                        setattr(cfg, cfg.strategy, OmegaConf.create({}))
                    getattr(cfg, cfg.strategy).beam_size = c["beam"]
            model.change_decoding_strategy(cfg)
            
            t0 = time.perf_counter_ns()
            transcripts = model.transcribe(audio=audio, return_hypotheses=(c["beam"] > 1))
            t1 = time.perf_counter_ns()
            
            decode_ms = (t1 - t0) / 1_000_000
            
            text_obj = transcripts
            while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0:
                text_obj = text_obj[0]
                
            if hasattr(text_obj, 'text'):
                text_str = text_obj.text
            elif hasattr(text_obj, 'text_no_timesteps'):
                text_str = text_obj.text_no_timesteps
            else:
                text_str = str(text_obj)
            
            print(f"{label:<20} {c['name']:<18} '{text_str.strip()}'\t{decode_ms:.1f}")

    print("\n=== REPEATABILITY TEST ===")
    if os.path.exists(failed_path):
        import soundfile as sf
        audio, _ = sf.read(failed_path)
        cfg = OmegaConf.create(default_cfg)
        cfg.strategy = "greedy_batch"
        model.change_decoding_strategy(cfg)
        
        for i in range(10):
            transcripts = model.transcribe(audio=audio, return_hypotheses=False)
            text_obj = transcripts
            while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0:
                text_obj = text_obj[0]
            if hasattr(text_obj, 'text'):
                text_str = text_obj.text
            elif hasattr(text_obj, 'text_no_timesteps'):
                text_str = text_obj.text_no_timesteps
            else:
                text_str = str(text_obj)
            print(f"Run {i+1}: '{text_str.strip()}'")


if __name__ == "__main__":
    failed_path = "/app/test_set/4d6522a1-2f31-4cb3-8c1f-5f2f3f720f09_16k.wav"
    successful_path = "/app/test_set/f2d62ee9-9ddc-4a9b-8f5c-36244f9088e2_16k.wav"
    
    analyze_wav(failed_path, "FAILED WAV")
    analyze_wav(successful_path, "SUCCESSFUL WAV")
    
    run_decoder_matrix(successful_path, failed_path)

