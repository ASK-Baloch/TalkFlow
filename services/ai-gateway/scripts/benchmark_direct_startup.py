import asyncio
import time
import soundfile as sf
from app.realtime.asr.faster_whisper import FasterWhisperProvider
import numpy as np

async def main():
    wav_path = "scripts/test_set/001.wav"
    print(f"Loading {wav_path}...")
    audio_data, sr = sf.read(wav_path)
    if sr != 16000:
        raise ValueError("Audio must be 16kHz")
    
    audio_f32 = audio_data.astype(np.float32)
    audio_duration_ms = (len(audio_f32) / 16000) * 1000

    print("Initializing FasterWhisperProvider...")
    t0 = time.perf_counter_ns()
    provider = FasterWhisperProvider(
        model_name="models/large-v3-turbo-ct2",
        device="cuda",
        compute_type="int8_float16",
        language="en",
        condition_on_previous_text=False,
        word_timestamps=False,
        initial_prompt="",
    )
    t1 = time.perf_counter_ns()
    model_loaded_ms = (t1 - t0) / 1_000_000
    print(f"Model loaded in {model_loaded_ms:.1f}ms")

    print("\nStarting 10 sequential transcribes:")
    print("iter | decode_ms | total_ms | rtf | text")
    
    for i in range(1, 11):
        t2 = time.perf_counter_ns()
        res = provider.transcribe(audio_f32, beam_size=1)
        t3 = time.perf_counter_ns()
        
        decode_ms = (t3 - t2) / 1_000_000
        rtf = decode_ms / audio_duration_ms
        
        print(f"{i:4d} | {decode_ms:9.1f} | {decode_ms:8.1f} | {rtf:3.3f} | {res.text}")
        
if __name__ == "__main__":
    asyncio.run(main())
