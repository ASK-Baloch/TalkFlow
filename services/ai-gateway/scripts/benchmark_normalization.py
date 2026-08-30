import time
import sys
import os

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.realtime.asr.normalization import get_domain_normalizer

def benchmark():
    normalizer = get_domain_normalizer()
    
    test_cases = [
        "TalkFlow",
        "Hello TalkFlow",
        "Welcome to TalkFlow",
        "This is TalkFlow",
        "TalkFlow Medicare",
        "Hello, top flow.",
        "Do you have Medicare part bee?",
        "I have Medicare part ay.",
        "The top of the pipe has good flow."  # negative test
    ]
    
    print("=" * 60)
    print("NORMALIZATION BENCHMARK".center(60))
    print("=" * 60)
    
    total_ms = 0
    
    for i, raw in enumerate(test_cases):
        # Determine context based on the test
        context = ["ASK_PART_A", "ASK_PART_B"] if "part" in raw.lower() else []
        
        start = time.perf_counter_ns()
        normalized, corrections = normalizer.normalize(raw, context_hints=context)
        elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000.0
        total_ms += elapsed_ms
        
        print(f"TEST {i+1}:")
        print(f"RAW:        {raw}")
        print(f"NORMALIZED: {normalized}")
        print(f"LATENCY:    {elapsed_ms:.3f} ms")
        if corrections:
            print(f"CORRECTED:  yes ({len(corrections)})")
        print("-" * 60)
        
    avg = total_ms / len(test_cases)
    print(f"AVERAGE LATENCY: {avg:.4f} ms")
    
if __name__ == "__main__":
    benchmark()
