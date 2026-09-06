import json
import subprocess
import threading
import time
import urllib.request

import psutil

# The 4 test utterances
UTTERANCES = [
    "Yes.",                                           # 1 word (or 3 words limit)
    "Sure, let me check.",                            # 4 words (or 8 words limit)
    "Sure, let me check that right now. One moment.", # 9 words (or 15 words limit)
    "Sure, let me check that right now. It will only take a moment for me to verify the details in the system before we proceed further." # 26 words (or 25 words limit)
]

def get_vram():
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,nounits,noheader"],
            encoding='utf-8'
        )
        return max(int(line.strip()) for line in output.strip().split('\n') if line.strip())
    except Exception:
        return 0

class ResourceMonitor(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.peak_vram = 0
        self.peak_cpu = 0
        self.daemon = True

    def run(self):
        # Baseline
        self.peak_vram = get_vram()
        psutil.cpu_percent(interval=None) # Prime psutil
        
        while self.running:
            vram = get_vram()
            self.peak_vram = max(self.peak_vram, vram)
                
            cpu = psutil.cpu_percent(interval=0.1)
            self.peak_cpu = max(self.peak_cpu, cpu)
            
            time.sleep(0.05)
            
    def stop(self):
        self.running = False
        self.join()

def run_benchmark():
    print(f"{'Words':<6} | {'Chars':<6} | {'TTFB (s)':<9} | {'Total (s)':<9} | {'Audio (s)':<9} | {'RTF':<6} | {'Peak VRAM':<10} | {'Peak CPU'}")
    print("-" * 90)
    
    for text in UTTERANCES:
        monitor = ResourceMonitor()
        monitor.start()
        
        words = len(text.split())
        chars = len(text)
        
        data = json.dumps({
            "text": text,
            "voice_id": "talkflow_primary"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            'http://127.0.0.1:8091/v1/synthesize',
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        t0 = time.time()
        ttfb = 0
        audio_data = b""
        
        try:
            with urllib.request.urlopen(req) as res:
                # Read chunk by chunk to measure TTFB
                while True:
                    chunk = res.read(4096)
                    if not chunk:
                        break
                        
                    if ttfb == 0:
                        ttfb = time.time() - t0
                        
                    audio_data += chunk
                    
            t_total = time.time() - t0
            
            monitor.stop()
            
            # 8000 Hz, 16-bit PCM = 16000 bytes/sec
            audio_duration = len(audio_data) / 16000.0
            
            rtf = t_total / audio_duration if audio_duration > 0 else 0
            
            print(f"{words:<6} | {chars:<6} | {ttfb:<9.3f} | {t_total:<9.3f} | {audio_duration:<9.3f} | {rtf:<6.3f} | {monitor.peak_vram:<6} MB   | {monitor.peak_cpu:>5.1f}%")
            
        except Exception as e:
            monitor.stop()
            print(f"Error testing '{text}': {e}")
            
if __name__ == "__main__":
    run_benchmark()
