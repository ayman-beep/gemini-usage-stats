import os
import json
import glob
import hashlib
import re
from datetime import datetime
from collections import defaultdict

# Multi-CLI API Pricing (USD per 1M tokens) - Updated with Opencode Zen pricing
PRICING = {
    # Gemini models
    "gemini-3-pro": {"input": 2.00, "output": 12.00, "cached": 0.20},
    "gemini-3-pro-preview": {"input": 2.00, "output": 12.00, "cached": 0.20},
    "gemini-3-flash": {"input": 0.50, "output": 3.00, "cached": 0.05},
    "gemini-3-flash-preview": {"input": 0.50, "output": 3.00, "cached": 0.05},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "cached": 0.125},
    "gemini-2.5-flash": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40, "cached": 0.01},
    
    # OpenAI / Codex CLI models (Official Codex CLI Pricing)
    # GPT-5.2 Variants
    "gpt-5.2": {"input": 1.75, "output": 14.00, "cached": 0.175},
    "gpt-5.2-instant": {"input": 1.75, "output": 14.00, "cached": 0.175},
    "gpt-5.2-thinking": {"input": 1.75, "output": 14.00, "cached": 0.175},
    "gpt-5.2-pro": {"input": 21.00, "output": 168.00, "cached": 2.10},
    "gpt-5.2-codex": {"input": 1.75, "output": 14.00, "cached": 0.175},
    # GPT-5.1 Variants
    "gpt-5.1": {"input": 1.25, "output": 10.00, "cached": 0.125},
    "gpt-5.1-codex-max": {"input": 1.25, "output": 10.00, "cached": 0.125},
    "gpt-5.1-codex-mini": {"input": 0.25, "output": 2.00, "cached": 0.025},
    "gpt-5-nano": {"input": 0.05, "output": 0.40, "cached": 0.005},
    # Legacy Codex models
    "gpt-5-codex": {"input": 0.50, "output": 1.50, "cached": 0.025},
    "gpt-5.3-codex": {"input": 0.30, "output": 1.20, "cached": 0.025},
    "gpt-4-codex": {"input": 2.00, "output": 6.00, "cached": 0.50},
    # Other OpenAI models
    "o3-mini": {"input": 1.10, "output": 4.40, "cached": 0.55},
    "o1": {"input": 15.00, "output": 60.00, "cached": 7.50},
    "gpt-4o": {"input": 2.50, "output": 10.00, "cached": 1.25},
    
    # Anthropic / Claude models (Opencode Zen pricing)
    "claude-opus-4-6": {"input": 5.00, "output": 25.00, "cached": 0.50},
    "claude-opus-4-5": {"input": 5.00, "output": 25.00, "cached": 0.50},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00, "cached": 0.30},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00, "cached": 0.30},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00, "cached": 0.10},
    "claude-opus-4-1": {"input": 15.00, "output": 75.00, "cached": 1.50},
    "claude-3-7-sonnet": {"input": 3.00, "output": 15.00, "cached": 0.30},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00, "cached": 0.30},
    "claude-3-opus": {"input": 15.00, "output": 75.00, "cached": 1.50},
    
    # Opencode Zen models
    "kimi-k2-5": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "kimi-k2": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "glm-4-7": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-4-6": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "minimax-m2-5": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2-1": {"input": 0.30, "output": 1.20, "cached": 0.03},
    
    # Qwen models (Alibaba Cloud, via OpenRouter pricing)
    "qwen-2.5-coder-32b-instruct": {"input": 0.20, "output": 0.20, "cached": 0.02},
    "qwen-2.5-72b-instruct": {"input": 0.36, "output": 0.36, "cached": 0.036},
    "qwen-2.5-vl-72b-instruct": {"input": 0.40, "output": 0.40, "cached": 0.04},
    "qwen-2.5-vl-7b-instruct": {"input": 0.10, "output": 0.10, "cached": 0.01},
    "qwen-2.5-7b-instruct": {"input": 0.05, "output": 0.05, "cached": 0.005},
    "qwen-qwq-32b": {"input": 0.20, "output": 0.20, "cached": 0.02},
    "qwen-2.5-max": {"input": 1.60, "output": 6.40, "cached": 0.16},
    "qwen-2.5-plus": {"input": 0.40, "output": 1.20, "cached": 0.04},
    "qwen-3-235b-a22b": {"input": 0.20, "output": 0.60, "cached": 0.02},
    "qwen-3-30b-a3b": {"input": 0.05, "output": 0.15, "cached": 0.005},
    "qwen-3-32b": {"input": 0.20, "output": 0.20, "cached": 0.02},
    "qwen-3-8b": {"input": 0.05, "output": 0.05, "cached": 0.005},
    "qwen-3-4b": {"input": 0.02, "output": 0.02, "cached": 0.002},
    "qwen-3-0.6b": {"input": 0.01, "output": 0.01, "cached": 0.001},
    
    # Stealth models — no public API pricing
    "pony-alpha": {"input": 0, "output": 0, "cached": 0},
    "giga-potato": {"input": 0, "output": 0, "cached": 0},
}

DEFAULT_PRICING = {"input": 0, "output": 0, "cached": 0}

def normalize_model_name(model):
    """Strip date suffixes (e.g. -20251001) and :free suffix from model names for pricing lookup."""
    # Remove trailing date like -20251001, -20251101, etc.
    normalized = re.sub(r'-\d{8}$', '', model)
    # Remove :free suffix (e.g. "kimi-k2.5:free" -> "kimi-k2.5")
    normalized = re.sub(r':free$', '', normalized)
    # Remove thinking suffix (e.g. "claude-sonnet-4.5 (thinking)" -> "claude-sonnet-4.5")
    normalized = re.sub(r'\s*\(thinking\)$', '', normalized, flags=re.IGNORECASE)
    # Remove high/low/medium suffixes (e.g. "gemini-3-pro (high)" -> "gemini-3-pro")
    normalized = re.sub(r'\s*\((high|low|medium)\)$', '', normalized, flags=re.IGNORECASE)
    # Replace spaces with hyphens for consistency (e.g. "Qwen 2.5 Coder 32B Instruct" -> "qwen-2.5-coder-32b-instruct")
    normalized = normalized.replace(' ', '-').lower()
    return normalized

def get_cost(model, input_tokens, output_tokens, cached_tokens):
    pricing = PRICING.get(model) or PRICING.get(normalize_model_name(model), DEFAULT_PRICING)
    # Subtract cached tokens from total input to get billed non-cached input
    billed_input = max(0, input_tokens - cached_tokens)
    cost = (billed_input / 1_000_000) * pricing["input"] + \
           (output_tokens / 1_000_000) * pricing["output"] + \
           (cached_tokens / 1_000_000) * pricing["cached"]
    return cost

def format_num(n):
    return f"{n:,}"

def get_project_map():
    home_dir = os.path.expanduser("~")
    trusted_file = os.path.join(home_dir, ".gemini", "trustedFolders.json")
    proj_map = {}
    trusted_paths = []

    if os.path.exists(trusted_file):
        try:
            with open(trusted_file, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    trusted_paths = list(data.keys())
                else:
                    trusted_paths = data
        except Exception:
            pass

    for path in trusted_paths:
        # Gemini uses sha256 of the path to create the hash directory name
        h_exact = hashlib.sha256(path.encode('utf-8')).hexdigest()
        proj_map[h_exact] = path
        
        # Fallback for lowercase
        h_lower = hashlib.sha256(path.lower().encode('utf-8')).hexdigest()
        if h_lower not in proj_map:
            proj_map[h_lower] = path
            
    return proj_map

def track_usage():
    home_dir = os.path.expanduser("~")
    gemini_tmp = os.path.join(home_dir, ".gemini", "tmp")
    proj_map = get_project_map()
    
    # Pattern to find all session files
    pattern = os.path.join(gemini_tmp, "*", "chats", "session-*.json")
    session_files = glob.glob(pattern)
    
    if not session_files:
        print(f"No session files found in {gemini_tmp}")
        return

    stats_by_day = defaultdict(lambda: {
        "input": 0, "output": 0, "cached": 0, "cost": 0.0, "sessions": set()
    })
    
    stats_by_project = defaultdict(lambda: {
        "input": 0, "output": 0, "cached": 0, "cost": 0.0, "sessions": 0
    })

    model_usage = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0.0})

    for file_path in session_files:
        try:
            project_hash = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            session_id = data.get("sessionId")
            messages = data.get("messages", [])
            
            session_input = 0
            session_output = 0
            session_cached = 0
            session_cost = 0.0
            
            has_gemini_msg = False
            for msg in messages:
                if msg.get("type") == "gemini" and "tokens" in msg:
                    has_gemini_msg = True
                    tokens = msg["tokens"]
                    model = msg.get("model", "unknown")
                    ts = msg.get("timestamp")
                    
                    i = tokens.get("input", 0)
                    o = tokens.get("output", 0)
                    c = tokens.get("cached", 0)
                    
                    cost = get_cost(model, i, o, c)
                    
                    session_input += i
                    session_output += o
                    session_cached += c
                    session_cost += cost
                    
                    model_usage[model]["input"] += i
                    model_usage[model]["output"] += o
                    model_usage[model]["cost"] += cost
                    
                    if ts:
                        date_str = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                        day = stats_by_day[date_str]
                        day["input"] += i
                        day["output"] += o
                        day["cached"] += c
                        day["cost"] += cost
                        day["sessions"].add(session_id)
            
            if has_gemini_msg:
                proj_name = proj_map.get(project_hash, project_hash)
                proj = stats_by_project[proj_name]
                proj["input"] += session_input
                proj["output"] += session_output
                proj["cached"] += session_cached
                proj["cost"] += session_cost
                proj["sessions"] += 1

        except Exception:
            continue

    # 1. Daily Summary
    print("\n" + "DAILY USAGE SUMMARY".center(100, "="))
    print(f"{ 'Date':<12} | {'Input':>15} | {'Output':>12} | {'Cached':>15} | {'Cost ($)':>12}")
    print("-" * 100)
    
    total_i = total_o = total_c = total_cost = 0
    sorted_days = sorted(stats_by_day.keys())
    for d in sorted_days:
        s = stats_by_day[d]
        print(f"{d:<12} | {format_num(s['input']):>15} | {format_num(s['output']):>12} | {format_num(s['cached']):>15} | {s['cost']:>12.4f}")
        total_i += s["input"]
        total_o += s["output"]
        total_c += s["cached"]
        total_cost += s["cost"]
    
    print("-" * 100)
    print(f"{ 'TOTAL':<12} | {format_num(total_i):>15} | {format_num(total_o):>12} | {format_num(total_c):>15} | {total_cost:>12.4f}")
    
    # 2. Project Summary
    print("\n" + "USAGE BY REPOSITORY / FOLDER".center(100, "="))
    print(f"{ 'Repository/Folder':<50} | {'Input':>15} | {'Cost ($)':>12}")
    print("-" * 100)
    for p, data in sorted(stats_by_project.items(), key=lambda x: x[1]['cost'], reverse=True):
        display_name = p
        if len(display_name) > 47:
            display_name = "..." + display_name[-47:]
        print(f"{display_name:<50} | {format_num(data['input']):>15} | {data['cost']:>12.4f}")

    # 3. Model Summary
    print("\n" + "USAGE BY MODEL".center(115, "="))
    print(f"{ 'Model':<40} | {'Input':>15} | {'Output':>12} | {'Total Tokens':>15} | {'Cost ($)':>12}")
    print("-" * 115)
    for m, data in sorted(model_usage.items(), key=lambda x: x[1]['cost'], reverse=True):
        total_tokens = data['input'] + data['output']
        print(f"{m:<40} | {format_num(data['input']):>15} | {format_num(data['output']):>12} | {format_num(total_tokens):>15} | {data['cost']:>12.4f}")

    # 4. Overall Stats
    print("\n" + "OVERALL STATISTICS".center(100, "="))
    num_days = len(sorted_days)
    if num_days > 0:
        print(f"Average Cost per Day:  ${total_cost / num_days:.4f}")
        print(f"Total Input Tokens:    {format_num(total_i)}")
        print(f"Total Output Tokens:   {format_num(total_o)}")
        print(f"Total Cached Tokens:   {format_num(total_c)}")
        print(f"Total Estimated Cost:  ${total_cost:.4f}")
        print(f"Total Active Projects: {len(stats_by_project)}")
        print(f"Total Sessions:        {sum(p['sessions'] for p in stats_by_project.values())}")
    print("=" * 100 + "\n")

if __name__ == "__main__":
    track_usage()
