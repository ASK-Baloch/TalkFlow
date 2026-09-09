import asyncio
import time
import httpx
import statistics

URL = "http://127.0.0.1:8000/internal/llm/test"

PROMPTS = [
    "Why do you need my ZIP code?",
    "What is Medicare Part A?",
    "Can you repeat the question?",
    "Hold on, I didn't understand.",
    "Why are you asking my age?",
    "I need a minute.",
    "Are you a real person?",
    "I don't know what Part B means."
]

NUM_RUNS_PER_PROMPT = 3

async def run_benchmark():
    latencies = []
    tokens_per_sec_list = []
    output_lengths = []
    
    print(f"Starting Qwen 2.5 latency baseline benchmark against {URL}")
    print(f"Number of prompts: {len(PROMPTS)}")
    print(f"Runs per prompt: {NUM_RUNS_PER_PROMPT}")
    print("-" * 50)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Warmup run
        try:
            print("Running warmup request...")
            await client.post(URL, json={"text": "Hello"})
        except Exception as e:
            print(f"Warmup failed: {e}")
            return
            
        print("Warmup complete. Starting benchmark...\n")
        
        for prompt in PROMPTS:
            print(f"Prompt: '{prompt}'")
            for i in range(NUM_RUNS_PER_PROMPT):
                start_time = time.perf_counter()
                try:
                    response = await client.post(URL, json={"text": prompt})
                    response.raise_for_status()
                    data = response.json()
                    
                    latency = data.get("latency_ms", 0.0)
                    completion_tokens = data.get("completion_tokens")
                    
                    if latency > 0 and completion_tokens:
                        tokens_per_sec = completion_tokens / (latency / 1000.0)
                    else:
                        tokens_per_sec = 0.0
                        
                    latencies.append(latency)
                    if tokens_per_sec > 0:
                        tokens_per_sec_list.append(tokens_per_sec)
                    output_lengths.append(len(data.get("text", "")))
                    
                    print(f"  Run {i+1}: {latency:.1f}ms | {completion_tokens} tokens | {tokens_per_sec:.1f} tok/s")
                except Exception as e:
                    print(f"  Run {i+1} Failed: {e}")
                    
    print("-" * 50)
    print("BENCHMARK RESULTS")
    if not latencies:
        print("No valid data collected.")
        return
        
    latencies.sort()
    
    p50_idx = int(len(latencies) * 0.5)
    p95_idx = int(len(latencies) * 0.95)
    
    p50_latency = latencies[p50_idx]
    p95_latency = latencies[p95_idx]
    avg_latency = statistics.mean(latencies)
    avg_tps = statistics.mean(tokens_per_sec_list) if tokens_per_sec_list else 0.0
    avg_length = statistics.mean(output_lengths) if output_lengths else 0.0
    
    print(f"Total Requests  : {len(latencies)}")
    print(f"Average Latency : {avg_latency:.1f} ms")
    print(f"P50 Latency     : {p50_latency:.1f} ms")
    print(f"P95 Latency     : {p95_latency:.1f} ms")
    print(f"Tokens/Second   : {avg_tps:.1f} tok/s")
    print(f"Average Output Length : {avg_length:.1f} chars")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
