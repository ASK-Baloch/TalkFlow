import argparse
import sys
import numpy as np
import wave
import scipy.io.wavfile as wavfile

def audit_wav(path: str):
    try:
        sample_rate, data = wavfile.read(path)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        sys.exit(1)

    with wave.open(path, 'rb') as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        nframes = wf.getnframes()
        comptype = wf.getcomptype()
    
    duration = nframes / float(sample_rate)
    
    # Handle data formats
    if data.dtype == np.float32:
        max_val = 1.0
        min_val = -1.0
    elif data.dtype == np.int16:
        max_val = 32767.0
        min_val = -32768.0
    elif data.dtype == np.int32:
        max_val = 2147483647.0
        min_val = -2147483648.0
    elif data.dtype == np.uint8:
        max_val = 255.0
        min_val = 0.0
        data = data.astype(np.float32) - 128.0 # Center to 0 for analysis
    else:
        max_val = np.iinfo(data.dtype).max if np.issubdtype(data.dtype, np.integer) else 1.0
        min_val = np.iinfo(data.dtype).min if np.issubdtype(data.dtype, np.integer) else -1.0

    # Ensure float for calculation
    float_data = data.astype(np.float64)
    
    # Normalize if int
    if data.dtype != np.float32 and data.dtype != np.float64:
        norm_data = float_data / max_val
    else:
        norm_data = float_data

    peak_amplitude = np.max(np.abs(norm_data))
    rms = np.sqrt(np.mean(norm_data**2))
    
    # Clipping detection (samples exactly at min or max)
    if data.dtype == np.float32:
        clip_mask = (data >= max_val) | (data <= min_val)
        out_of_bounds_mask = (data > max_val) | (data < min_val)
    else:
        clip_mask = (data == np.max(data)) | (data == np.min(data)) # Empirical clipping
        clip_mask = clip_mask & (np.abs(norm_data) > 0.99) # Only if near absolute bounds
        out_of_bounds_mask = np.zeros_like(clip_mask, dtype=bool)

    clipping_count = np.sum(clip_mask)
    clipping_percent = (clipping_count / len(data)) * 100
    
    out_of_bounds_count = np.sum(out_of_bounds_mask)
    
    dc_offset = np.mean(norm_data)
    
    print(f"=== Audio Quality Report ===")
    print(f"File: {path}")
    print(f"Sample Rate: {sample_rate} Hz")
    print(f"Channels: {channels}")
    print(f"Sample Width: {sampwidth} bytes")
    print(f"Data Type: {data.dtype}")
    print(f"Compression: {comptype}")
    print(f"Duration: {duration:.3f} seconds")
    print(f"Frames: {nframes}")
    print(f"-----------------------------")
    print(f"Peak Amplitude (norm): {peak_amplitude:.6f}")
    print(f"RMS (norm): {rms:.6f}")
    print(f"DC Offset (norm): {dc_offset:.6f}")
    print(f"Clipping Samples: {clipping_count} ({clipping_percent:.4f}%)")
    print(f"Samples outside [-1, 1]: {out_of_bounds_count}")
    print(f"=============================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to WAV file")
    args = parser.parse_args()
    audit_wav(args.path)
