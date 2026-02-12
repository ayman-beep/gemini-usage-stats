import json, os

# Check Kilo cache for provider-to-model mappings
cache = os.path.join(os.environ["APPDATA"], "Antigravity", "User", "globalStorage", "kilocode.kilo-code", "cache")
for f in os.listdir(cache):
    if "endpoint" in f:
        data = json.load(open(os.path.join(cache, f), "r", encoding="utf-8"))
        for k, v in data.items():
            name = v.get("displayName", k)
            print(f"  {f} -> {name}")
            break

# Now check each task to find the actual model used per provider
base = os.path.join(os.environ["APPDATA"], "Antigravity", "User", "globalStorage", "kilocode.kilo-code", "tasks")
provider_models = {}
for tid in os.listdir(base):
    ui = os.path.join(base, tid, "ui_messages.json")
    if not os.path.exists(ui):
        continue
    msgs = json.load(open(ui, "r", encoding="utf-8"))
    provider = None
    for msg in msgs:
        if msg.get("say") == "api_req_started":
            data = json.loads(msg.get("text", "{}"))
            provider = data.get("inferenceProvider", "")
            # Check the request field for model
            req = data.get("request", "")
            if isinstance(req, str) and "model" in req:
                import re
                m = re.search(r'"model"\s*:\s*"([^"]+)"', req)
                if m:
                    model = m.group(1)
                    if provider not in provider_models:
                        provider_models[provider] = set()
                    provider_models[provider].add(model)
            break

print("\nProvider -> Model mapping from task requests:")
for p, models in sorted(provider_models.items()):
    print(f"  {p or '(none)'}: {models}")

# Also check Roo Code
for ext in ["rooveterinaryinc.roo-cline", "rooveterinaryinc.roo-code-nightly"]:
    roo_base = os.path.join(os.environ["APPDATA"], "Antigravity", "User", "globalStorage", ext, "tasks")
    if not os.path.exists(roo_base):
        continue
    for tid in os.listdir(roo_base):
        ui = os.path.join(roo_base, tid, "ui_messages.json")
        if not os.path.exists(ui):
            continue
        msgs = json.load(open(ui, "r", encoding="utf-8"))
        for msg in msgs:
            if msg.get("say") == "api_req_started":
                data = json.loads(msg.get("text", "{}"))
                provider = data.get("inferenceProvider", "(none)")
                req = data.get("request", "")
                if isinstance(req, str) and "model" in req:
                    import re
                    m = re.search(r'"model"\s*:\s*"([^"]+)"', req)
                    if m:
                        print(f"\n  Roo ({ext}): provider={provider}, model={m.group(1)}")
                break
