# ruff: noqa
import asyncio
import sys
import time

import soundfile as sf


async def main():
    sys.path.append("/app")
    from app.realtime.asr.faster_whisper import FasterWhisperProvider
    
    provider = FasterWhisperProvider(
        model_name="models/large-v3-turbo-ct2",
        device="cuda",
        compute_type="int8_float16",
        language="en",
        condition_on_previous_text=False,
        word_timestamps=False,
        initial_prompt="TalkFlow"
    )
    
    audio, sr = sf.read("/app/test_set/phase3_v1/008.wav", dtype="float32")
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
        
    print(f"Loaded audio, duration={len(audio)/sr:.2f}s")
    
    # Warmup
    print("Warming up...")
    res = await asyncio.to_thread(provider.transcribe, audio, beam_size=1)
    expected_text = res.text
    print(f"Expected: {expected_text}")
    
    tasks = []
    concurrency = 20
    print(f"Launching {concurrency} concurrent transcribe calls...")
    
    start_time = time.perf_counter()
    
    for i in range(concurrency):
        tasks.append(asyncio.to_thread(provider.transcribe, audio, beam_size=1))
        
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = time.perf_counter()
    
    mismatches = 0
    exceptions = 0
    
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            exceptions += 1
            print(f"Task {i} failed: {res}")
        elif res.text != expected_text:
            mismatches += 1
            print(f"Task {i} mismatch: {res.text}")
            
    print("--- Concurrency Test Results ---")
    print(f"Total time: {end_time - start_time:.2f}s")
    print(f"Mismatches: {mismatches}")
    print(f"Exceptions: {exceptions}")
    
    if mismatches == 0 and exceptions == 0:
        print("CONCURRENCY TEST PASSED")
    else:
        print("CONCURRENCY TEST FAILED")
        
if __name__ == "__main__":
    asyncio.run(main())

