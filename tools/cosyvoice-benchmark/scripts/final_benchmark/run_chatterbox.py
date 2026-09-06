import os
import sys
import time
import json
import traceback
from pathlib import Path
import numpy as np

# Add project root to sys path to resolve imports
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "services" / "ai-gateway"))

from chatterbox.tts_turbo import ChatterboxTurboTTS
sys.path.insert(0, str(ROOT / "tools" / "cosyvoice-benchmark" / "scripts" / "final_benchmark"))
from shared import (
    SENTENCES, WARMUP_TEXT, TRIALS, get_vram_usage, validate_audio
)

def run_chatterbox(output_dir: Path, ref_audio: Path):
    print("Loading Chatterbox Turbo...")
    t0 = time.perf_counter()
    model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    load_time = time.perf_counter() - t0
    
    idle_vram = get_vram_usage()
    print(f"Loaded in {load_time:.2f}s. Idle VRAM: {idle_vram:.2f} MB")
    
    # Warmup
    print("Running warmup...")
    t0_warmup = time.perf_counter()
    warmup_samples = model.generate(WARMUP_TEXT, audio_prompt_path=str(ref_audio))
    warmup_time = time.perf_counter() - t0_warmup
    warmup_pcm = (np.asarray(warmup_samples, dtype=np.float32).reshape(-1) * 32767.0).astype(np.int16).tobytes()
    sample_rate = getattr(model, "sr", 24000)
    is_valid, dur, rms, peak, reason = validate_audio(warmup_pcm, sample_rate, 2)
    print(f"Warmup time: {warmup_time:.2f}s, Valid: {is_valid} ({reason})")
    
    idle_vram_after_warmup = get_vram_usage()
    
    results = {
        "model": "Chatterbox Turbo",
        "load_time": load_time,
        "idle_vram": idle_vram,
        "warmup_time": warmup_time,
        "warmup_valid": is_valid,
        "idle_vram_after_warmup": idle_vram_after_warmup,
        "trials": []
    }
    
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    import wave
    
    for sentence in SENTENCES:
        print(f"Testing {sentence['id']}...")
        
        sentence_metrics = []
        best_pcm = None
        best_dur = 0
        
        for trial in range(TRIALS):
            vram_before = get_vram_usage()
            t_start = time.perf_counter()
            
            error_type = ""
            error_message = ""
            ttfa = 0.0
            generation_time = 0.0
            
            try:
                # We assume model.generate returns entire waveform for Chatterbox, TTFA=N/A
                # unless it returns a generator. Let's check type.
                gen_result = model.generate(sentence["text"], audio_prompt_path=str(ref_audio))
                generation_time = time.perf_counter() - t_start
                
                pcm = (np.asarray(gen_result, dtype=np.float32).reshape(-1) * 32767.0).astype(np.int16).tobytes()
                vram_peak = get_vram_usage() # Approximate
                
                is_valid, dur, rms, peak, reason = validate_audio(pcm, sample_rate, 2)
                
                if not is_valid:
                    error_type = reason
                else:
                    if best_pcm is None:
                        best_pcm = pcm
                        best_dur = dur
                        
            except Exception as e:
                generation_time = time.perf_counter() - t_start
                error_type = "GENERATION_ERROR"
                error_message = str(e)
                is_valid = False
                dur = 0.0
                rms = 0.0
                peak = 0.0
                pcm = b""
                
            vram_after = get_vram_usage()
            
            trial_data = {
                "model": "Chatterbox Turbo",
                "sentence_id": sentence["id"],
                "category": sentence["category"],
                "trial_number": trial + 1,
                "retry_number": 0,
                "status": "VALID" if is_valid else error_type,
                "text": sentence["text"],
                "generation_time": generation_time,
                "TTFA": None,
                "TTFA_measurement_method": "N/A (non-streaming measurement)",
                "audio_duration": dur,
                "RTF": (generation_time / (dur/1000.0)) if dur > 0 else 0,
                "output_sample_rate": sample_rate,
                "channels": 1,
                "RMS": rms,
                "peak": peak,
                "file_size": len(pcm),
                "VRAM_before": vram_before,
                "VRAM_peak": vram_peak if 'vram_peak' in locals() else vram_before,
                "VRAM_after": vram_after,
                "process_RAM": 0.0,
                "error_type": error_type,
                "error_message": error_message
            }
            results["trials"].append(trial_data)
            sentence_metrics.append(trial_data)
            
        if best_pcm:
            wav_path = audio_dir / f"{sentence['id']}.wav"
            with wave.open(str(wav_path), "wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(sample_rate)
                wav.writeframes(best_pcm)
                
    with open(output_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    ref_audio = Path(sys.argv[2])
    run_chatterbox(out_dir, ref_audio)
