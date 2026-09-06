import json
import sys
import time
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "services" / "ai-gateway"))

from chatterbox.tts_turbo import ChatterboxTurboTTS

ASSET_DIR = ROOT / "assets" / "tts" / "talkflow-chatterbox-v1"
REFERENCE_WAV = ROOT / "tools" / "tts-assets" / "reference" / "talkflow_reference.wav"
PROMPTS_FILE = ROOT / "tools" / "tts-assets" / "talkflow_prompts.json"

def main():
    if not PROMPTS_FILE.exists():
        raise FileNotFoundError(f"Prompts file not found: {PROMPTS_FILE}")
        
    with open(PROMPTS_FILE, "r") as f:
        prompts_data = json.load(f)
        
    responses = prompts_data.get("responses", {})
    if not responses:
        raise ValueError("No responses found in prompts file.")

    print("Loading Chatterbox Turbo model...")
    t0 = time.perf_counter()
    model = ChatterboxTurboTTS.from_pretrained(device="cuda")
    print(f"Loaded in {time.perf_counter() - t0:.2f}s")

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    
    sample_rate = getattr(model, "sr", 24000)
    print(f"Model Sample Rate: {sample_rate} Hz")

    for response_id, text in responses.items():
        print(f"Generating [{response_id}]: {text}")
        t_start = time.perf_counter()
        
        gen_result = model.generate(text, audio_prompt_path=str(REFERENCE_WAV))
        
        pcm = (np.asarray(gen_result, dtype=np.float32).reshape(-1) * 32767.0).astype(np.int16).tobytes()
        
        duration = len(pcm) / 2 / sample_rate
        print(f"  -> Generated {duration:.2f}s audio in {time.perf_counter() - t_start:.2f}s")
        
        wav_path = ASSET_DIR / f"{response_id}.wav"
        with wave.open(str(wav_path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm)

if __name__ == "__main__":
    main()
