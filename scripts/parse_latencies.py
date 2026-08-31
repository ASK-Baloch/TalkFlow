import re
import numpy as np

def main():
    log_file = "gateway3.log"
    with open(log_file, "r", encoding="utf-16le") as f:
        content = f.read()
        
    stale_count = content.count("ASR FINAL_TENTATIVE discarded (stale)")
    utilized_pre = content.count("utilizing FINAL_TENTATIVE result (pre-arrived)")
    utilized_inflight = content.count("FINAL_TENTATIVE->FINAL (speculative hit)")
    utilized_count = utilized_pre + utilized_inflight
    resumed_cancels = content.count("VAD pending_end_cancelled")
    
    acoustic_latencies = []
    for m in re.finditer(r'acoustic_end_to_final_ms=([0-9.]+)', content):
        acoustic_latencies.append(float(m.group(1)))
                
    if not acoustic_latencies:
        print("No latencies found!")
        return
        
    print(f"Total finals: {len(acoustic_latencies)}")
    print(f"Speculative finals utilized: {utilized_count}")
    print(f"Stale speculative finals discarded: {stale_count}")
    
    print("\nLive Acoustic End -> Final Transcript Latency (T0 -> T5):")
    print(f"  P50: {np.percentile(acoustic_latencies, 50):.1f} ms")
    print(f"  P90: {np.percentile(acoustic_latencies, 90):.1f} ms")
    print(f"  P95: {np.percentile(acoustic_latencies, 95):.1f} ms")
    print(f"  Max: {np.max(acoustic_latencies):.1f} ms")

if __name__ == "__main__":
    main()
