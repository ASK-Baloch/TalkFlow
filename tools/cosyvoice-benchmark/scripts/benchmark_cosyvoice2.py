import os
import sys
import time
import json
import torch
import torchaudio

# Setup paths to import from CosyVoice
BENCHMARK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COSYVOICE_DIR = os.path.join(BENCHMARK_DIR, 'CosyVoice')
sys.path.append(COSYVOICE_DIR)
sys.path.append(os.path.join(COSYVOICE_DIR, 'third_party', 'Matcha-TTS'))

from cosyvoice.cli.cosyvoice import AutoModel

def main():
    model_dir = os.path.join(BENCHMARK_DIR, 'models', 'CosyVoice2-0.5B')
    ref_audio_path = os.path.abspath(os.path.join(BENCHMARK_DIR, '..', '..', 'assets', 'voices', 'talkflow', 'talkflow_reference.wav'))
    ref_transcript = "hi how are you doing today great i am glad to hear that"
    
    sentences = [
        "Hi, how are you doing today?",
        "Okay, perfect.",
        "And what's your ZIP code?",
        "Do you currently have Medicare Part A and Part B?",
        "Okay, I have that as seven four four two zero. Is that correct?"
    ]
    
    results_dir = os.path.join(BENCHMARK_DIR, 'results', 'cosyvoice2')
    os.makedirs(results_dir, exist_ok=True)
    
    metrics = {
        'model': 'CosyVoice2-0.5B',
        'sentences': []
    }
    
    print("Loading model...")
    start_load = time.perf_counter()
    cosyvoice = AutoModel(model_dir=model_dir)
    metrics['model_load_ms'] = (time.perf_counter() - start_load) * 1000
    
    metrics['vram_after_load_mb'] = torch.cuda.memory_allocated() / 1024 / 1024 if torch.cuda.is_available() else 0
    
    print("Running warmup...")
    start_warmup = time.perf_counter()
    # Warmup with standard zero-shot, not streaming to just warm the weights
    for j in cosyvoice.inference_zero_shot("Hello there, I am just warming up the system to make sure it works.", ref_transcript, ref_audio_path, stream=False):
        pass
    metrics['warmup_ms'] = (time.perf_counter() - start_warmup) * 1000
    
    print("Starting benchmark runs...")
    
    for idx, text in enumerate(sentences):
        print(f"Testing sentence {idx + 1}: {text}")
        
        sent_metrics = {
            'text': text,
            'runs': []
        }
        
        # Run 10 iterations
        best_audio = None
        for iteration in range(10):
            torch.cuda.reset_peak_memory_stats()
            
            req_start = time.perf_counter()
            
            # Start streaming inference
            generator = cosyvoice.inference_zero_shot(text, ref_transcript, ref_audio_path, stream=True)
            
            first_chunk_time = None
            audio_chunks = []
            
            for chunk in generator:
                if first_chunk_time is None:
                    first_chunk_time = time.perf_counter()
                audio_chunks.append(chunk['tts_speech'])
            
            req_end = time.perf_counter()
            
            ttfa_ms = (first_chunk_time - req_start) * 1000 if first_chunk_time else (req_end - req_start) * 1000
            total_time_ms = (req_end - req_start) * 1000
            
            final_audio = torch.cat(audio_chunks, dim=1)
            audio_duration_ms = (final_audio.shape[1] / cosyvoice.sample_rate) * 1000
            rtf = (total_time_ms / 1000.0) / (audio_duration_ms / 1000.0) if audio_duration_ms > 0 else 0
            
            peak_vram = torch.cuda.max_memory_allocated() / 1024 / 1024 if torch.cuda.is_available() else 0
            
            run_data = {
                'ttfa_ms': ttfa_ms,
                'total_time_ms': total_time_ms,
                'audio_duration_ms': audio_duration_ms,
                'rtf': rtf,
                'peak_vram_mb': peak_vram
            }
            sent_metrics['runs'].append(run_data)
            
            # Keep the last iteration's audio for saving
            if iteration == 9:
                best_audio = final_audio
                
        # Calculate stats for the sentence
        ttfas = [r['ttfa_ms'] for r in sent_metrics['runs']]
        totals = [r['total_time_ms'] for r in sent_metrics['runs']]
        rtfs = [r['rtf'] for r in sent_metrics['runs']]
        
        ttfas.sort()
        totals.sort()
        rtfs.sort()
        
        sent_metrics['ttfa_p50'] = ttfas[len(ttfas)//2]
        sent_metrics['ttfa_p95'] = ttfas[int(len(ttfas)*0.95)]
        sent_metrics['total_p50'] = totals[len(totals)//2]
        sent_metrics['rtf_p50'] = rtfs[len(rtfs)//2]
        
        metrics['sentences'].append(sent_metrics)
        
        # Save output WAV
        out_path = os.path.join(results_dir, f'test_{idx+1}.wav')
        torchaudio.save(out_path, best_audio, cosyvoice.sample_rate)
        
    # Save final JSON
    json_path = os.path.join(results_dir, 'benchmark.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=4)
        
    print("Benchmark complete!")

if __name__ == '__main__':
    main()
