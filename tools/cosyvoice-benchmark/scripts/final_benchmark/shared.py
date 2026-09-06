import os
from pathlib import Path
import json

SENTENCES = [
    # SHORT
    {"id": "S01", "category": "SHORT", "text": "Hi, how are you doing today?"},
    {"id": "S02", "category": "SHORT", "text": "Okay, perfect."},
    {"id": "S03", "category": "SHORT", "text": "What's your ZIP code?"},
    {"id": "S04", "category": "SHORT", "text": "Alright, got it."},
    
    # MEDIUM
    {"id": "M01", "category": "MEDIUM", "text": "Do you currently have Medicare Part A and Part B?"},
    {"id": "M02", "category": "MEDIUM", "text": "Sorry, I didn't quite catch that. Could you say your ZIP code again?"},
    {"id": "M03", "category": "MEDIUM", "text": "And may I ask how old you are?"},
    {"id": "M04", "category": "MEDIUM", "text": "Okay, great. Thank you for confirming that."},
    
    # LONG
    {"id": "L01", "category": "LONG", "text": "Okay, I have your ZIP code as seven four four two zero. Is that correct?"},
    {"id": "L02", "category": "LONG", "text": "Perfect. And just to make sure I have everything right, let me quickly go over what you told me."},
    {"id": "L03", "category": "LONG", "text": "Thanks for your patience. I just have one more quick question before we continue."},
    {"id": "L04", "category": "LONG", "text": "Sorry about that. I didn't quite hear the last part clearly. Could you please say it one more time for me?"},
    
    # NUMBER / DOMAIN TESTS
    {"id": "N01", "category": "NUMBER_DOMAIN", "text": "Your ZIP code is seven four four two zero."},
    {"id": "N02", "category": "NUMBER_DOMAIN", "text": "Do you have Medicare Part A and Part B?"},
    {"id": "N03", "category": "NUMBER_DOMAIN", "text": "Your date of birth is January fifteenth, nineteen fifty-eight."},
    {"id": "N04", "category": "NUMBER_DOMAIN", "text": "I heard your age as sixty-seven. Is that correct?"},
]

WARMUP_TEXT = "Hi, how are you doing today?"
TRIALS = 3

def get_vram_usage():
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / (1024 * 1024) # MB
    except:
        pass
    return 0.0

def validate_audio(pcm_data: bytes, sample_rate: int, sample_width: int):
    # Returns (valid, duration_ms, rms, peak, reason)
    if not pcm_data:
        return False, 0.0, 0.0, 0.0, "EMPTY_OUTPUT"
    
    import numpy as np
    
    try:
        samples = np.frombuffer(pcm_data, dtype=np.int16)
        if len(samples) == 0:
            return False, 0.0, 0.0, 0.0, "EMPTY_OUTPUT"
            
        if np.isnan(samples).any() or np.isinf(samples).any():
            return False, 0.0, 0.0, 0.0, "CORRUPT_OUTPUT"
            
        float_samples = samples.astype(np.float32) / 32768.0
        
        peak = float(np.max(np.abs(float_samples)))
        rms = float(np.sqrt(np.mean(float_samples**2)))
        duration_ms = (len(samples) / sample_rate) * 1000.0
        
        if rms < 0.0001 or peak < 0.001:
            return False, duration_ms, rms, peak, "SILENT_OUTPUT"
            
        if duration_ms < 100:
            return False, duration_ms, rms, peak, "TOO_SHORT"
            
        return True, duration_ms, rms, peak, "VALID"
        
    except Exception as e:
        return False, 0.0, 0.0, 0.0, f"VALIDATION_ERROR: {str(e)}"
