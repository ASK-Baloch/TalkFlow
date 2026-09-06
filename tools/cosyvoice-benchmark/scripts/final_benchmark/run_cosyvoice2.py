import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools" / "cosyvoice-benchmark" / "CosyVoice"))
sys.path.insert(0, str(ROOT / "tools" / "cosyvoice-benchmark" / "CosyVoice" / "third_party" / "Matcha-TTS"))
from cosyvoice.cli.cosyvoice import CosyVoice2

sys.path.insert(0, str(ROOT / "tools" / "cosyvoice-benchmark" / "scripts" / "final_benchmark"))
from shared import SENTENCES, TRIALS, WARMUP_TEXT, get_vram_usage, validate_audio


def run_cosyvoice2(output_dir: Path, ref_audio: Path, transcript: str):
    print("Loading CosyVoice 2...")
    model_dir = ROOT / "tools" / "cosyvoice-benchmark" / "models" / "CosyVoice2-0.5B"
    
    t0 = time.perf_counter()
    model = CosyVoice2(str(model_dir))
    load_time = time.perf_counter() - t0
    
    idle_vram = get_vram_usage()
    print(f"Loaded in {load_time:.2f}s. Idle VRAM: {idle_vram:.2f} MB")
    
    ref_transcript = transcript.strip()
    
    print(f"Using reference transcript: {ref_transcript}")
    
    # Warmup
    print("Running warmup...")
    t0_warmup = time.perf_counter()
    for _ in model.inference_zero_shot(WARMUP_TEXT, ref_transcript, str(ref_audio), stream=False):
        pass
    warmup_time = time.perf_counter() - t0_warmup
    idle_vram_after_warmup = get_vram_usage()
    
    results = {
        "model": "CosyVoice 2",
        "load_time": load_time,
        "idle_vram": idle_vram,
        "warmup_time": warmup_time,
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
        best_ttfa_diff = float("inf")
        median_ttfa = 0
        
        for trial in range(TRIALS):
            trial_data = run_trial(model, sentence, ref_transcript, ref_audio, trial + 1, 0)
            
            if trial_data["status"] in ["EMPTY_OUTPUT", "SILENT_OUTPUT", "CORRUPT_OUTPUT"]:
                print(f"Trial {trial+1} failed with {trial_data['status']}. Retrying once...")
                results["trials"].append(trial_data) # Log failure
                trial_data = run_trial(model, sentence, ref_transcript, ref_audio, trial + 1, 1) # Retry
                
            results["trials"].append(trial_data)
                
            if trial_data["status"] == "VALID":
                sentence_metrics.append(trial_data)
                
        # Pick the median TTFA trial as representative listening sample
        if sentence_metrics:
            ttfas = [m["TTFA"] for m in sentence_metrics if m["TTFA"] is not None]
            if ttfas:
                median_ttfa = np.median(ttfas)
                best_metric = min(sentence_metrics, key=lambda x: abs(x["TTFA"] - median_ttfa))
            else:
                best_metric = sentence_metrics[0]
                
            best_pcm = best_metric.pop("_pcm", None)
            if best_pcm:
                wav_path = audio_dir / f"{sentence['id']}.wav"
                with wave.open(str(wav_path), "wb") as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(22050)
                    wav.writeframes(best_pcm)
                    
        # Remove _pcm from all trials before dumping JSON
        for t in results["trials"]:
            t.pop("_pcm", None)
    
    with open(output_dir / "metrics.json", "w") as f:
        json.dump(results, f, indent=2)

def run_trial(model, sentence, ref_transcript, ref_audio, trial_num, retry_num):
    vram_before = get_vram_usage()
    t_start = time.perf_counter()
    ttfa = None
    first_chunk_size = 0
    first_chunk_dur = 0
    
    pcm_chunks = []
    error_type = ""
    error_message = ""
    
    try:
        generator = model.inference_zero_shot(sentence["text"], ref_transcript, str(ref_audio), stream=True)
        for chunk in generator:
            if ttfa is None:
                ttfa = (time.perf_counter() - t_start) * 1000.0
                first_chunk_size = len(chunk['tts_speech']) if isinstance(chunk, dict) else chunk.shape[1]
                first_chunk_dur = (first_chunk_size / 22050) * 1000.0
                
            chunk_tensor = chunk['tts_speech'] if isinstance(chunk, dict) else chunk
            pcm_chunk = (chunk_tensor.numpy().reshape(-1) * 32767.0).astype(np.int16).tobytes()
            pcm_chunks.append(pcm_chunk)
            
        generation_time = time.perf_counter() - t_start
        full_pcm = b"".join(pcm_chunks)
        
        is_valid, dur, rms, peak, reason = validate_audio(full_pcm, 22050, 2)
        if not is_valid:
            error_type = reason
            
    except Exception as e:
        generation_time = time.perf_counter() - t_start
        error_type = "GENERATION_ERROR"
        error_message = str(e)
        is_valid = False
        dur = 0.0
        rms = 0.0
        peak = 0.0
        full_pcm = b""
        
    vram_after = get_vram_usage()
    
    return {
        "model": "CosyVoice 2",
        "sentence_id": sentence["id"],
        "category": sentence["category"],
        "trial_number": trial_num,
        "retry_number": retry_num,
        "status": "VALID" if is_valid else error_type,
        "text": sentence["text"],
        "generation_time": generation_time,
        "TTFA": ttfa,
        "TTFA_measurement_method": "First streaming chunk yielded",
        "audio_duration": dur,
        "RTF": (generation_time / (dur/1000.0)) if dur > 0 else 0,
        "output_sample_rate": 22050,
        "channels": 1,
        "RMS": rms,
        "peak": peak,
        "file_size": len(full_pcm),
        "VRAM_before": vram_before,
        "VRAM_peak": vram_after, # Approx
        "VRAM_after": vram_after,
        "process_RAM": 0.0,
        "error_type": error_type,
        "error_message": error_message,
        "_pcm": full_pcm if is_valid else None
    }

if __name__ == "__main__":
    out_dir = Path(sys.argv[1])
    ref_audio = Path(sys.argv[2])
    transcript = sys.argv[3]
    
    # We will let the orchestrator handle picking the best PCM and writing it.
    run_cosyvoice2(out_dir, ref_audio, transcript)
