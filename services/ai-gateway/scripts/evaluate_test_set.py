# ruff: noqa
import glob
import os
import re
import sys
from dataclasses import dataclass

try:
    import nemo.collections.asr as nemo_asr
except ImportError:
    print("NeMo is not installed.")
    sys.exit(1)

EXPECTED_PHRASES = [
    "I have Medicare.",
    "I don't have Medicare.",
    "I have Medicaid.",
    "I have Medicare Part A.",
    "I don't have Medicare Part A.",
    "I have Medicare Part B.",
    "I don't have Medicare Part B.",
    "I have both Medicare Part A and Part B.",
    "I only have Part A.",
    "I only have Part B.",
    "Yes.",
    "No.",
    "Yes I do.",
    "No I don't.",
    "I am 65 years old.",
    "I am 72 years old.",
    "I'm sixty eight.",
    "My ZIP code is 75001.",
    "My ZIP code is 90210.",
    "My ZIP code is 33101.",
    "My insurance is Humana.",
    "I have Aetna.",
    "I have UnitedHealthcare.",
    "I have Blue Cross.",
    "I have medical insurance.",
    "I need medical help.",
    "I don't know what Medicare is.",
    "I have Medicaid, not Medicare.",
    "I have Medicare, not Medicaid.",
    "I don't have Part B."
]

@dataclass
class Extraction:
    has_medicare: bool | None = None
    has_medicaid: bool | None = None
    part_a: bool | None = None
    part_b: bool | None = None
    is_negation: bool | None = None
    zip_code: str | None = None
    age: str | None = None
    carrier: str | None = None
    yes_no: bool | None = None

def extract_fields(text: str) -> Extraction:
    text_lower = text.lower()
    
    e = Extraction()
    
    # Simple rule-based extraction for demonstration
    if "medicare" in text_lower:
        e.has_medicare = True
    if "medicaid" in text_lower:
        e.has_medicaid = True
        
    if "part a" in text_lower:
        e.part_a = True
    if "part b" in text_lower:
        e.part_b = True
        
    negations = ["don't", "do not", "no", "not"]
    e.is_negation = any(n in text_lower for n in negations)
    
    # ZIP
    match_zip = re.search(r'\b\d{5}\b', text_lower)
    if match_zip:
        e.zip_code = match_zip.group(0)
        
    # Age
    match_age = re.search(r'\b(\d{2}|sixty\s*eight)\b', text_lower)
    if match_age:
        e.age = match_age.group(1)
        
    # Carrier
    carriers = ["humana", "aetna", "united", "blue cross"]
    for c in carriers:
        if c in text_lower:
            e.carrier = c
            
    # Yes/No
    if text_lower.startswith("yes"):
        e.yes_no = True
    elif text_lower.startswith("no"):
        e.yes_no = False
        
    return e

def compare_extraction(pred: Extraction, expected: Extraction) -> dict:
    scores = {}
    if expected.has_medicare is not None:
        scores["medicare_presence"] = (pred.has_medicare == expected.has_medicare)
    if expected.has_medicaid is not None:
        scores["medicaid_presence"] = (pred.has_medicaid == expected.has_medicaid)
    if expected.part_a is not None:
        scores["part_a"] = (pred.part_a == expected.part_a)
    if expected.part_b is not None:
        scores["part_b"] = (pred.part_b == expected.part_b)
    if expected.is_negation is not None:
        scores["negation"] = (pred.is_negation == expected.is_negation)
    if expected.zip_code is not None:
        scores["zip"] = (pred.zip_code == expected.zip_code)
    if expected.age is not None:
        scores["age"] = (pred.age == expected.age)
    if expected.carrier is not None:
        scores["carrier"] = (pred.carrier == expected.carrier)
    if expected.yes_no is not None:
        scores["yes_no"] = (pred.yes_no == expected.yes_no)
        
    return scores

def run_eval(test_set_dir: str):
    # Only pick 16k files for ASR
    files = glob.glob(os.path.join(test_set_dir, "*_16k.wav"))
    files.sort(key=os.path.getmtime)
    
    if not files:
        print("No files found in test_set!")
        return
        
    if len(files) != len(EXPECTED_PHRASES):
        print(f"Warning: Found {len(files)} files, but expected {len(EXPECTED_PHRASES)}.")
    
    print("Loading Parakeet Model...")
    model_path = "/app/models/parakeet-unified-en-0.6b/parakeet-unified-en-0.6b.nemo"
    model = nemo_asr.models.EncDecRNNTBPEModel.restore_from(model_path)
    
    from omegaconf import OmegaConf
    if getattr(model.cfg, "validation_ds", None) is None:
        model.cfg.validation_ds = OmegaConf.create({})
        
    import torch
    if torch.cuda.is_available():
        model = model.cuda()
    model.eval()
    
    # Disable bias
    model.change_decoding_strategy(model.cfg.decoding)
    
    results = []
    
    for i, file in enumerate(files):
        expected_text = EXPECTED_PHRASES[i] if i < len(EXPECTED_PHRASES) else "UNKNOWN"
        print(f"Transcribing {file} (Expected: {expected_text})...")
        
        import soundfile as sf
        audio, _sr = sf.read(file)
        
        if len(audio) == 0:
            print("Empty audio file!")
            continue
            
        transcripts = model.transcribe(audio=audio)
        text = transcripts[0] if isinstance(transcripts, tuple) else transcripts
        if isinstance(text, list): text = text[0]
        if hasattr(text, 'text'): text = text.text
        
        pred_ext = extract_fields(text)
        exp_ext = extract_fields(expected_text)
        
        scores = compare_extraction(pred_ext, exp_ext)
        
        results.append({
            "expected": expected_text,
            "actual": text,
            "scores": scores
        })
        
    # Summarize
    print("\n\n=== RAW TRANSCRIPTION & FIELD EXTRACTION REPORT ===")
    category_totals = {}
    category_correct = {}
    
    for r in results:
        print(f"\nExpected: {r['expected']}")
        print(f"Actual:   {r['actual']}")
        raw_exact = (r['expected'].lower().replace('.','').replace(',','') == r['actual'].lower().replace('.','').replace(',',''))
        print(f"Raw Exact Match: {raw_exact}")
        print(f"Field Scores: {r['scores']}")
        
        for k, v in r['scores'].items():
            category_totals[k] = category_totals.get(k, 0) + 1
            if v:
                category_correct[k] = category_correct.get(k, 0) + 1
                
    print("\n\n=== SUMMARY ACCURACY ===")
    for k in category_totals:
        acc = (category_correct.get(k, 0) / category_totals[k]) * 100
        print(f"{k.upper()}: {acc:.1f}% ({category_correct.get(k, 0)}/{category_totals[k]})")
        
if __name__ == "__main__":
    run_eval("/app/test_set")

