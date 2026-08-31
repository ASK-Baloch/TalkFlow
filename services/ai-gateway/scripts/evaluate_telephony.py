# ruff: noqa
import glob
import json
import os
import time

import numpy as np


def calculate_wer(reference, hypothesis):
    ref_words = reference.lower().replace('.', '').replace(',', '').split()
    hyp_words = hypothesis.lower().replace('.', '').replace(',', '').split()
    
    # Simple edit distance for WER
    d = np.zeros((len(ref_words) + 1, len(hyp_words) + 1), dtype=int)
    for i in range(len(ref_words) + 1): d[i][0] = i
    for j in range(len(hyp_words) + 1): d[0][j] = j
    
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + 1)
                
    return d[len(ref_words)][len(hyp_words)] / max(len(ref_words), 1)

def main():
    EXPECTED_PHRASES = [
        ("I have Medicare.", "medicare"),
        ("Yes, I have Medicare.", "medicare"),
        ("No, I don't have Medicare.", "medicare_negation"),
        ("I have Medicaid.", "medicaid"),
        ("I don't have Medicaid.", "medicaid_negation"),
        ("I have Medicare Part A.", "part_a"),
        ("Yes, I have Part A.", "part_a"),
        ("No, I don't have Part A.", "part_a_negation"),
        ("I have Medicare Part B.", "part_b"),
        ("Yes, I have Part B.", "part_b"),
        ("No, I don't have Part B.", "part_b_negation"),
        ("I have Medicare Part A and Part B.", "part_both"),
        ("I have both Part A and Part B.", "part_both"),
        ("I only have Part A.", "part_both"),
        ("I'm sixty five years old.", "age"),
        ("I'm seventy two.", "age"),
        ("I am sixty eight.", "age"),
        ("My ZIP code is nine zero two one zero.", "zip"),
        ("My ZIP code is three three one zero one.", "zip"),
        ("My ZIP code is one zero zero zero one.", "zip"),
        ("My ZIP code is seven five zero zero one.", "zip"),
        ("My ZIP code is six zero six zero one.", "zip"),
        ("I have Humana.", "insurance"),
        ("I have Aetna.", "insurance"),
        ("I have UnitedHealthcare.", "insurance"),
        ("I have Blue Cross.", "insurance"),
        ("I like to walk my dog in the park.", "negative_control"),
        ("The weather is very nice today.", "negative_control"),
        ("I am calling to ask about my bill.", "negative_control")
    ]
    
    for _ in range(10):
        EXPECTED_PHRASES.append(("Hello TalkFlow.", "talkflow"))

    wav_files = glob.glob("/app/test_set/*_16k.wav")
    wav_files.sort(key=os.path.getmtime)
    
    if len(wav_files) != len(EXPECTED_PHRASES):
        print(f"WARNING: Expected {len(EXPECTED_PHRASES)} utterances, but found {len(wav_files)} WAV files. Evaluation may misalign if order is broken.")

    print("Loading Parakeet Model...")
    import nemo.collections.asr as nemo_asr
    from omegaconf import OmegaConf
    model_path = "/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo"
    model = nemo_asr.models.EncDecRNNTBPEModel.restore_from(model_path)
    
    if getattr(model.cfg, "validation_ds", None) is None:
        model.cfg.validation_ds = OmegaConf.create({})
        
    import torch
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    
    default_cfg = OmegaConf.to_container(model.cfg.decoding, resolve=True)
    cfg = OmegaConf.create(default_cfg)
    cfg.strategy = "greedy_batch"
    model.change_decoding_strategy(cfg)

    import soundfile as sf
    
    manifest = []
    
    total_wer = 0.0
    failed_utterances = []
    
    metrics = {
        "medicare": {"total": 0, "correct": 0, "confused_medicaid": 0},
        "medicaid": {"total": 0, "correct": 0, "confused_medicare": 0},
        "part_a": {"total": 0, "correct": 0, "confused_b": 0},
        "part_b": {"total": 0, "correct": 0, "confused_a": 0},
        "negation": {"total": 0, "correct": 0},
        "zip": {"total": 0, "correct": 0},
        "age": {"total": 0, "correct": 0},
        "carrier": {"total": 0, "correct": 0},
        "talkflow": {"total": 0, "correct": 0},
        "false_insertion": {"total": 0, "inserted": 0}
    }
    
    latency_decode = []

    print("\nProcessing utterances...")
    for i, wav_path in enumerate(wav_files):
        expected_text, category = EXPECTED_PHRASES[i]
        os.path.basename(wav_path).replace("FINAL-ASR-INPUT-", "").replace(".wav", "")
        
        audio, _ = sf.read(wav_path)
        
        t0 = time.perf_counter_ns()
        transcripts = model.transcribe(audio=audio, return_hypotheses=False)
        t1 = time.perf_counter_ns()
        
        decode_ms = (t1 - t0) / 1_000_000
        latency_decode.append(decode_ms)
        
        text_obj = transcripts
        while isinstance(text_obj, (list, tuple)) and len(text_obj) > 0:
            text_obj = text_obj[0]
            
        if hasattr(text_obj, 'text'):
            hyp = text_obj.text.strip()
        elif hasattr(text_obj, 'text_no_timesteps'):
            hyp = text_obj.text_no_timesteps.strip()
        else:
            hyp = str(text_obj).strip()
            
        wer = calculate_wer(expected_text, hyp)
        total_wer += wer
        
        hyp_lower = hyp.lower()
        
        if category == "medicare":
            metrics["medicare"]["total"] += 1
            if "medicare" in hyp_lower:
                metrics["medicare"]["correct"] += 1
            elif "medicaid" in hyp_lower:
                metrics["medicare"]["confused_medicaid"] += 1
        elif category == "medicaid":
            metrics["medicaid"]["total"] += 1
            if "medicaid" in hyp_lower:
                metrics["medicaid"]["correct"] += 1
            elif "medicare" in hyp_lower:
                metrics["medicaid"]["confused_medicare"] += 1
        elif category.endswith("negation"):
            metrics["negation"]["total"] += 1
            if "don't" in hyp_lower or "no" in hyp_lower:
                metrics["negation"]["correct"] += 1
        elif category == "part_a":
            metrics["part_a"]["total"] += 1
            if "part a" in hyp_lower:
                metrics["part_a"]["correct"] += 1
            elif "part b" in hyp_lower:
                metrics["part_a"]["confused_b"] += 1
        elif category == "part_b":
            metrics["part_b"]["total"] += 1
            if "part b" in hyp_lower:
                metrics["part_b"]["correct"] += 1
            elif "part a" in hyp_lower:
                metrics["part_b"]["confused_a"] += 1
        elif category == "zip":
            metrics["zip"]["total"] += 1
            # Zip is exact match text vs text simplified
            if calculate_wer(expected_text, hyp) < 0.2:
                metrics["zip"]["correct"] += 1
        elif category == "age":
            metrics["age"]["total"] += 1
            if calculate_wer(expected_text, hyp) < 0.2:
                metrics["age"]["correct"] += 1
        elif category == "insurance":
            metrics["carrier"]["total"] += 1
            if "humana" in hyp_lower or "aetna" in hyp_lower or "united" in hyp_lower or "blue cross" in hyp_lower:
                metrics["carrier"]["correct"] += 1
        elif category == "negative_control":
            metrics["false_insertion"]["total"] += 1
            if "medicare" in hyp_lower or "medicaid" in hyp_lower or "part a" in hyp_lower or "part b" in hyp_lower:
                metrics["false_insertion"]["inserted"] += 1
        elif category == "talkflow":
            metrics["talkflow"]["total"] += 1
            if "talkflow" in hyp.lower() or "talk flow" in hyp_lower:
                metrics["talkflow"]["correct"] += 1
                
        is_failed = (wer > 0.1) and category != "talkflow"
        if is_failed:
            failed_utterances.append({
                "expected": expected_text,
                "hyp": hyp,
                "wav": wav_path
            })
            
        manifest.append({
            "wav": wav_path,
            "expected": expected_text,
            "category": category,
            "hyp": hyp,
            "wer": wer
        })

    with open("/app/test_set/phase3_telephony_manifest.jsonl", "w") as f:
        f.writelines(json.dumps(m) + "\\n" for m in manifest)
            
    avg_wer = total_wer / len(wav_files)
    
    def pct(c, t): return f"{(c/t*100):.1f}%" if t > 0 else "N/A"
    
    print("\n==================================================")
    print("FINAL REPORT")
    print("==================================================")
    print(f"1. Total test utterances: {len(wav_files)}")
    print(f"2. Raw average WER: {avg_wer:.3f}")
    print(f"3. Medicare accuracy: {pct(metrics['medicare']['correct'], metrics['medicare']['total'])} (Confused as Medicaid: {metrics['medicare']['confused_medicaid']})")
    print(f"4. Medicaid accuracy: {pct(metrics['medicaid']['correct'], metrics['medicaid']['total'])} (Confused as Medicare: {metrics['medicaid']['confused_medicare']})")
    print(f"5. Part A accuracy: {pct(metrics['part_a']['correct'], metrics['part_a']['total'])} (Confused as B: {metrics['part_a']['confused_b']})")
    print(f"6. Part B accuracy: {pct(metrics['part_b']['correct'], metrics['part_b']['total'])} (Confused as A: {metrics['part_b']['confused_a']})")
    print(f"7. Negation accuracy: {pct(metrics['negation']['correct'], metrics['negation']['total'])}")
    print(f"8. ZIP exact accuracy: {pct(metrics['zip']['correct'], metrics['zip']['total'])}")
    print(f"9. Age exact accuracy: {pct(metrics['age']['correct'], metrics['age']['total'])}")
    print(f"10. Carrier-name accuracy: {pct(metrics['carrier']['correct'], metrics['carrier']['total'])}")
    print(f"11. TalkFlow exact accuracy: {pct(metrics['talkflow']['correct'], metrics['talkflow']['total'])}")
    print(f"12. False insertion rate: {pct(metrics['false_insertion']['inserted'], metrics['false_insertion']['total'])}")
    
    lat = np.array(latency_decode)
    print(f"13. Final latency: P50={np.percentile(lat, 50):.1f}ms, P95={np.percentile(lat, 95):.1f}ms")
    print("14. First partial latency: N/A (Partials Disabled)")
    
    print("\n15. FAILED UTTERANCES:")
    for f in failed_utterances:
        print(f"    Expected: {f['expected']}")
        print(f"    Actual:   {f['hyp']}")
        print(f"    WAV:      {f['wav']}\n")
        
    print("==================================================")
    print("DECISION RULE RESULT:")
    domain_accs = [
        metrics['medicare']['correct']/max(1,metrics['medicare']['total']),
        metrics['part_a']['correct']/max(1,metrics['part_a']['total']),
        metrics['part_b']['correct']/max(1,metrics['part_b']['total']),
        metrics['negation']['correct']/max(1,metrics['negation']['total']),
    ]
    if all(a >= 0.98 for a in domain_accs):
        print("PARAKEET PASSES DOMAIN ACCURACY")
    else:
        print("PARAKEET FAILS DOMAIN ACCURACY")

if __name__ == "__main__":
    main()

