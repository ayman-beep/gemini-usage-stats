import os
import json
import glob
import hashlib
import webbrowser
from datetime import datetime
from collections import defaultdict

# Gemini API Pricing
PRICING = {
    "gemini-3-pro-preview": {"input": 2.00, "output": 12.00, "cached": 0.20},
    "gemini-3-flash": {"input": 0.50, "output": 3.00, "cached": 0.05},
    "gemini-3-flash-preview": {"input": 0.50, "output": 3.00, "cached": 0.05},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "cached": 0.125},
    "gemini-2.5-flash": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40, "cached": 0.01},
}
DEFAULT_PRICING = {"input": 0.50, "output": 3.00, "cached": 0.05}

def get_cost(model, input_tokens, output_tokens, cached_tokens):
    pricing = PRICING.get(model, DEFAULT_PRICING)
    # Subtract cached tokens from total input to get billed non-cached input
    billed_input = max(0, input_tokens - cached_tokens)
    return (billed_input / 1_000_000) * pricing["input"] + \
           (output_tokens / 1_000_000) * pricing["output"] + \
           (cached_tokens / 1_000_000) * pricing["cached"]

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
        # Gemini often uses the exact case of the path for hashing
        h_exact = hashlib.sha256(path.encode('utf-8')).hexdigest()
        proj_map[h_exact] = os.path.basename(path) or path
        
        # Fallback for some versions/platforms that might use lowercase
        h_lower = hashlib.sha256(path.lower().encode('utf-8')).hexdigest()
        if h_lower not in proj_map:
            proj_map[h_lower] = os.path.basename(path) or path

    # Additionally, try to map the current working directory
    current_dir = os.getcwd()
    current_dir_hash = hashlib.sha256(current_dir.encode('utf-8')).hexdigest()
    if current_dir_hash not in proj_map:
        proj_map[current_dir_hash] = os.path.basename(current_dir) or current_dir

    return proj_map

def generate_data():
    home_dir = os.path.expanduser("~")
    gemini_tmp = os.path.join(home_dir, ".gemini", "tmp")
    proj_map = get_project_map()
    pattern = os.path.join(gemini_tmp, "*", "chats", "session-*.json")
    session_files = glob.glob(pattern)
    
    stats_by_day = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "cost": 0.0})
    stats_by_project = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0.0})
    model_usage = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0.0})

    for file_path in session_files:
        try:
            project_hash = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for msg in data.get("messages", []):
                if msg.get("type") == "gemini" and "tokens" in msg:
                    tokens = msg["tokens"]
                    model = msg.get("model", "unknown")
                    ts = msg.get("timestamp")
                    i, o, c = tokens.get("input", 0), tokens.get("output", 0), tokens.get("cached", 0)
                    cost = get_cost(model, i, o, c)
                    
                    model_usage[model]["input"] += i
                    model_usage[model]["output"] += o
                    model_usage[model]["cost"] += cost
                    
                    proj_name = proj_map.get(project_hash, project_hash[:8])
                    stats_by_project[proj_name]["input"] += i
                    stats_by_project[proj_name]["output"] += o
                    stats_by_project[proj_name]["cost"] += cost

                    if ts:
                        d = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                        stats_by_day[d]["input"] += i
                        stats_by_day[d]["output"] += o
                        stats_by_day[d]["cached"] += c
                        stats_by_day[d]["cost"] += cost
        except: continue

    sorted_days = sorted(stats_by_day.keys())
    # Sort projects by cost descending for the data structure
    sorted_projects = sorted(stats_by_project.items(), key=lambda x: x[1]["cost"], reverse=True)
    
    return {
        "days": sorted_days,
        "daily_costs": [stats_by_day[d]["cost"] for d in sorted_days],
        "daily_tokens": [stats_by_day[d]["input"] for d in sorted_days],
        "projects": [p for p, v in sorted_projects],
        "project_costs": [v["cost"] for v, p in [ (v, p) for p, v in sorted_projects ]],
        "project_tokens": [v["input"] for v, p in [ (v, p) for p, v in sorted_projects ]],
        "models": list(model_usage.keys()),
        "model_costs": [v["cost"] for v in model_usage.values()],
        "totals": {
            "cost": sum(v["cost"] for v in stats_by_day.values()),
            "input": sum(v["input"] for v in stats_by_day.values()),
            "output": sum(v["output"] for v in stats_by_day.values()),
            "cached": sum(v["cached"] for v in stats_by_day.values()),
            "avg_day": sum(v["cost"] for v in stats_by_day.values()) / max(len(stats_by_day), 1)
        }
    }

def main():
    data = generate_data()
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini CLI Usage Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }}
        .card-grad {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 10px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="mb-10 flex justify-between items-end">
            <div>
                <h1 class="text-4xl font-bold tracking-tight text-white mb-2">Gemini <span class="text-blue-500">Analytics</span></h1>
                <p class="text-slate-400">Real-time usage and cost tracking for Gemini CLI</p>
            </div>
            <div class="text-right">
                <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Last Updated</span>
                <p class="text-sm font-medium text-slate-300">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-10">
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-blue-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Input Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['input']:,}</h3>
                <div class="mt-2 text-xs text-blue-400 font-medium">Context Sent</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-purple-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Output Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['output']:,}</h3>
                <div class="mt-2 text-xs text-purple-400 font-medium">Responses Gen</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-emerald-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Cached Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['cached']:,}</h3>
                <div class="mt-2 text-xs text-emerald-400 font-medium">Efficiency Savings</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-slate-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Total Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['input'] + data['totals']['output']:,}</h3>
                <div class="mt-2 text-xs text-slate-400 font-medium">Combined Usage</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-amber-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Total Cost</p>
                <h3 class="text-2xl font-bold text-white">${data['totals']['cost']:,.2f}</h3>
                <div class="mt-2 text-xs text-amber-400 font-medium">Est. API Spend</div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
            <div class="lg:col-span-2 glass p-6 rounded-2xl">
                <h3 class="text-lg font-semibold mb-6">Daily Cost Trend</h3>
                <div style="height: 350px; position: relative;">
                    <canvas id="costChart"></canvas>
                </div>
            </div>
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-lg font-semibold mb-6">Cost by Model</h3>
                <div style="height: 350px; position: relative;">
                    <canvas id="modelChart"></canvas>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-lg font-semibold mb-6">Usage Breakdown</h3>
                <div class="overflow-y-auto max-h-[400px]">
                    <canvas id="projectChart" style="height: {max(400, len(data['projects']) * 30)}px"></canvas>
                </div>
            </div>
            <div class="glass p-6 rounded-2xl overflow-hidden">
                <h3 class="text-lg font-semibold mb-4 px-2">All Projects</h3>
                <div class="overflow-x-auto max-h-[400px] overflow-y-auto">
                    <table class="w-full text-left text-sm">
                        <thead class="text-slate-500 uppercase text-xs border-b border-slate-700 sticky top-0 bg-[#1e293b] z-10">
                            <tr>
                                <th class="py-3 px-2">Project</th>
                                <th class="py-3 px-2 text-right">Tokens</th>
                                <th class="py-3 px-2 text-right">Cost</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            {''.join([f"<tr><td class='py-4 px-2 font-medium'>{p}</td><td class='py-4 px-2 text-right text-slate-400'>{c:,}</td><td class='py-4 px-2 text-right text-blue-400 font-semibold'>${v:,.2f}</td></tr>" for p, c, v in zip(data['projects'], data['project_tokens'], data['project_costs'])])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        const ctxCost = document.getElementById('costChart').getContext('2d');
        new Chart(ctxCost, {{
            type: 'line',
            data: {{
                labels: {json.dumps(data['days'])},
                datasets: [{{
                    label: 'Daily Cost ($)',
                    data: {json.dumps(data['daily_costs'])},
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: '#3b82f6'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }}
                }}
            }}
        }});

        const ctxModel = document.getElementById('modelChart').getContext('2d');
        new Chart(ctxModel, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(data['models'])},
                datasets: [{{
                    data: {json.dumps(data['model_costs'])},
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#6366f1'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', padding: 20, usePointStyle: true }} }}
                }},
                cutout: '70%'
            }}
        }});

        const ctxProj = document.getElementById('projectChart').getContext('2d');
        new Chart(ctxProj, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(data['projects'])},
                datasets: [{{
                    label: 'Cost by Project ($)',
                    data: {json.dumps(data['project_costs'])},
                    backgroundColor: '#3b82f6',
                    borderRadius: 8
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
                    y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """
    # Write to a file in the temporary directory or current directory
    output_path = os.path.abspath("dashboard.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"✅ Dashboard generated: {output_path}")
    webbrowser.open(f"file://{output_path}")

if __name__ == "__main__":
    main()
