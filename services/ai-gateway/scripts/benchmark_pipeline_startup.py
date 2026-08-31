# ruff: noqa
import os
import socket
import time
import uuid

import numpy as np
import soundfile as sf


def float32_to_pcm16le(audio: np.ndarray) -> bytes:
    audio = np.clip(audio, -1.0, 1.0)
    audio_pcm = (audio * 32767.0).astype(np.int16)
    return audio_pcm.tobytes()

def send_audiosocket(sock, kind, payload=b""):
    header = bytes([kind]) + len(payload).to_bytes(2, "big")
    sock.sendall(header + payload)

def main():
    wav_path = "scripts/test_set/001.wav"
    audio_data, sr = sf.read(wav_path)
    if sr != 16000:
        raise ValueError("Audio must be 16kHz")
    
    # We need 8kHz for AudioSocket, let's downsample manually for the test
    import librosa
    audio_8k = librosa.resample(audio_data, orig_sr=16000, target_sr=8000)
    audio_f32 = audio_8k.astype(np.float32)
    chunk_size = 320 # 40ms of 8kHz

    port = int(os.environ.get("AUDIOSOCKET_PORT", "9019"))
    
    print("\nStarting 10 sequential full-pipeline transcribes:")
    for i in range(1, 11):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", port))
        
        call_uuid = uuid.uuid4().bytes
        send_audiosocket(sock, 0x01, call_uuid)
        
        time.perf_counter_ns()
        for idx in range(0, len(audio_f32), chunk_size):
            chunk = audio_f32[idx:idx+chunk_size]
            if len(chunk) < chunk_size:
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
            payload = float32_to_pcm16le(chunk)
            send_audiosocket(sock, 0x10, payload)
            time.sleep(0.04) # simulate real-time
            
        silence_chunk = np.zeros(chunk_size, dtype=np.float32)
        silence_payload = float32_to_pcm16le(silence_chunk)
        for _ in range(int(3000 / 40)):
            send_audiosocket(sock, 0x10, silence_payload)
            time.sleep(0.04)
            
        time.perf_counter_ns()
        
        send_audiosocket(sock, 0x00)
        sock.close()
        
        print(f"Sent iteration {i}")
        time.sleep(1) # wait between iterations
        
if __name__ == "__main__":
    main()

