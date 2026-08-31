import os
import socket
import time
import uuid
import soundfile as sf
import numpy as np
from gtts import gTTS
import subprocess
import sys

def send_audiosocket(sock, msg_type, payload=b""):
    if len(payload) > 65535:
        raise ValueError("Payload too large")
    header = bytes([msg_type]) + len(payload).to_bytes(2, "big")
    sock.sendall(header + payload)

def float32_to_pcm16le(audio):
    audio = np.clip(audio, -1.0, 1.0)
    audio = (audio * 32767).astype(np.int16)
    return audio.tobytes()

def generate_audio(text, temp_wav):
    temp_mp3 = temp_wav.replace(".wav", ".mp3")
    tts = gTTS(text, lang='en', slow=False)
    tts.save(temp_mp3)
    # convert using ffmpeg
    subprocess.run(["ffmpeg", "-y", "-i", temp_mp3, "-ar", "8000", "-ac", "1", temp_wav], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    audio, sr = sf.read(temp_wav)
    return audio

def main():
    pause_ms = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    
    turns = [
        "Hello TalkFlow",
        "My name is Daniel Smith",
        "I am 67 years old",
        "My ZIP code is 7442"
    ]
    
    chunk_size = 320 # 40ms of 8kHz
    
    audios = []
    for i, text in enumerate(turns):
        print(f"[{i+1}/4] Synthesizing: {text}")
        temp_file = f"scripts/test_set/temp_turn_{i}.wav"
        audios.append((text, generate_audio(text, temp_file)))
    
    port = int(os.environ.get("AUDIOSOCKET_PORT", "9019"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", port))
    
    call_uuid = uuid.uuid4().bytes
    send_audiosocket(sock, 0x01, call_uuid) # UUID
    print("Connected to AudioSocket")
    
    for i, (text, audio) in enumerate(audios):
        
        print(f"[{i+1}/4] Streaming: {text}")
        for idx in range(0, len(audio), chunk_size):
            chunk = audio[idx:idx+chunk_size]
            if len(chunk) < chunk_size:
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
            payload = float32_to_pcm16le(chunk)
            send_audiosocket(sock, 0x10, payload) # PCM_8K
            time.sleep(0.04) # Realtime streaming
            
        print(f"[{i+1}/4] Pause for {pause_ms}ms...")
        silence_chunk = np.zeros(chunk_size, dtype=np.float32)
        silence_payload = float32_to_pcm16le(silence_chunk)
        for _ in range(int(pause_ms / 40)): 
            send_audiosocket(sock, 0x10, silence_payload)
            time.sleep(0.04)
            
    # Send a bit of final silence to let the last inference finish
    silence_chunk = np.zeros(chunk_size, dtype=np.float32)
    silence_payload = float32_to_pcm16le(silence_chunk)
    for _ in range(int(3000 / 40)):
        send_audiosocket(sock, 0x10, silence_payload)
        time.sleep(0.04)
        
    send_audiosocket(sock, 0x00) # TERMINATE
    sock.close()
    print("Simulation complete.")

if __name__ == "__main__":
    main()
