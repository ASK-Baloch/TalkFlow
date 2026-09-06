import csv
import json
import subprocess
import sys
import wave
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

def run_cmd(cmd, env=None):
    print(f"Running: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    return process.returncode

def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    benchmark_dir = ROOT / "benchmarks" / "tts" / f"final_{timestamp}"
    
    dirs = [
        benchmark_dir,
        benchmark_dir / "environment",
        benchmark_dir / "chatterbox_turbo" / "audio",
        benchmark_dir / "cosyvoice3" / "audio",
        benchmark_dir / "cosyvoice2" / "audio",
        benchmark_dir / "comparison" / "listening"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        
    ref_audio = ROOT / "assets" / "voices" / "talkflow" / "talkflow_reference.wav"
    ref_transcript_file = ROOT / "assets" / "voices" / "talkflow" / "transcript.txt"
    
    with open(ref_transcript_file, "r") as f:
        transcript = f.read().strip()
        
    # Get system info
    import platform
    env_info = {
        "os": platform.system(),
        "release": platform.release(),
        "processor": platform.processor()
    }
    with open(benchmark_dir / "environment" / "info.json", "w") as f:
        json.dump(env_info, f, indent=2)
        
    print(f"Benchmark started. Dir: {benchmark_dir}")
    
    python_chatterbox = str(ROOT / "tools" / "tts-assets" / ".venv" / "Scripts" / "python.exe")
    python_cosyvoice = str(ROOT / "tools" / "cosyvoice-benchmark" / ".venv" / "Scripts" / "python.exe")
    
    script_dir = ROOT / "tools" / "cosyvoice-benchmark" / "scripts" / "final_benchmark"
    
    # 1. Chatterbox Turbo
    print("\n" + "="*50)
    print("Running Chatterbox Turbo")
    run_cmd([python_chatterbox, str(script_dir / "run_chatterbox.py"), str(benchmark_dir / "chatterbox_turbo"), str(ref_audio)])
    
    # 2. CosyVoice 3
    print("\n" + "="*50)
    print("Running CosyVoice 3")
    run_cmd([python_cosyvoice, str(script_dir / "run_cosyvoice3.py"), str(benchmark_dir / "cosyvoice3"), str(ref_audio), transcript])
    
    # 3. CosyVoice 2
    print("\n" + "="*50)
    print("Running CosyVoice 2")
    run_cmd([python_cosyvoice, str(script_dir / "run_cosyvoice2.py"), str(benchmark_dir / "cosyvoice2"), str(ref_audio), transcript])
    
    # Consolidate metrics and convert to telephony
    print("\n" + "="*50)
    print("Consolidating metrics and converting audio...")
    consolidate(benchmark_dir)

def resample_to_telephony(src_path, dest_path):
    # Convert to 8kHz mono PCM16
    try:
        with wave.open(str(src_path), "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            frames = wav.readframes(wav.getnframes())
            
        import numpy as np
        if sample_width == 2:
            dtype = np.int16
        elif sample_width == 4:
            dtype = np.int32
        else:
            return False
            
        samples = np.frombuffer(frames, dtype=dtype)
        if channels == 2:
            samples = samples[::2] # simple mono mix
            
        float_samples = samples.astype(np.float32)
        
        if framerate != 8000:
            import soxr
            float_samples = soxr.resample(float_samples, framerate, 8000, quality="HQ")
            
        pcm16 = np.clip(float_samples, -32768.0, 32767.0).astype(np.int16).tobytes()
        
        with wave.open(str(dest_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(8000)
            wav.writeframes(pcm16)
        return True
    except Exception as e:
        print(f"Failed to resample {src_path}: {e}")
        return False

def consolidate(benchmark_dir):
    all_trials = []
    models = ["chatterbox_turbo", "cosyvoice3", "cosyvoice2"]
    
    listening_dir = benchmark_dir / "comparison" / "listening"
    telephony_dir = benchmark_dir / "comparison" / "listening_telephony"
    telephony_dir.mkdir(exist_ok=True)
    
    for m in models:
        metrics_file = benchmark_dir / m / "metrics.json"
        if metrics_file.exists():
            with open(metrics_file, "r") as f:
                data = json.load(f)
                all_trials.extend(data.get("trials", []))
                
    # Write raw json
    with open(benchmark_dir / "comparison" / "raw_results.json", "w") as f:
        json.dump(all_trials, f, indent=2)
        
    if not all_trials:
        print("No trials found.")
        return
        
    # Write CSV
    keys = all_trials[0].keys()
    with open(benchmark_dir / "comparison" / "raw_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for t in all_trials:
            writer.writerow(t)
            
    # Organize audio
    import sys
    sys.path.insert(0, str(ROOT / "tools" / "cosyvoice-benchmark" / "scripts" / "final_benchmark"))
    from shared import SENTENCES
    
    manifest_lines = ["# Audio Manifest\n\n"]
    
    for s in SENTENCES:
        s_id = s["id"]
        manifest_lines.append(f"## {s_id}: {s['text']}\n")
        
        s_list_dir = listening_dir / s_id
        s_list_dir.mkdir(exist_ok=True)
        s_tel_dir = telephony_dir / s_id
        s_tel_dir.mkdir(exist_ok=True)
        
        for m in models:
            src_audio = benchmark_dir / m / "audio" / f"{s_id}.wav"
            if src_audio.exists():
                import shutil
                dest_audio = s_list_dir / f"{m}.wav"
                dest_tel_audio = s_tel_dir / f"{m}.wav"
                
                shutil.copy2(src_audio, dest_audio)
                resample_to_telephony(src_audio, dest_tel_audio)
                
                manifest_lines.append(f"### {m}\n- Native: `comparison/listening/{s_id}/{m}.wav`\n- Telephony: `comparison/listening_telephony/{s_id}/{m}.wav`\n- Status: VALID\n")
            else:
                manifest_lines.append(f"### {m}\n- NO VALID AUDIO — generation failed.\n")
                
    with open(benchmark_dir / "comparison" / "AUDIO_MANIFEST.md", "w") as f:
        f.writelines(manifest_lines)
        
    # Build final report
    build_report(benchmark_dir, models, all_trials)
    
def build_report(benchmark_dir, models, all_trials):
    print("Building report...")
    report_script = ROOT / "tools" / "cosyvoice-benchmark" / "scripts" / "final_benchmark" / "generate_report.py"
    
    # Run the report generator
    import subprocess
    python_exe = sys.executable
    subprocess.run([python_exe, str(report_script), str(benchmark_dir)])
        
if __name__ == "__main__":
    main()
