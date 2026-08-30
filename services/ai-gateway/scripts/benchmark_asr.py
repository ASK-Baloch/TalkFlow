import asyncio
import time
import os
import sys
import glob
import numpy as np
import wave

# Adjust path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.realtime.asr.nemo_provider import NemoProvider
from app.realtime.asr.normalization import normalize_transcript
from app.core.config import get_asr_vocabulary

def read_wav(path: str) -> np.ndarray:
    with wave.open(path, 'rb') as wf:
        n_frames = wf.getnframes()
        data = wf.readframes(n_frames)
        pcm = np.frombuffer(data, dtype=np.int16)
        return pcm.astype(np.float32) / 32768.0

def simulate_streaming(provider, audio, chunk_ms):
    chunk_samples = int(16000 * chunk_ms / 1000)
    
    stream = provider.open_stream(beam_size=1, context_hints=[])
    stream._chunk_samples = chunk_samples # Override chunk samples for test
    
    latencies = []
    
    for i in range(0, len(audio), chunk_samples):
        chunk = audio[i:i+chunk_samples]
        stream.push_audio(chunk)
        
        t0 = time.time()
        # Force it to process the partial chunk immediately if it reached chunk size
        res = stream.get_partial()
        latencies.append(time.time() - t0)
        
    final_res = stream.finalize()
    return final_res.text, latencies

async def run_benchmark(audio_dir: str):
    print("="*50)
    print("ASR Streaming Latency & Accuracy Benchmark Suite")
    print("="*50)

    model_path = os.getenv("ASR_MODEL", "models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo")
    device = os.getenv("ASR_DEVICE", "cuda")
    
    print(f"\nLoading NeMo Parakeet from {model_path} on {device}...")
    t0 = time.time()
    nemo_provider = NemoProvider(
        model_path=model_path,
        device=device
    )
    print(f"NeMo loaded in {time.time() - t0:.2f}s")

    wav_files = glob.glob(os.path.join(audio_dir, "*.wav"))
    if not wav_files:
        print(f"\nNo .wav files found in {audio_dir}.")
        # Use synthetic test signal if no wavs found
        print("Using synthetic sine wave for latency testing...")
        wav_files = ["synthetic"]
        
    print(f"\nFound {len(wav_files)} files to benchmark. Running tests...")

    for wav_file in wav_files:
        print(f"\n--- Processing: {os.path.basename(wav_file)} ---")
        if wav_file == "synthetic":
            # 5 seconds of 440Hz sine wave
            t = np.linspace(0, 5, 16000 * 5, False)
            audio = np.sin(440 * 2 * np.pi * t).astype(np.float32)
        else:
            audio = read_wav(wav_file)
            
        duration = len(audio) / 16000.0
        print(f"Audio Duration: {duration:.2f}s")
        
        # Test Non-streaming (Baseline)
        t0 = time.time()
        res_baseline = nemo_provider.transcribe(audio, beam_size=1)
        latency_baseline = time.time() - t0
        print(f"\nBaseline (Non-streaming) Latency: {latency_baseline*1000:.1f}ms")
        print(f"Baseline Result: '{res_baseline.text}'")

        # Test Streaming 320ms
        print("\nTesting 320ms streaming...")
        res_320, latencies_320 = simulate_streaming(nemo_provider, audio, 320)
        avg_320 = np.mean(latencies_320) * 1000
        p95_320 = np.percentile(latencies_320, 95) * 1000
        print(f"320ms Avg Latency: {avg_320:.1f}ms, P95: {p95_320:.1f}ms")
        print(f"320ms Result: '{res_320}'")
        
        # Test Streaming 240ms
        print("\nTesting 240ms streaming...")
        res_240, latencies_240 = simulate_streaming(nemo_provider, audio, 240)
        avg_240 = np.mean(latencies_240) * 1000
        p95_240 = np.percentile(latencies_240, 95) * 1000
        print(f"240ms Avg Latency: {avg_240:.1f}ms, P95: {p95_240:.1f}ms")
        print(f"240ms Result: '{res_240}'")

    print("\n" + "="*50)

if __name__ == "__main__":
    audio_dir = sys.argv[1] if len(sys.argv) > 1 else "/app/debug"
    asyncio.run(run_benchmark(audio_dir))
