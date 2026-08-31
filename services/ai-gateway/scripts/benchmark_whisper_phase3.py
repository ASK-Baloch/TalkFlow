# ruff: noqa
import csv
import time

import numpy as np
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
    metrics = {
        "medicare": {"total": 0, "correct": 0},
        "medicaid": {"total": 0, "correct": 0},
        "part_a": {"total": 0, "correct": 0},
        "part_b": {"total": 0, "correct": 0},
        "negation": {"total": 0, "correct": 0},
        "zip": {"total": 0, "correct": 0},
        "age": {"total": 0, "correct": 0},
        "humana": {"total": 0, "correct": 0},
        "aetna": {"total": 0, "correct": 0},
        "united": {"total": 0, "correct": 0},
        "blue_cross": {"total": 0, "correct": 0},
        "talkflow": {"total": 0, "correct": 0},
        "false_insertion": {"total": 0, "count": 0}
    }
    
    total_wer = 0.0
    for r in results:
        expected_text = r["expected"]
        hyp_text = r["hyp"]
        
        expected_semantics = SemanticExtractor.extract(expected_text)
        hyp_semantics = SemanticExtractor.extract(hyp_text)
        
        total_wer += calculate_wer(expected_text, hyp_text)
        
        # Track false insertions
        metrics["false_insertion"]["total"] += 1
        has_false_insertion = False
        
        # Medicare
        if expected_semantics["medicare"]:
            metrics["medicare"]["total"] += 1
            if hyp_semantics["medicare"]: metrics["medicare"]["correct"] += 1
        elif hyp_semantics["medicare"]:
            has_false_insertion = True
            
        # Medicaid
        if expected_semantics["medicaid"]:
            metrics["medicaid"]["total"] += 1
            if hyp_semantics["medicaid"]: metrics["medicaid"]["correct"] += 1
        elif hyp_semantics["medicaid"]:
            has_false_insertion = True
            
        # Part A
        if expected_semantics["part_a"] == "yes":
            metrics["part_a"]["total"] += 1
            if hyp_semantics["part_a"] == "yes": metrics["part_a"]["correct"] += 1
        elif hyp_semantics["part_a"] == "yes":
            has_false_insertion = True
            
        # Part B
        if expected_semantics["part_b"] == "yes":
            metrics["part_b"]["total"] += 1
            if hyp_semantics["part_b"] == "yes": metrics["part_b"]["correct"] += 1
        elif hyp_semantics["part_b"] == "yes":
            has_false_insertion = True
            
        # Negation
        if expected_semantics["negation"]:
            metrics["negation"]["total"] += 1
            if hyp_semantics["negation"]: metrics["negation"]["correct"] += 1
            
        # ZIP
        if expected_semantics["zip"]:
            metrics["zip"]["total"] += 1
            if hyp_semantics["zip"] == expected_semantics["zip"]: metrics["zip"]["correct"] += 1
            
        # Age
        if expected_semantics["age"]:
            metrics["age"]["total"] += 1
            if hyp_semantics["age"] == expected_semantics["age"]: metrics["age"]["correct"] += 1
            
        # Carriers
        carriers_map = {"humana": "humana", "aetna": "aetna", "united": "united", "blue cross": "blue_cross"}
        for c, key in carriers_map.items():
            if expected_semantics["carrier"] == c:
                metrics[key]["total"] += 1
                if hyp_semantics["carrier"] == c: metrics[key]["correct"] += 1
            elif hyp_semantics["carrier"] == c:
                has_false_insertion = True
                
        # TalkFlow
        if expected_semantics["talkflow"]:
            metrics["talkflow"]["total"] += 1
            if hyp_semantics["talkflow"]: metrics["talkflow"]["correct"] += 1
        elif hyp_semantics["talkflow"]:
            has_false_insertion = True
            
        if has_false_insertion:
            metrics["false_insertion"]["count"] += 1
            
    return metrics, total_wer / max(1, len(results))

def pct(c, t): 
    if t == 0: return "N/A"
    return f"{c}/{t} ({c/t*100:.1f}%)"

def run_model(model, utterances, config_name, beam_size, initial_prompt=None):
    results = []
    latencies = []
    print(f"\nRunning {config_name} (beam={beam_size}, prompt={'Yes' if initial_prompt else 'No'})")
    
    for item in utterances:
        wav_path = f"/app/test_set/phase3_v1/{item['file']}"
        
        t0 = time.perf_counter_ns()
        segs, _ = model.transcribe(
            wav_path,
            language="en",
            beam_size=beam_size,
            temperature=0.0,
            vad_filter=False,
            condition_on_previous_text=False,
            initial_prompt=initial_prompt
        )
        hyp = " ".join([s.text for s in segs]).strip()
        t1 = time.perf_counter_ns()
        decode_ms = (t1 - t0) / 1_000_000
        
        results.append({"wav": wav_path, "expected": item["expected_text"], "hyp": hyp})
        latencies.append(decode_ms)
        
    mets, wer = compute_semantic_metrics(results)
    
    return {
        "metrics": mets,
        "wer": wer,
        "latencies": latencies,
        "results": results
    }

def main():
    manifest_path = "/app/test_set/phase3_v1/manifest.csv"
    
    verified_utterances = []
    with open(manifest_path, "r", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["expected_text"].strip():
                verified_utterances.append(row)
                
    print(f"Loaded {len(verified_utterances)} HUMAN-VERIFIED utterances from Phase 3 regression corpus.")
    
    print("Loading Whisper large-v3-turbo...")
    model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type="float16")
    
    configs = [
        {"name": "Baseline (b=1)", "beam_size": 1, "initial_prompt": None},
        {"name": "Low-Latency (b=2)", "beam_size": 2, "initial_prompt": None},
        {"name": "Prompted (b=1)", "beam_size": 1, "initial_prompt": "Medicare, Medicaid, Part A, Part B, TalkFlow, Humana, Aetna, Blue Cross, UnitedHealthcare"}
    ]
    
    runs = {}
    for c in configs:
        runs[c["name"]] = run_model(model, verified_utterances, c["name"], c["beam_size"], c["initial_prompt"])
        
    print("\n==================================================")
    print("CRITICAL DOMAIN SCOREBOARD (SEMANTIC EXTRACTION)")
    print("==================================================")
    config_names = [c["name"] for c in configs]
    header = f"{'Metric':<25} | " + " | ".join([f"{name:<18}" for name in config_names])
    print(header)
    print("-" * len(header))
    
    def print_row(name, m_key, sub_key="correct"):
        vals = []
        for cname in config_names:
            run_data = runs[cname]
            if m_key == "WER":
                vals.append(f"{run_data['wer']:.3f}")
            else:
                mets = run_data["metrics"]
                count = mets[m_key][sub_key]
                total = mets[m_key]["total"]
                vals.append(pct(count, total))
        row_str = f"{name:<25} | " + " | ".join([f"{v:<18}" for v in vals])
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
    print_row("False Insertions", "false_insertion", "count")
    
    print("\n==================================================")
    print("LATENCY SCOREBOARD (Pure Model Compute Time)")
    print("==================================================")
    header = f"{'Config':<20} | {'P50':<10} | {'P95':<10}"
    print(header)
    print("-" * len(header))
    for cname in config_names:
        arr = np.array(runs[cname]["latencies"])
        print(f"{cname:<20} | {np.percentile(arr, 50):.1f}ms   | {np.percentile(arr, 95):.1f}ms")

if __name__ == "__main__":
    main()

