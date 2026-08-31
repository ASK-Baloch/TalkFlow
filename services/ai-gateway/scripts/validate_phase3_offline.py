# ruff: noqa
import csv

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
    entities = ["medicare", "medicaid", "part_a", "part_b", "negation", "zip", "age", "humana", "aetna", "united", "blue_cross", "talkflow"]
    
    metrics = {e: {"total_positive": 0, "correct_positive": 0, "eligible_negative": 0, "false_positive": 0} for e in entities}
    
    medicare_medicaid_confusion = {"eligible": 0, "count": 0}
    parta_partb_confusion = {"eligible": 0, "count": 0}
    
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
        
        # Confusions
        if expected_semantics["medicare"] or expected_semantics["medicaid"]:
            medicare_medicaid_confusion["eligible"] += 1
            if expected_semantics["medicare"] and not expected_semantics["medicaid"] and hyp_semantics["medicaid"] and not hyp_semantics["medicare"] or expected_semantics["medicaid"] and not expected_semantics["medicare"] and hyp_semantics["medicare"] and not hyp_semantics["medicaid"]:
                medicare_medicaid_confusion["count"] += 1
                
        if expected_semantics["part_a"] or expected_semantics["part_b"]:
            parta_partb_confusion["eligible"] += 1
            if expected_semantics["part_a"] and not expected_semantics["part_b"] and hyp_semantics["part_b"] and not hyp_semantics["part_a"] or expected_semantics["part_b"] and not expected_semantics["part_a"] and hyp_semantics["part_a"] and not hyp_semantics["part_b"]:
                parta_partb_confusion["count"] += 1
        
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
                    if hyp_val: 
                        metrics[e]["false_positive"] += 1
                        if e == "medicaid":
                            print("\n*** MEDICAID FALSE INSERTION IDENTIFIED ***")
                            print(f"WAV: {r['wav']}")
                            print(f"Expected: '{expected_text}'")
                            print(f"Hypothesis: '{hyp_text}'")
                            print(f"Prompt used: '{r.get('prompt', 'None')}'")
                            print("*******************************************\n")
            
    return metrics, medicare_medicaid_confusion, parta_partb_confusion, total_wer / max(1, len(results))

def get_state_prompt(category):
    if category == "medicare": return "Medicare, Medicaid"
    if category == "part_a": return "Medicare, Part A"
    if category == "part_b": return "Medicare, Part B"
    if category == "insurance": return "Humana, Aetna, UnitedHealthcare, Blue Cross"
    if category == "zip": return "ZIP code"
    return "TalkFlow"

def run_model(model, utterances):
    results = []
    
    for item in utterances:
        wav_path = f"/app/test_set/phase3_v1/{item['file']}"
        prompt = get_state_prompt(item["guessed_category"])
            
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
        results.append({"wav": wav_path, "expected": item["expected_text"], "hyp": hyp, "prompt": prompt})
        
    return compute_semantic_metrics(results)

def main():
    manifest_path = "/app/test_set/phase3_v1/manifest.csv"
    
    verified_utterances = []
    with open(manifest_path, "r", encoding="cp1252") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["expected_text"].strip():
                verified_utterances.append(row)
                
    model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type="int8_float16")
    
    metrics, mm_conf, p_conf, wer = run_model(model, verified_utterances)
    
    print("\n==================================================")
    print("PHASE 3 ACCURACY SCOREBOARD")
    print("==================================================")
    print(f"WER: {wer:.3f}")
    
    def prnt(name, key):
        c = metrics[key]["correct_positive"]
        t = metrics[key]["total_positive"]
        print(f"{name}: {c} / {t}")
        
    prnt("Medicare", "medicare")
    prnt("Medicaid", "medicaid")
    prnt("Part A", "part_a")
    prnt("Part B", "part_b")
    
    print(f"Medicare-vs-Medicaid confusion: {mm_conf['count']} / {mm_conf['eligible']}")
    print(f"Part-A-vs-Part-B confusion: {p_conf['count']} / {p_conf['eligible']}")
    
    prnt("Negation", "negation")
    prnt("ZIP exact", "zip")
    prnt("Age exact", "age")
    prnt("Humana", "humana")
    prnt("Aetna", "aetna")
    prnt("UnitedHealthcare", "united")
    prnt("Blue Cross", "blue_cross")
    prnt("TalkFlow", "talkflow")
    
    print("\n--- False Critical-Domain Insertions ---")
    def prnt_false(name, key):
        c = metrics[key]["false_positive"]
        t = metrics[key]["eligible_negative"]
        print(f"{name}: {c} / {t}")
        
    prnt_false("Medicare", "medicare")
    prnt_false("Medicaid", "medicaid")
    prnt_false("Part A", "part_a")
    prnt_false("Part B", "part_b")
    prnt_false("Humana", "humana")
    prnt_false("Aetna", "aetna")
    prnt_false("UnitedHealthcare", "united")
    prnt_false("Blue Cross", "blue_cross")
    prnt_false("TalkFlow", "talkflow")
    
if __name__ == "__main__":
    main()

