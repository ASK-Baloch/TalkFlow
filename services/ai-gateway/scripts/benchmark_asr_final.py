# ruff: noqa
import csv
import gc
import time

import numpy as np
import torch
from omegaconf import OmegaConf


def calculate_wer(reference, hypothesis):
    ref_words = reference.lower().replace('.', '').replace(',', '').split()
    hyp_words = hypothesis.lower().replace('.', '').replace(',', '').split()
    if len(ref_words) == 0: return 0.0
    
    d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1), dtype=int)
    for i in range(len(ref_words) + 1): d[i][0] = i
    for j in range(len(hyp_words) + 1): d[0][j] = j
    
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + 1)
                
    return d[len(ref_words)][len(hyp_words)] / len(ref_words)

def compute_metrics(results):
    metrics = {
        "medicare": {"total": 0, "correct": 0},
        "medicaid": {"total": 0, "correct": 0},
        "medicare_vs_medicaid": {"total": 0, "confused": 0},
        "part_a": {"total": 0, "correct": 0},
        "part_b": {"total": 0, "correct": 0},
        "part_a_vs_part_b": {"total": 0, "confused": 0},
        "negation": {"total": 0, "correct": 0},
        "zip": {"total": 0, "correct": 0},
        "age": {"total": 0, "correct": 0},
        "humana": {"total": 0, "correct": 0},
        "aetna": {"total": 0, "correct": 0},
        "united": {"total": 0, "correct": 0},
        "blue_cross": {"total": 0, "correct": 0},
        "talkflow": {"total": 0, "correct": 0}
    }
    
    total_wer = 0.0
    for r in results:
        expected = r["expected"].lower()
        hyp = r["hyp"].lower()
        wer = calculate_wer(expected, r["hyp"])
        total_wer += wer
        
        # Medicare
        if "medicare" in expected and "medicaid" not in expected:
            metrics["medicare"]["total"] += 1
            if "medicare" in hyp: metrics["medicare"]["correct"] += 1
            if "medicaid" in hyp: 
                metrics["medicare_vs_medicaid"]["total"] += 1
                metrics["medicare_vs_medicaid"]["confused"] += 1
        
        # Medicaid
        if "medicaid" in expected:
            metrics["medicaid"]["total"] += 1
            if "medicaid" in hyp: metrics["medicaid"]["correct"] += 1
            if "medicare" in hyp:
                metrics["medicare_vs_medicaid"]["total"] += 1
                metrics["medicare_vs_medicaid"]["confused"] += 1
                
        # Part A
        if "part a" in expected:
            metrics["part_a"]["total"] += 1
            if "part a" in hyp: metrics["part_a"]["correct"] += 1
            if "part b" in hyp and "part b" not in expected:
                metrics["part_a_vs_part_b"]["total"] += 1
                metrics["part_a_vs_part_b"]["confused"] += 1

        # Part B
        if "part b" in expected:
            metrics["part_b"]["total"] += 1
            if "part b" in hyp: metrics["part_b"]["correct"] += 1
            if "part a" in hyp and "part a" not in expected:
                metrics["part_a_vs_part_b"]["total"] += 1
                metrics["part_a_vs_part_b"]["confused"] += 1
                
        # Negation
        if "don't" in expected or "no" in expected:
            metrics["negation"]["total"] += 1
            if "don't" in hyp or "no" in hyp: metrics["negation"]["correct"] += 1
            
        # ZIP
        if "zip" in expected:
            metrics["zip"]["total"] += 1
            if wer < 0.2: metrics["zip"]["correct"] += 1
            
        # Age
        if "years old" in expected or "i am" in expected:
            if "zip" not in expected and "calling" not in expected:
                metrics["age"]["total"] += 1
                if wer < 0.2: metrics["age"]["correct"] += 1

        # Insurance
        if "humana" in expected:
            metrics["humana"]["total"] += 1
            if "humana" in hyp: metrics["humana"]["correct"] += 1
        elif "aetna" in expected:
            metrics["aetna"]["total"] += 1
            if "aetna" in hyp: metrics["aetna"]["correct"] += 1
        elif "unitedhealthcare" in expected:
            metrics["united"]["total"] += 1
            if "united" in hyp or "healthcare" in hyp: metrics["united"]["correct"] += 1
        elif "blue cross" in expected:
            metrics["blue_cross"]["total"] += 1
            if "blue cross" in hyp: metrics["blue_cross"]["correct"] += 1
            
        # TalkFlow
        if "talkflow" in expected or "talk flow" in expected:
            metrics["talkflow"]["total"] += 1
            if "talkflow" in hyp or "talk flow" in hyp: metrics["talkflow"]["correct"] += 1
            
    return metrics, total_wer / max(1, len(results))

def pct(c, t): 
    if t == 0: return "N/A"
    return f"{c}/{t} ({c/t*100:.1f}%)"

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
    manifest_path = "/app/test_set/human_review_manifest.csv"
    
    verified_utterances = []
    with open(manifest_path, "r", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["expected_text"].strip():
                verified_utterances.append(row)
                
    if len(verified_utterances) == 0:
        print("ERROR: No verified utterances found. Please fill 'expected_text' in human_review_manifest.csv")
        return
        
    print(f"Loaded {len(verified_utterances)} HUMAN-VERIFIED utterances.")
    
    models_to_test = ["Parakeet", "Nemotron", "Whisper"]
    model_results = {m: [] for m in models_to_test}
    latencies = {m: [] for m in models_to_test}
    
    # 1. Parakeet
    try:
        model = get_nemo_model("/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo")
        cfg = OmegaConf.create(OmegaConf.to_container(model.cfg.decoding, resolve=True))
        cfg.strategy = "greedy_batch"
        model.change_decoding_strategy(cfg)
        import soundfile as sf
        for item in verified_utterances:
            wav_path = "/app/phase3_human_review/" + item["file"]
            audio, _ = sf.read(wav_path)
            t0 = time.perf_counter_ns()
            transcripts = model.transcribe(audio=audio, return_hypotheses=False)
            t1 = time.perf_counter_ns()
            decode_ms = (t1 - t0) / 1_000_000
            
            text_obj = transcripts
            while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0: text_obj = text_obj[0]
            if hasattr(text_obj, 'text'): hyp = text_obj.text.strip()
            elif hasattr(text_obj, 'text_no_timesteps'): hyp = text_obj.text_no_timesteps.strip()
            else: hyp = str(text_obj).strip()
            
            model_results["Parakeet"].append({"wav": wav_path, "expected": item["expected_text"], "hyp": hyp})
            latencies["Parakeet"].append(decode_ms)
        del model
        gc.collect()
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"Error running Parakeet: {e}")

    # 2. Nemotron
    try:
        model = get_nemo_model("/app/models/nemotron-speech-streaming-en-0.6b/nemotron-speech-streaming-en-0.6b.nemo")
        cfg = OmegaConf.create(OmegaConf.to_container(model.cfg.decoding, resolve=True))
        cfg.strategy = "greedy_batch"
        model.change_decoding_strategy(cfg)
        import soundfile as sf
        for item in verified_utterances:
            wav_path = "/app/phase3_human_review/" + item["file"]
            audio, _ = sf.read(wav_path)
            t0 = time.perf_counter_ns()
            transcripts = model.transcribe(audio=audio, return_hypotheses=False)
            t1 = time.perf_counter_ns()
            decode_ms = (t1 - t0) / 1_000_000
            
            text_obj = transcripts
            while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0: text_obj = text_obj[0]
            if hasattr(text_obj, 'text'): hyp = text_obj.text.strip()
            elif hasattr(text_obj, 'text_no_timesteps'): hyp = text_obj.text_no_timesteps.strip()
            else: hyp = str(text_obj).strip()
            
            model_results["Nemotron"].append({"wav": wav_path, "expected": item["expected_text"], "hyp": hyp})
            latencies["Nemotron"].append(decode_ms)
        del model
        gc.collect()
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"Error running Nemotron: {e}")

    # 3. Whisper
    try:
        from faster_whisper import WhisperModel
        print("Loading Whisper large-v3-turbo...")
        model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type="float16")
        for item in verified_utterances:
            wav_path = "/app/phase3_human_review/" + item["file"]
            t0 = time.perf_counter_ns()
            segs, _ = model.transcribe(wav_path, language="en")
            hyp = " ".join([s.text for s in segs]).strip()
            t1 = time.perf_counter_ns()
            decode_ms = (t1 - t0) / 1_000_000
            
            model_results["Whisper"].append({"wav": wav_path, "expected": item["expected_text"], "hyp": hyp})
            latencies["Whisper"].append(decode_ms)
        del model
        gc.collect()
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"Error running Whisper: {e}")

    print("\n==================================================")
    print("10. PER-UTTERANCE COMPARISON")
    print("==================================================")
    for i, item in enumerate(verified_utterances):
        print("Expected:")
        print(f"    \"{item['expected_text']}\"")
        for m in models_to_test:
            if i < len(model_results[m]):
                print(f"{m}:")
                print(f"    \"{model_results[m][i]['hyp']}\"")
        print()
        
    print("\n==================================================")
    print("7-8. CRITICAL DOMAIN SCOREBOARD (RAW TRANSCRIPT)")
    print("==================================================")
    print(f"{'Metric':<25} | {'Parakeet':<20} | {'Nemotron':<20} | {'Whisper':<20}")
    print("-" * 90)
    
    scoreboards = {}
    wers = {}
    for m in models_to_test:
        if len(model_results[m]) > 0:
            mets, wer = compute_metrics(model_results[m])
            scoreboards[m] = mets
            wers[m] = wer
        else:
            scoreboards[m] = None
            wers[m] = 0.0

    def print_row(name, m_key, sub_key="correct"):
        vals = []
        for m in models_to_test:
            if scoreboards[m]:
                if m_key == "WER":
                    vals.append(f"{wers[m]:.3f}")
                else:
                    c = scoreboards[m][m_key][sub_key]
                    t = scoreboards[m][m_key]["total"]
                    vals.append(pct(c, t))
            else:
                vals.append("N/A")
        print(f"{name:<25} | {vals[0]:<20} | {vals[1]:<20} | {vals[2]:<20}")

    print_row("WER", "WER")
    print_row("Medicare Correct", "medicare")
    print_row("Medicaid Correct", "medicaid")
    print_row("Medicare/caid Confusion", "medicare_vs_medicaid", "confused")
    print_row("Part A Correct", "part_a")
    print_row("Part B Correct", "part_b")
    print_row("Part A/B Confusion", "part_a_vs_part_b", "confused")
    print_row("Negation", "negation")
    print_row("ZIP exact", "zip")
    print_row("Age exact", "age")
    print_row("Humana", "humana")
    print_row("Aetna", "aetna")
    print_row("UnitedHealthcare", "united")
    print_row("Blue Cross", "blue_cross")
    print_row("TalkFlow", "talkflow")

    print("\n==================================================")
    print("11. LATENCY SCOREBOARD (Pure Model Compute Time)")
    print("==================================================")
    print(f"{'Model':<15} | {'P50':<10} | {'P95':<10}")
    print("-" * 40)
    for m in models_to_test:
        if len(latencies[m]) > 0:
            arr = np.array(latencies[m])
            print(f"{m:<15} | {np.percentile(arr, 50):.1f}ms   | {np.percentile(arr, 95):.1f}ms")
        else:
            print(f"{m:<15} | N/A        | N/A")
            
    print("\n==================================================")
    print("12. FINAL DECISION RULE")
    print("==================================================")
    print("Waiting for human review decision. Do not automatically choose D.")

if __name__ == "__main__":
    main()

