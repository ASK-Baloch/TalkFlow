# ruff: noqa
import argparse
import sys

import librosa
import numpy as np
from scipy.io import wavfile


def validate_resampler(file_8k: str, file_16k: str):
    try:
        sr8, data8 = wavfile.read(file_8k)
        sr16, data16 = wavfile.read(file_16k)
    except Exception as e:
        print(f"Error reading files: {e}")
        sys.exit(1)
        
    # Convert to float for comparison
    if data8.dtype != np.float32 and data8.dtype != np.float64:
        data8 = data8.astype(np.float64) / np.iinfo(data8.dtype).max
    if data16.dtype != np.float32 and data16.dtype != np.float64:
        data16 = data16.astype(np.float64) / np.iinfo(data16.dtype).max
        
    duration8 = len(data8) / float(sr8)
    duration16 = len(data16) / float(sr16)
    
    print("=== Resampler Validation Report ===")
    print(f"8kHz File: {file_8k}")
    print(f"16kHz File: {file_16k}")
    print("--- Duration Preservation ---")
    print(f"8kHz Duration: {duration8:.4f}s")
    print(f"16kHz Duration: {duration16:.4f}s")
    print(f"Difference: {abs(duration16 - duration8):.4f}s")
    
    print("--- Sample Count Check ---")
    print(f"8kHz Samples: {len(data8)}")
    print(f"16kHz Samples: {len(data16)}")
    expected_samples = len(data8) * 2
    print(f"Expected 16kHz Samples: {expected_samples}")
    print(f"Difference: {len(data16) - expected_samples} samples")
    
    if abs(len(data16) - expected_samples) <= 1:
        print("RESULT: Sample count ~= input_samples * 2 (PASS)")
    else:
        print("RESULT: Sample count mismatch (FAIL)")
        
    print("--- Amplitude Preservation ---")
    peak8 = np.max(np.abs(data8))
    peak16 = np.max(np.abs(data16))
    rms8 = np.sqrt(np.mean(data8**2))
    rms16 = np.sqrt(np.mean(data16**2))
    print(f"8kHz Peak: {peak8:.6f} | 16kHz Peak: {peak16:.6f}")
    print(f"8kHz RMS: {rms8:.6f} | 16kHz RMS: {rms16:.6f}")
    
    print("--- Data Integrity ---")
    print(f"NaN/Inf in 16kHz: {np.isnan(data16).any() or np.isinf(data16).any()}")
    
    dc8 = np.mean(data8)
    dc16 = np.mean(data16)
    print(f"8kHz DC Offset: {dc8:.6f}")
    print(f"16kHz DC Offset: {dc16:.6f}")
    
    # State Preservation / Spectral Abnormalities Check
    # If the resampler state is constantly reset across frames, there will be high-frequency clicks.
    # We can detect this by checking if the 16kHz audio has unnatural high-frequency energy compared to the 8kHz audio.
    # But a simpler heuristic: the zero crossing rate shouldn't explode.
    zcr8 = librosa.feature.zero_crossing_rate(data8)[0].mean()
    zcr16 = librosa.feature.zero_crossing_rate(data16)[0].mean()
    print("--- Spectral/State Check ---")
    print(f"8kHz ZCR: {zcr8:.4f}")
    print(f"16kHz ZCR: {zcr16:.4f}")
    if zcr16 > zcr8 * 1.5:
         print("WARNING: Unusually high zero-crossing rate in 16kHz. Resampler state might be resetting per frame causing clicks.")
    else:
         print("State preservation appears intact (no excessive clicks).")
    
    print("===================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_8k", help="Path to 8kHz WAV")
    parser.add_argument("file_16k", help="Path to 16kHz WAV")
    args = parser.parse_args()
    validate_resampler(args.file_8k, args.file_16k)

