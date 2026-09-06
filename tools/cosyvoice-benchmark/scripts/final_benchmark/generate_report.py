import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def p50(data):
    if not data: return "N/A"
    return f"{np.percentile(data, 50):.2f}"

def p95(data):
    if not data: return "N/A"
    return f"{np.percentile(data, 95):.2f}"

def build_report(benchmark_dir):
    benchmark_dir = Path(benchmark_dir)
    
    with open(benchmark_dir / "comparison" / "raw_results.json", "r") as f:
        trials = json.load(f)
        
    models_data = {
        "Chatterbox Turbo": {"metrics": {}},
        "CosyVoice 3": {"metrics": {}},
        "CosyVoice 2": {"metrics": {}}
    }
    
    for model_key, model_folder in [("Chatterbox Turbo", "chatterbox_turbo"), ("CosyVoice 3", "cosyvoice3"), ("CosyVoice 2", "cosyvoice2")]:
        m_file = benchmark_dir / model_folder / "metrics.json"
        if m_file.exists():
            with open(m_file, "r") as f:
                d = json.load(f)
                models_data[model_key]["metrics"] = d
                
    report_lines = [
        "# FINAL TTS BENCHMARK REPORT\n\n",
        "## Hardware / Software Environment\n"
    ]
    
    env_file = benchmark_dir / "environment" / "info.json"
    if env_file.exists():
        with open(env_file, "r") as f:
            env = json.load(f)
            for k,v in env.items():
                report_lines.append(f"- **{k}**: {v}\n")
    report_lines.append("\n")
    
    table_header = "| Metric | Chatterbox Turbo | CosyVoice 3 | CosyVoice 2 |\n|---|---|---|---|\n"
    report_lines.append("## Core Metrics\n\n" + table_header)
    
    def get_model_metric(model_name, key, fmt="{:.2f}"):
        v = models_data[model_name]["metrics"].get(key, "N/A")
        if isinstance(v, (int, float)): return fmt.format(v)
        return str(v)
        
    report_lines.append(f"| Model load (s) | {get_model_metric('Chatterbox Turbo', 'load_time')} | {get_model_metric('CosyVoice 3', 'load_time')} | {get_model_metric('CosyVoice 2', 'load_time')} |\n")
    report_lines.append(f"| Warmup (s) | {get_model_metric('Chatterbox Turbo', 'warmup_time')} | {get_model_metric('CosyVoice 3', 'warmup_time')} | {get_model_metric('CosyVoice 2', 'warmup_time')} |\n")
    report_lines.append(f"| Idle VRAM (MB) | {get_model_metric('Chatterbox Turbo', 'idle_vram')} | {get_model_metric('CosyVoice 3', 'idle_vram')} | {get_model_metric('CosyVoice 2', 'idle_vram')} |\n")
    
    # Calculate medians
    model_stats = defaultdict(lambda: defaultdict(list))
    for t in trials:
        m = t["model"]
        if t["status"] == "VALID":
            if t["TTFA"] is not None:
                model_stats[m]["ttfa"].append(t["TTFA"])
            model_stats[m]["gen"].append(t["generation_time"])
            model_stats[m]["rtf"].append(t["RTF"])
            if t["VRAM_peak"]:
                model_stats[m]["vram_peak"].append(t["VRAM_peak"])
                
            model_stats[m][f"cat_{t['category']}_ttfa"].append(t["TTFA"] if t["TTFA"] else t["generation_time"])
            
        model_stats[m]["trials_total"] = model_stats[m].get("trials_total", 0) + 1
        if t["status"] == "VALID": model_stats[m]["valid"] = model_stats[m].get("valid", 0) + 1
        if t["status"] == "SILENT_OUTPUT": model_stats[m]["silent"] = model_stats[m].get("silent", 0) + 1
        if t["status"] == "EMPTY_OUTPUT": model_stats[m]["empty"] = model_stats[m].get("empty", 0) + 1
        if "ERROR" in t["status"]: model_stats[m]["error"] = model_stats[m].get("error", 0) + 1
        if t["status"] == "TIMEOUT": model_stats[m]["timeout"] = model_stats[m].get("timeout", 0) + 1
        
    def stat_row(metric_name, stat_key, calc_fn):
        row = f"| {metric_name} | "
        for m in ["Chatterbox Turbo", "CosyVoice 3", "CosyVoice 2"]:
            row += f"{calc_fn(model_stats[m].get(stat_key, []))} | "
        return row + "\n"
        
    report_lines.append(stat_row("Peak VRAM (MB)", "vram_peak", lambda d: f"{np.max(d):.2f}" if d else "N/A"))
    report_lines.append(stat_row("p50 TTFA (ms)", "ttfa", p50))
    report_lines.append(stat_row("p95 TTFA (ms)", "ttfa", p95))
    report_lines.append(stat_row("p50 Total Generation (s)", "gen", p50))
    report_lines.append(stat_row("p95 Total Generation (s)", "gen", p95))
    report_lines.append(stat_row("p50 RTF", "rtf", p50))
    report_lines.append(stat_row("Short p50 Latency", "cat_SHORT_ttfa", p50))
    report_lines.append(stat_row("Medium p50 Latency", "cat_MEDIUM_ttfa", p50))
    report_lines.append(stat_row("Long p50 Latency", "cat_LONG_ttfa", p50))
    report_lines.append(stat_row("Number/Domain p50 Latency", "cat_NUMBER_DOMAIN_ttfa", p50))
    
    # Reliability table
    report_lines.append("\n## Reliability\n\n| Model | Trials | Valid | Silent | Empty | Errors | OOM | Timeout | Success Rate |\n|---|---|---|---|---|---|---|---|---|\n")
    for m in ["Chatterbox Turbo", "CosyVoice 3", "CosyVoice 2"]:
        tot = model_stats[m].get("trials_total", 0)
        val = model_stats[m].get("valid", 0)
        sil = model_stats[m].get("silent", 0)
        emp = model_stats[m].get("empty", 0)
        err = model_stats[m].get("error", 0)
        oom = 0 # Not explicitly tracked unless caught in error
        to = model_stats[m].get("timeout", 0)
        rate = f"{(val/tot*100):.1f}%" if tot > 0 else "N/A"
        
        report_lines.append(f"| {m} | {tot} | {val} | {sil} | {emp} | {err} | {oom} | {to} | {rate} |\n")
        
    report_lines.append("\n## Subjective Scoring\n\n| Metric | Chatterbox Turbo | CosyVoice 3 | CosyVoice 2 |\n|---|---|---|---|\n")
    report_lines.append("| LATENCY | | | |\n")
    report_lines.append("| RELIABILITY | | | |\n")
    report_lines.append("| VRAM EFFICIENCY | | | |\n")
    report_lines.append("| TELEPHONY SUITABILITY | | | |\n")
    report_lines.append("| VOICE CONSISTENCY | PENDING HUMAN LISTENING | PENDING HUMAN LISTENING | PENDING HUMAN LISTENING |\n")
    report_lines.append("| NATURALNESS | PENDING HUMAN LISTENING | PENDING HUMAN LISTENING | PENDING HUMAN LISTENING |\n")
    
    with open(benchmark_dir / "comparison" / "FINAL_REPORT.md", "w") as f:
        f.writelines(report_lines)

if __name__ == "__main__":
    build_report(sys.argv[1])
