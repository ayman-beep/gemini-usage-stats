import json, os, re
from collections import Counter

appdata = os.environ.get("APPDATA", os.path.join(os.path.expanduser("~"), "AppData", "Roaming"))
base = os.path.join(appdata, "Code", "User", "globalStorage", "kilocode.kilo-code", "tasks")
dirs = sorted(os.listdir(base))

provider_counter = Counter()
model_found = Counter()

for tid in dirs:
    ui = os.path.join(base, tid, "ui_messages.json")
    if not os.path.exists(ui):
        continue
    msgs = json.load(open(ui, "r", encoding="utf-8"))
    
    task_provider = ""
    task_model = ""
    
    for msg in msgs:
        # Check for inferenceProvider
        if msg.get("say") == "api_req_started":
            data = json.loads(msg.get("text", "{}"))
            if data.get("inferenceProvider"):
                task_provider = data["inferenceProvider"]
        
        # Check for modelId in various places
        if msg.get("apiMetrics"):
            print("Found apiMetrics:", msg["apiMetrics"])
        if msg.get("modelId"):
            task_model = msg["modelId"]
        if msg.get("say") == "api_req_started":
            data = json.loads(msg.get("text", "{}"))
            if data.get("model"):
                task_model = data["model"]
            if data.get("modelId"):
                task_model = data["modelId"]
    
    label = task_model if task_model else task_provider if task_provider else "unknown"
    model_found[label] += 1

print("Model/Provider breakdown across all tasks:")
for m, c in model_found.most_common():
    print(f"  {m}: {c} tasks")
