# ruff: noqa
import csv
import gc
import time

import numpy as np
import torch
from faster_whisper import WhisperModel
from semantic_extractor import SemanticExtractor


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

def compute_semantic_metrics(results):
    entities = ["medicare", "medicaid", "part_a", "part_b", "negation", "zip", "age", "humana", "aetna", "united", "blue_cross", "talkflow"]
    
    metrics = {e: {"total_positive": 0, "correct_positive": 0, "eligible_negative": 0, "false_positive": 0} for e in entities}
    
    total_wer = 0.0
    for r in results:
        expected_text = r["expected"]
        hyp_text = r["hyp"]
        
        expected_semantics = SemanticExtractor.extract(expected_text)
        hyp_semantics = SemanticExtractor.extract(hyp_text)
        
        total_wer += calculate_wer(expected_text, hyp_text)
        
        # Map some keys
        expected_semantics["united"] = (expected_semantics["carrier"] == "united")
        hyp_semantics["united"] = (hyp_semantics["carrier"] == "united")
        
        expected_semantics["humana"] = (expected_semantics["carrier"] == "humana")
        hyp_semantics["humana"] = (hyp_semantics["carrier"] == "humana")
        
        expected_semantics["aetna"] = (expected_semantics["carrier"] == "aetna")
        hyp_semantics["aetna"] = (hyp_semantics["carrier"] == "aetna")
        
        expected_semantics["blue_cross"] = (expected_semantics["carrier"] == "blue cross")
        hyp_semantics["blue_cross"] = (hyp_semantics["carrier"] == "blue cross")
        
        expected_semantics["part_a"] = (expected_semantics["part_a"] == "yes")
        hyp_semantics["part_a"] = (hyp_semantics["part_a"] == "yes")
        
        expected_semantics["part_b"] = (expected_semantics["part_b"] == "yes")
        hyp_semantics["part_b"] = (hyp_semantics["part_b"] == "yes")
        
        for e in entities:
            # For exact matches like zip and age
            if e in ["zip", "age"]:
                exp_val = expected_semantics[e]
                hyp_val = hyp_semantics[e]
                
                if exp_val is not None:
                    metrics[e]["total_positive"] += 1
                    if hyp_val == exp_val: metrics[e]["correct_positive"] += 1
                else:
                    metrics[e]["eligible_negative"] += 1
                    if hyp_val is not None: metrics[e]["false_positive"] += 1
            else:
                exp_val = bool(expected_semantics[e])
                hyp_val = bool(hyp_semantics[e])
                
                if exp_val:
                    metrics[e]["total_positive"] += 1
                    if hyp_val: metrics[e]["correct_positive"] += 1
                else:
                    metrics[e]["eligible_negative"] += 1
                    if hyp_val: metrics[e]["false_positive"] += 1
            
    return metrics, total_wer / max(1, len(results))

def pct(c, t): 
    if t == 0: return "N/A"
    return f"{c}/{t} ({c/t*100:.1f}%)"

def get_state_prompt(category):
    if category == "medicare": return "Medicare, Medicaid"
    if category == "part_a": return "Medicare, Part A"
    if category == "part_b": return "Medicare, Part B"
    if category == "insurance": return "Humana, Aetna, UnitedHealthcare, Blue Cross"
    if category == "zip": return "ZIP code"
    return "TalkFlow"

def run_model(model, utterances, config_name):
    results = []
    latencies = []
    vrams = []
    print(f"\nRunning {config_name}")
    
    for item in utterances:
        wav_path = f"/app/test_set/phase3_v1/{item['file']}"
        
        # Decide prompt based on config_name
        prompt = None
        if "B: Core Medicare" in config_name:
            prompt = "Medicare, Medicaid, Part A, Part B"
        elif "C: Core + Insurance" in config_name:
            prompt = "Medicare, Medicaid, Part A, Part B, Humana, Aetna, UnitedHealthcare, Blue Cross"
        elif "D: State-Specific" in config_name:
            prompt = get_state_prompt(item["guessed_category"])
            
        t0 = time.perf_counter_ns()
        segs, _ = model.transcribe(
            wav_path,
            language="en",
            beam_size=1,
            temperature=0.0,
            vad_filter=False,
            condition_on_previous_text=False,
            word_timestamps=False,
            initial_prompt=prompt
        )
        hyp = " ".join([s.text for s in segs]).strip()
        t1 = time.perf_counter_ns()
        decode_ms = (t1 - t0) / 1_000_000
        
        results.append({"wav": wav_path, "expected": item["expected_text"], "hyp": hyp})
        latencies.append(decode_ms)
        vrams.append(torch.cuda.memory_allocated() / (1024 * 1024))
        
    mets, wer = compute_semantic_metrics(results)
    
    return {
        "metrics": mets,
        "wer": wer,
        "latencies": latencies,
        "results": results,
        "vram": max(vrams) if vrams else 0
    }

def print_scoreboard(runs, config_names):
    print("\n==================================================")
    print("CRITICAL DOMAIN SCOREBOARD (SEMANTIC EXTRACTION)")
    print("==================================================")
    header = f"{'Metric':<25} | " + " | ".join([f"{name:<25}" for name in config_names])
    print(header)
    print("-" * len(header))
    
    def print_row(name, m_key, sub_key="correct_positive", denom_key="total_positive"):
        vals = []
        for cname in config_names:
            run_data = runs[cname]
            if m_key == "WER":
                vals.append(f"{run_data['wer']:.3f}")
            else:
                mets = run_data["metrics"]
                count = mets[m_key][sub_key]
                total = mets[m_key][denom_key]
                vals.append(pct(count, total))
        row_str = f"{name:<25} | " + " | ".join([f"{v:<25}" for v in vals])
        print(row_str)

    print_row("WER", "WER")
    print_row("Medicare", "medicare")
    print_row("Medicaid", "medicaid")
    print_row("Part A", "part_a")
    print_row("Part B", "part_b")
    print_row("Negation", "negation")
    print_row("ZIP", "zip")
    print_row("Age", "age")
    print_row("Humana", "humana")
    print_row("Aetna", "aetna")
    print_row("UnitedHealthcare", "united")
    print_row("Blue Cross", "blue_cross")
    print_row("TalkFlow", "talkflow")
    
    print("\n--- False Insertions (FP / Eligible Negatives) ---")
    print_row("Medicare False Inst", "medicare", "false_positive", "eligible_negative")
    print_row("Medicaid False Inst", "medicaid", "false_positive", "eligible_negative")
    print_row("Part A False Inst", "part_a", "false_positive", "eligible_negative")
    print_row("Part B False Inst", "part_b", "false_positive", "eligible_negative")
    print_row("Humana False Inst", "humana", "false_positive", "eligible_negative")
    print_row("Aetna False Inst", "aetna", "false_positive", "eligible_negative")
    print_row("United False Inst", "united", "false_positive", "eligible_negative")
    print_row("Blue Cross False Inst", "blue_cross", "false_positive", "eligible_negative")
    print_row("TalkFlow False Inst", "talkflow", "false_positive", "eligible_negative")
    
    print("\n==================================================")
    print("LATENCY & COMPUTE SCOREBOARD")
    print("==================================================")
    header = f"{'Config':<30} | {'P50':<10} | {'P95':<10} | {'Max VRAM (MB)':<15}"
    print(header)
    print("-" * len(header))
    for cname in config_names:
        arr = np.array(runs[cname]["latencies"])
        vram = runs[cname]["vram"]
        print(f"{cname:<30} | {np.percentile(arr, 50):.1f}ms   | {np.percentile(arr, 95):.1f}ms   | {vram:.1f}")

def main():
    manifest_path = "/app/test_set/phase3_v1/manifest.csv"
    
    verified_utterances = []
    with open(manifest_path, "r", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["expected_text"].strip():
                verified_utterances.append(row)
                
    print(f"Loaded {len(verified_utterances)} HUMAN-VERIFIED utterances from Phase 3 regression corpus.")
    
    # 1. Ablation test with float16
    print("\n--- PHASE A: PROMPT ABLATION (float16) ---")
    model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type="float16")
    configs = [
        "A: No Prompt",
        "B: Core Medicare",
        "C: Core + Insurance",
        "D: State-Specific"
    ]
    runs = {}
    for c in configs:
        runs[c] = run_model(model, verified_utterances, c)
    print_scoreboard(runs, configs)
    
    # Free up memory
    del model
    gc.collect()
    torch.cuda.empty_cache()
    
    # 2. Compute types test with State-Specific prompt (assuming it's best)
    print("\n--- PHASE B: COMPUTE TYPES (State-Specific Prompt) ---")
    ct_runs = {}
    compute_types = ["float16", "int8_float16", "int8"]
    
    for ct in compute_types:
        try:
            model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type=ct)
            ct_runs[ct] = run_model(model, verified_utterances, f"D: State-Specific ({ct})")
            del model
            gc.collect()
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"Failed to load with {ct}: {e}")
            
    print_scoreboard(ct_runs, list(ct_runs.keys()))

if __name__ == "__main__":
    main()

