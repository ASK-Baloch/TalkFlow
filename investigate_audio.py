import glob
import os
import time

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel


def main():
    print("Loading model...")
    model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type="int8_float16")
    
    wav_files = glob.glob("/app/test_set/*_16k.wav")
    print(f"Found {len(wav_files)} files.")
    
    for wf in wav_files:
        try:
            data, sr = sf.read(wf)
            duration = len(data) / sr
            
            # min max rms
            min_val = np.min(data)
            max_val = np.max(data)
            rms = np.sqrt(np.mean(data**2))
            clipping_count = np.sum(np.abs(data) >= 0.99)
            
            # transcribe
            t0 = time.perf_counter_ns()
            segs, _ = model.transcribe(
                wf,
                language="en",
                beam_size=1,
                temperature=0.0,
                vad_filter=False,
                condition_on_previous_text=False,
                initial_prompt="TalkFlow."
            )
            text = " ".join([s.text for s in segs]).strip()
            t1 = time.perf_counter_ns()
            decode_ms = (t1 - t0) / 1_000_000
            
            print(f"File: {os.path.basename(wf)}")
            print(f"Duration: {duration:.2f}s | SR: {sr} | Dtype: {data.dtype}")
            print(f"Min: {min_val:.3f} | Max: {max_val:.3f} | RMS: {rms:.4f} | Clipping: {clipping_count}")
            print(f"Text: '{text}' | Decode: {decode_ms:.1f}ms")
            print("-" * 40)
            
        except Exception as e:
            print(f"Error on {wf}: {e}")

if __name__ == '__main__':
    main()
