import os
import glob
import time
import sys
import numpy as np
from omegaconf import OmegaConf, open_dict

try:
    import nemo.collections.asr as nemo_asr
except ImportError:
    print("NeMo is not installed.")
    sys.exit(1)

def run_matrix_eval(test_set_dir: str):
    files = glob.glob(os.path.join(test_set_dir, "*_16k.wav"))
    files.sort(key=os.path.getmtime)
    
    if not files:
        print("No files found in test_set!")
        return
        
    print("Loading Parakeet Model...")
    model_path = "/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo"
    model = nemo_asr.models.EncDecRNNTBPEModel.restore_from(model_path)
    
    if getattr(model.cfg, "validation_ds", None) is None:
        model.cfg.validation_ds = OmegaConf.create({})
        
    import torch
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    
    # Store default decoding config
    default_cfg = OmegaConf.to_container(model.cfg.decoding, resolve=True)
    
    results = []
    
    configs = [
        {"name": "greedy_batch", "beam": 1, "context": False, "strategy": "greedy_batch"},
        {"name": "current_fast_final", "beam": 1, "context": False, "strategy": "greedy_batch"},
        {"name": "malsd_batch_b2", "beam": 2, "context": False, "strategy": "malsd_batch"},
        {"name": "malsd_batch_b4", "beam": 4, "context": False, "strategy": "malsd_batch"},
        {"name": "beam2", "beam": 2, "context": False, "strategy": "beam"},
        {"name": "beam4", "beam": 4, "context": False, "strategy": "beam"},
    ]
    
    for file in files:
        if "227ac925-10d1-43ff-8e99-a4cd9d37d300_16k.wav" not in file:
            continue
            
        print(f"\nEvaluating: {file}")
        import soundfile as sf
        audio, sr = sf.read(file)
        
        print("Warming up models...")
        for c in configs:
            cfg = OmegaConf.create(default_cfg)
            if c["beam"] == 1:
                cfg.strategy = "greedy_batch"
            else:
                cfg.strategy = c.get("strategy", "beam")
                with open_dict(cfg):
                    if not hasattr(cfg, cfg.strategy):
                        setattr(cfg, cfg.strategy, OmegaConf.create({}))
                    getattr(cfg, cfg.strategy).beam_size = c["beam"]
            model.change_decoding_strategy(cfg)
            model.transcribe(audio=audio, return_hypotheses=(c["beam"] > 1))
            
        print("Warmup complete. Starting benchmark.")
        file_res = {"file": file, "duration": len(audio) / sr, "runs": {}}
        
        for c in configs:
            cfg = OmegaConf.create(default_cfg)
            if c["beam"] == 1:
                cfg.strategy = "greedy_batch"
            else:
                cfg.strategy = c.get("strategy", "beam")
                with open_dict(cfg):
                    if not hasattr(cfg, cfg.strategy):
                        setattr(cfg, cfg.strategy, OmegaConf.create({}))
                    getattr(cfg, cfg.strategy).beam_size = c["beam"]
                    
            if c["context"]:
                pass # TODO: apply true context
                
            model.change_decoding_strategy(cfg)
            
            t0 = time.perf_counter_ns()
            transcripts = model.transcribe(audio=audio, return_hypotheses=(c["beam"] > 1))
            t1 = time.perf_counter_ns()
            
            decode_ms = (t1 - t0) / 1_000_000
            
            text_obj = transcripts
            while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0:
                text_obj = text_obj[0]
                
            if hasattr(text_obj, 'text'):
                text_str = text_obj.text
            elif hasattr(text_obj, 'text_no_timesteps'):
                text_str = text_obj.text_no_timesteps
            else:
                text_str = str(text_obj)
            
            file_res["runs"][c["name"]] = {
                "text": text_str.strip(),
                "ms": decode_ms
            }
            
        results.append(file_res)
        
    print("\n=== MATRIX REPORT ===")
    for r in results:
        print(f"\nFile: {os.path.basename(r['file'])} (Duration: {r['duration']:.2f}s)")
        for c in configs:
            name = c["name"]
            data = r["runs"][name]
            rtf = (data["ms"] / 1000) / r["duration"]
            print(f"  [{name}] {data['ms']:.1f}ms (RTF {rtf:.3f}) | '{data['text']}'")

if __name__ == "__main__":
    run_matrix_eval("/app/test_set")
