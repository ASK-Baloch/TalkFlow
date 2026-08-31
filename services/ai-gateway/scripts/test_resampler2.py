import numpy as np
import soxr

def test_streaming_resampler():
    print("=== SOXR RESAMPLER VERIFICATION ===")
    
    sr_in = 8000
    sr_out = 16000
    t = np.linspace(0, 1.0, sr_in, endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.05 * np.random.randn(sr_in)
    signal = signal.astype(np.float32)
    
    # A. One-pass resample
    resampler_full = soxr.ResampleStream(sr_in, sr_out, 1, dtype="float32")
    out_full = resampler_full.resample_chunk(signal, last=True)
    
    # B. Packetized resample
    packet_size = 160
    resampler_stream = soxr.ResampleStream(sr_in, sr_out, 1, dtype="float32")
    
    out_chunks = []
    for i in range(0, sr_in, packet_size):
        chunk = signal[i:i+packet_size]
        is_last = (i + packet_size >= sr_in)
        out_chunk = resampler_stream.resample_chunk(chunk, last=is_last)
        out_chunks.append(out_chunk)
        
    out_stream = np.concatenate(out_chunks)
    
    min_len = min(len(out_full), len(out_stream))
    diff = np.abs(out_full[:min_len] - out_stream[:min_len])
    max_err = np.max(diff)
    rms_err = np.sqrt(np.mean(diff**2))
    
    print(f"Max Absolute Error: {max_err:.10f}")
    print(f"RMS Error: {rms_err:.10f}")

if __name__ == "__main__":
    test_streaming_resampler()
