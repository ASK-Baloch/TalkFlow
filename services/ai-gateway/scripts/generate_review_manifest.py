import os
import glob
import csv
import json
import time
import shutil
import soundfile as sf
import torch
import gc
from omegaconf import OmegaConf

def get_nemo_model(model_name):
    import nemo.collections.asr as nemo_asr
    print(f"Loading {model_name}...")
    model = nemo_asr.models.EncDecRNNTBPEModel.restore_from(model_name)
    if getattr(model.cfg, "validation_ds", None) is None:
        model.cfg.validation_ds = OmegaConf.create({})
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    return model

def main():
    wav_files = glob.glob("/app/test_set/*_16k.wav")
    wav_files.sort(key=os.path.getmtime)
    
    out_dir = "/app/phase3_human_review"
    os.makedirs(out_dir, exist_ok=True)
    
    results = []
    
    print(f"Found {len(wav_files)} WAV files.")
    for idx, w in enumerate(wav_files):
        audio, sr = sf.read(w)
        duration = len(audio) / sr
        filename = f"{idx+1:03d}.wav"
        
        shutil.copy(w, os.path.join(out_dir, filename))
        
        results.append({
            "index": idx+1,
            "wav_path": w,
            "filename": filename,
            "duration": f"{duration:.2f}",
            "guessed_category": "",
            "expected_text": "",
            "parakeet": "",
            "nemotron": "",
            "whisper": ""
        })
        
    print("Files copied.")

    # Parakeet
    try:
        model = get_nemo_model("/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo")
        cfg = OmegaConf.create(OmegaConf.to_container(model.cfg.decoding, resolve=True))
        cfg.strategy = "greedy_batch"
        model.change_decoding_strategy(cfg)
        for r in results:
            audio, _ = sf.read(r["wav_path"])
            transcripts = model.transcribe(audio=audio, return_hypotheses=False)
            text_obj = transcripts
            while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0: text_obj = text_obj[0]
            if hasattr(text_obj, 'text'): hyp = text_obj.text.strip()
            elif hasattr(text_obj, 'text_no_timesteps'): hyp = text_obj.text_no_timesteps.strip()
            else: hyp = str(text_obj).strip()
            r["parakeet"] = hyp
        del model
        gc.collect()
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"Error running Parakeet: {e}")

    # Nemotron
    try:
        model = get_nemo_model("/app/models/nemotron-speech-streaming-en-0.6b/nemotron-speech-streaming-en-0.6b.nemo")
        cfg = OmegaConf.create(OmegaConf.to_container(model.cfg.decoding, resolve=True))
        cfg.strategy = "greedy_batch"
        model.change_decoding_strategy(cfg)
        for r in results:
            audio, _ = sf.read(r["wav_path"])
            transcripts = model.transcribe(audio=audio, return_hypotheses=False)
            text_obj = transcripts
            while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0: text_obj = text_obj[0]
            if hasattr(text_obj, 'text'): hyp = text_obj.text.strip()
            elif hasattr(text_obj, 'text_no_timesteps'): hyp = text_obj.text_no_timesteps.strip()
            else: hyp = str(text_obj).strip()
            r["nemotron"] = hyp
        del model
        gc.collect()
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"Error running Nemotron: {e}")

    # Whisper
    try:
        from faster_whisper import WhisperModel
        print("Loading Whisper large-v3-turbo...")
        model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type="float16")
        for r in results:
            segs, _ = model.transcribe(r["wav_path"], language="en")
            hyp = " ".join([s.text for s in segs]).strip()
            r["whisper"] = hyp
            
            tl = hyp.lower()
            cat = ""
            if "medicare" in tl and "medicaid" not in tl:
                if "part a" in tl and "part b" in tl: cat = "part_both"
                elif "part a" in tl: cat = "part_a"
                elif "part b" in tl: cat = "part_b"
                else: cat = "medicare"
            elif "medicaid" in tl: cat = "medicaid"
            elif "zip" in tl or any(c.isdigit() for c in tl) and "years" not in tl: cat = "zip"
            elif "years" in tl or "old" in tl or any(c.isdigit() for c in tl): cat = "age"
            elif any(w in tl for w in ["humana", "aetna", "united", "blue cross"]): cat = "insurance"
            elif "talk flow" in tl or "talkflow" in tl: cat = "talkflow"
            r["guessed_category"] = cat

        del model
        gc.collect()
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"Error running Whisper: {e}")
        
    csv_path = os.path.join(out_dir, "review.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "duration", "guessed_category", "expected_text", "parakeet", "nemotron", "whisper"])
        for r in results:
            writer.writerow([
                r["filename"],
                r["duration"],
                r["guessed_category"],
                "", 
                r["parakeet"],
                r["nemotron"],
                r["whisper"]
            ])
            
    print(f"Generated {csv_path}")
    
    with open("/app/test_set/human_review_manifest.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["index", "wav_path", "duration", "guessed_category", "expected_text", "parakeet", "nemotron", "whisper"])
        for r in results:
            writer.writerow([
                r["index"],
                r["wav_path"],
                r["duration"],
                r["guessed_category"],
                "",
                r["parakeet"],
                r["nemotron"],
                r["whisper"]
            ])
    print("Generated /app/test_set/human_review_manifest.csv")

if __name__ == "__main__":
    main()
