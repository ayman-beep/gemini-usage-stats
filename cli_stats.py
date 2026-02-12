import os
import json
import glob
import hashlib
import webbrowser
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
    # GPT-5 Pro
    "gpt-5-pro": {"input": 15.00, "output": 120.00, "cached": 1.50},
    # o1-pro and o3-pro models
    "o1-pro": {"input": 150.00, "output": 600.00, "cached": 15.00},
    "o3-pro": {"input": 20.00, "output": 80.00, "cached": 2.00},
    "o3-deep-research": {"input": 10.00, "output": 40.00, "cached": 1.00},
    # GPT-4 models
    "gpt-4-0314": {"input": 30.00, "output": 60.00, "cached": 3.00},
    "gpt-4": {"input": 30.00, "output": 60.00, "cached": 3.00},
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
    "kimi-k2.5": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "kimi-k2": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "kimi-k1.5": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "glm-4-7": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-4-6": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-5": {"input": 0.80, "output": 2.56, "cached": 0.08},
    "minimax-m2.1": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2.1-free": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2.5": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2.5:free": {"input": 0.30, "output": 1.20, "cached": 0.03},
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
    
    # xAI models
    "grok-code-fast-1": {"input": 0.20, "output": 1.50, "cached": 0.02},
    "grok-3": {"input": 0.20, "output": 1.50, "cached": 0.02},
    "grok-3-mini": {"input": 0.10, "output": 0.50, "cached": 0.01},
    
    # Mistral models
    "devstral-2512": {"input": 0.05, "output": 0.22, "cached": 0.005},
    "mistral-large-2411": {"input": 2.00, "output": 6.00, "cached": 0.50},
    "mistral-small-2501": {"input": 0.10, "output": 0.30, "cached": 0.025},
    
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
    cost_input = (billed_input / 1_000_000) * pricing["input"]
    cost_output = (output_tokens / 1_000_000) * pricing["output"]
    cost_cached = (cached_tokens / 1_000_000) * pricing["cached"]
    return cost_input + cost_output + cost_cached

def get_project_name(path_str):
    if not path_str: return None
    path_str = path_str.replace("/", "\\").strip()
    path_str = path_str.strip("'").strip('"')
    parts = [p for p in path_str.split("\\") if p]
    if not parts: return path_str
    if len(parts) >= 2 and ":" in parts[0]:
        if "New folder" in parts[1] and len(parts) >= 3:
            return f"{parts[0]}\\{parts[1]}\\{parts[2]}"
        return f"{parts[0]}\\{parts[1]}"
    return parts[0]

def track_usage():
    home_dir = os.path.expanduser("~")
    gemini_tmp = os.path.join(home_dir, ".gemini", "tmp")
    trusted_file = os.path.join(home_dir, ".gemini", "trustedFolders.json")
    pattern = os.path.join(gemini_tmp, "*", "chats", "session-*.json")
    session_files = glob.glob(pattern)
    if not session_files: return
    
    stats_by_day = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "cost": 0.0})
    stats_by_project = defaultdict(lambda: {"cost": 0.0})
    hash_to_name = {}

    if os.path.exists(trusted_file):
        try:
            with open(trusted_file, "r") as f:
                trusted = json.load(f)
                for path in trusted:
                    h = hashlib.sha256(path.lower().encode('utf-8')).hexdigest()
                    hash_to_name[h] = path
                    # Fix the backslash replacement issue by using a raw string or double escape
                    p_fs = path.replace("\\", "/")
                    h2 = hashlib.sha256(p_fs.lower().encode('utf-8')).hexdigest()
                    hash_to_name[h2] = path
        except: pass

    path_regex = r'[a-zA-Z]:\\[^"\`\n, ]+'

    for file_path in session_files:
        project_hash = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        if project_hash not in hash_to_name or "Project" in str(hash_to_name[project_hash]):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    matches = re.findall(path_regex, content)
                    for m in matches:
                        if "AppData" not in m and ".gemini" not in m:
                            hash_to_name[project_hash] = m
                            break
            except: continue

    for file_path in session_files:
        try:
            project_hash = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_name = hash_to_name.get(project_hash, f"Project {project_hash[:8]}")
            name = get_project_name(raw_name) if "\\" in str(raw_name) else raw_name
            for msg in data.get("messages", []):
                if msg.get("type") == "gemini" and "tokens" in msg:
                    tokens = msg["tokens"]
                    model = msg.get("model", "unknown")
                    ts = msg.get("timestamp")
                    i, o, c = tokens.get("input", 0), tokens.get("output", 0), tokens.get("cached", 0)
                    cost = get_cost(model, i, o, c)
                    stats_by_project[name]["cost"] += cost
                    if ts:
                        d = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                        stats_by_day[d]["input"] += i
                        stats_by_day[d]["output"] += o
                        stats_by_day[d]["cached"] += c
                        stats_by_day[d]["cost"] += cost
        except: continue

    sorted_days = sorted(stats_by_day.keys())
    total_cost = sum(d["cost"] for d in stats_by_day.values())
    total_input = sum(d["input"] for d in stats_by_day.values())
    total_output = sum(d["output"] for d in stats_by_day.values())
    total_cached = sum(d["cached"] for d in stats_by_day.values())
    avg_cost = total_cost / max(len(sorted_days), 1)

    print(f"\nSummary: Cost ${total_cost:,.2f} | Input {total_input:,} | Output {total_output:,}")
    print(f"Opening browser dashboard...")

    dashboard_data = {
        "days": sorted_days,
        "costs": [round(stats_by_day[d]["cost"], 4) for d in sorted_days],
        "proj_labels": list(stats_by_project.keys()),
        "proj_data": [round(v["cost"], 4) for v in stats_by_project.values()],
        "total_cost": f"{total_cost:,.2f}",
        "avg_cost": f"{avg_cost:,.2f}",
        "total_input": f"{total_input:,}",
        "total_output": f"{total_output:,}",
        "total_cached": f"{total_cached:,}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    html_template = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Gemini Usage Analytics</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: ui-sans-serif, system-ui, sans-serif; }
        .glass { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="mb-10 flex justify-between items-end">
            <div>
                <h1 class="text-4xl font-black tracking-tighter text-white">GEMINI <span class="text-blue-500">STATS</span></h1>
                <p class="text-slate-400 text-sm">Automated Usage & Cost Analysis</p>
            </div>
            <div class="text-right text-xs text-slate-500 font-mono" id="last-updated"></div>
        </header>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-10">
            <div class="glass p-5 rounded-2xl border-l-4 border-blue-500">
                <p class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">Input Tokens</p>
                <h2 class="text-2xl font-bold text-white" id="stat-input">0</h2>
            </div>
            <div class="glass p-5 rounded-2xl border-l-4 border-purple-500">
                <p class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">Output Tokens</p>
                <h2 class="text-2xl font-bold text-white" id="stat-output">0</h2>
            </div>
            <div class="glass p-5 rounded-2xl border-l-4 border-emerald-500">
                <p class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">Cached Tokens</p>
                <h2 class="text-2xl font-bold text-white" id="stat-cached">0</h2>
            </div>
            <div class="glass p-5 rounded-2xl border-l-4 border-slate-500">
                <p class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">Total Tokens</p>
                <h2 class="text-2xl font-bold text-white" id="stat-total-tokens">0</h2>
            </div>
            <div class="glass p-5 rounded-2xl border-l-4 border-amber-500">
                <p class="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1">Total Cost</p>
                <h2 class="text-2xl font-bold text-white" id="stat-total">$0.00</h2>
            </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div class="glass p-8 rounded-3xl"><h3 class="text-lg font-bold mb-6 text-slate-200">Spending Over Time</h3><canvas id="costChart"></canvas></div>
            <div class="glass p-8 rounded-3xl"><h3 class="text-lg font-bold mb-6 text-slate-200">Cost by Repository</h3><canvas id="projectChart"></canvas></div>
        </div>
    </div>
    <script>
        const data = __DATA_JSON__;
        document.getElementById('stat-total').innerText = '$' + data.total_cost;
        document.getElementById('stat-input').innerText = data.total_input;
        document.getElementById('stat-output').innerText = data.total_output;
        document.getElementById('stat-cached').innerText = data.total_cached;
        document.getElementById('stat-total-tokens').innerText = (parseInt(data.total_input.replace(/,/g, '')) + parseInt(data.total_output.replace(/,/g, ''))).toLocaleString();
        document.getElementById('last-updated').innerText = 'Last Sync: ' + data.timestamp;
        const tooltipConfig = { callbacks: { label: (ctx) => '$' + (ctx.parsed.y || ctx.parsed).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 4}) } };
        new Chart(document.getElementById('costChart'), {
            type: 'line',
            data: { labels: data.days, datasets: [{ data: data.costs, borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.05)', fill: true, tension: 0.4, borderWidth: 4, pointRadius: 4 }] },
            options: { plugins: { legend: { display: false }, tooltip: tooltipConfig }, scales: { y: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.03)' } }, x: { ticks: { color: '#64748b' }, grid: { display: false } } } }
        });
        new Chart(document.getElementById('projectChart'), {
            type: 'bar',
            data: { labels: data.proj_labels, datasets: [{ data: data.proj_data, backgroundColor: '#3b82f6', borderRadius: 10 }] },
            options: { indexAxis: 'y', plugins: { legend: { display: false }, tooltip: tooltipConfig }, scales: { x: { ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.03)' } }, y: { ticks: { color: '#64748b' }, grid: { display: false } } } }
        });
    </script>
</body>
</html>'''
    
    final_html = html_template.replace("__DATA_JSON__", json.dumps(dashboard_data))
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(final_html)
    webbrowser.open('file://' + os.path.abspath("dashboard.html"))

if __name__ == "__main__":
    track_usage()
