import asyncio
import time
import os
import sys
import numpy as np

# Adjust path to import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.realtime.asr.faster_whisper import FasterWhisperProvider
from app.realtime.asr.nemo_provider import NemoProvider
from app.realtime.asr.normalization import normalize_transcript

def create_dummy_audio(duration_sec=3.0, sample_rate=16000):
    """Generate 16kHz float32 white noise"""
    return np.random.randn(int(duration_sec * sample_rate)).astype(np.float32) * 0.1

async def run_benchmark():
    print("="*50)
    print("ASR CPU Benchmark: Whisper vs NeMo Parakeet")
    print("="*50)

    # 1. Faster Whisper
    print("\nLoading Faster Whisper (tiny.en)...")
    t0 = time.time()
    whisper_provider = FasterWhisperProvider(
        model_name="tiny.en",
        device="cpu",
        compute_type="float32",
        language="en",
        condition_on_previous_text=False,
        word_timestamps=False,
        initial_prompt="TalkFlow Medicare"
    )
    print(f"Whisper loaded in {time.time() - t0:.2f}s")
    
    # 2. NeMo Parakeet
    print("\nLoading NeMo Parakeet (nvidia/parakeet-unified-en-0.6b)...")
    t0 = time.time()
    nemo_provider = NemoProvider(
        model_path="nvidia/parakeet-unified-en-0.6b",
        device="cpu"
    )
    print(f"NeMo loaded in {time.time() - t0:.2f}s")

    print("\nBenchmarking 3-second audio chunk...")
    audio = create_dummy_audio(3.0)
    
    # Warmup
    whisper_provider.transcribe(audio, beam_size=1)
    nemo_provider.transcribe(audio, beam_size=1)
    
    # Test Whisper
    t0 = time.time()
    whisper_res = whisper_provider.transcribe(audio, beam_size=1)
    whisper_time = time.time() - t0
    
    # Test NeMo
    t0 = time.time()
    nemo_res = nemo_provider.transcribe(audio, beam_size=1)
    nemo_time = time.time() - t0
    
    print("\n" + "-"*30)
    print("RESULTS (CPU Inference)")
    print("-" * 30)
    print(f"Faster Whisper Latency: {whisper_time*1000:.1f} ms | RTF: {whisper_time/3.0:.3f}")
    print(f"NeMo Parakeet  Latency: {nemo_time*1000:.1f} ms | RTF: {nemo_time/3.0:.3f}")
    print("="*50)
    
    print(f"Notice: Parakeet RTF on CPU is generally higher. Use CUDA for production.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
