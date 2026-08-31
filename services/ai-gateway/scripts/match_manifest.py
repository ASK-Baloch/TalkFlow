import os
import glob
import json
import difflib

def main():
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "faster-whisper"])
        from faster_whisper import WhisperModel

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

    print("Loading Whisper...")
    model = WhisperModel("/app/models/large-v3-turbo-ct2", device="cuda", compute_type="float16")
    wav_files = glob.glob("/app/test_set/*_16k.wav")
    wav_files.sort(key=os.path.getmtime)

    manifest = []
    category_counts = {}
    
    print(f"Total WAV files found: {len(wav_files)}")
    
    for w in wav_files:
        segs, _ = model.transcribe(w, language="en")
        text = " ".join([s.text for s in segs]).strip()
        
        best_match = None
        best_score = 0
        for exp, cat in EXPECTED_PHRASES:
            score = difflib.SequenceMatcher(None, text.lower(), exp.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = (exp, cat)
                
        utterance_id = os.path.basename(w).replace("_16k.wav", "")
        if best_score > 0.6:  # Threshold for valid mapping
            manifest.append({
                "wav": w,
                "expected": best_match[0],
                "category": best_match[1],
                "utterance_id": utterance_id
            })
            category_counts[best_match[1]] = category_counts.get(best_match[1], 0) + 1
            print(f"Mapped {utterance_id} | Whisper: {text} | Expected: {best_match[0]}")
            EXPECTED_PHRASES.remove((best_match[0], best_match[1]))
        else:
            print(f"EXCLUDED {utterance_id} | Whisper: {text} | Best match was '{best_match[0]}' with score {best_score:.2f}")

    print("\n--- Manifest Summary ---")
    print(f"Total WAV files: {len(wav_files)}")
    print(f"Total labeled WAVs: {len(manifest)}")
    print(f"Total excluded WAVs: {len(wav_files) - len(manifest)}")
    print("\nCategory counts:")
    for k, v in category_counts.items():
        print(f"  {k}: {v}")
        
    with open("/app/test_set/phase3_manifest.jsonl", "w") as f:
        for m in manifest:
            f.write(json.dumps(m) + "\\n")
    print("Saved /app/test_set/phase3_manifest.jsonl")

if __name__ == "__main__":
    main()
