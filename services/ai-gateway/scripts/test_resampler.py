import torch
import torchaudio
import numpy as np

def test_streaming_resampler():
    print("=== RESAMPLER VERIFICATION ===")
    
    # 1. Generate test signal: 1 second of 440 Hz sine wave + random noise at 8kHz
    sr_in = 8000
    sr_out = 16000
    t = np.linspace(0, 1.0, sr_in, endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.05 * np.random.randn(sr_in)
    signal = signal.astype(np.float32)
    
    tensor_in = torch.from_numpy(signal).unsqueeze(0) # [1, sr_in]
    
    # A. One-pass resample
    resampler_full = torchaudio.transforms.Resample(orig_freq=sr_in, new_freq=sr_out, dtype=torch.float32)
    out_full = resampler_full(tensor_in).squeeze(0).numpy()
    
    # B. Packetized resample (similar to AudioSocket 320 bytes = 160 samples per packet at 8kHz)
    packet_size = 160
    resampler_stream = torchaudio.transforms.Resample(orig_freq=sr_in, new_freq=sr_out, dtype=torch.float32)
    
    out_chunks = []
    for i in range(0, sr_in, packet_size):
        chunk = tensor_in[:, i:i+packet_size]
        out_chunk = resampler_stream(chunk)
        out_chunks.append(out_chunk.squeeze(0).numpy())
        
    out_stream = np.concatenate(out_chunks)
    
    # Compare
    print(f"Input samples: {sr_in}")
    print(f"Full-pass output samples: {len(out_full)}")
    print(f"Stream output samples: {len(out_stream)}")
    
    min_len = min(len(out_full), len(out_stream))
    diff = np.abs(out_full[:min_len] - out_stream[:min_len])
    max_err = np.max(diff)
    rms_err = np.sqrt(np.mean(diff**2))
    
    print(f"Max Absolute Error: {max_err:.10f}")
    print(f"RMS Error: {rms_err:.10f}")
    
    # Check boundary errors
    boundary_errors = []
    out_packet_size = int(packet_size * (sr_out / sr_in))
    for i in range(1, len(out_chunks)):
        idx = i * out_packet_size
        if idx < min_len:
            # Check window around boundary
            window = diff[max(0, idx-5):min(min_len, idx+5)]
            boundary_errors.append(np.max(window))
            
    if boundary_errors:
        print(f"Max Boundary Error: {max(boundary_errors):.10f}")
        
    if max_err > 1e-4:
        print("FAIL: Streaming resampler produces discontinuities!")
    else:
        print("PASS: Streaming resampler perfectly matches one-pass resampling.")

if __name__ == "__main__":
    test_streaming_resampler()
