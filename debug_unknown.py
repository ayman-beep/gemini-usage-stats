import json, os, glob
from collections import Counter

appdata = os.environ.get("APPDATA")
bases = {
    "Cline": os.path.join(appdata, "Antigravity", "User", "globalStorage", "saoudrizwan.claude-dev"),
    "Roo Code": os.path.join(appdata, "Antigravity", "User", "globalStorage", "rooveterinaryinc.roo-cline"),
    "Roo Nightly": os.path.join(appdata, "Antigravity", "User", "globalStorage", "rooveterinaryinc.roo-code-nightly"),
    "Kilo Code": os.path.join(appdata, "Antigravity", "User", "globalStorage", "kilocode.kilo-code"),
}

for name, base in bases.items():
    # Check taskHistory
    hist = os.path.join(base, "state", "taskHistory.json")
    if os.path.exists(hist):
        tasks = json.load(open(hist, "r", encoding="utf-8"))
        models = Counter()
        total_in = 0
        total_out = 0
        for t in tasks:
            m = t.get("modelId") or "NO_MODEL"
            models[m] += 1
            total_in += t.get("tokensIn", 0) or 0
            total_out += t.get("tokensOut", 0) or 0
        print(f"{name} (taskHistory): {len(tasks)} tasks, models={dict(models)}, in={total_in}, out={total_out}")
    else:
        # Check individual tasks via ui_messages
        tasks_dir = os.path.join(base, "tasks")
        if not os.path.exists(tasks_dir):
            print(f"{name}: no data")
            continue
        
        task_dirs = [d for d in os.listdir(tasks_dir) if os.path.isdir(os.path.join(tasks_dir, d))]
        print(f"{name} (ui_messages fallback): {len(task_dirs)} task folders")
        
        models = Counter()
        total_in = 0
        total_out = 0
        for tid in task_dirs:
            ui = os.path.join(tasks_dir, tid, "ui_messages.json")
            if not os.path.exists(ui):
                continue
            msgs = json.load(open(ui, "r", encoding="utf-8"))
            task_model = "unknown"
            for msg in msgs:
                mi = msg.get("modelInfo", {})
                if mi and mi.get("modelId"):
                    task_model = mi["modelId"]
                say = msg.get("say", "")
                if say in ("api_req_started", "deleted_api_reqs", "subagent_usage"):
                    try:
                        data = json.loads(msg.get("text", "{}"))
                        total_in += data.get("tokensIn", 0) or 0
                        total_out += data.get("tokensOut", 0) or 0
                    except:
                        pass
            models[task_model] += 1
        print(f"  models={dict(models)}, in={total_in}, out={total_out}")
