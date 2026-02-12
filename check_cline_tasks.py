import json, os

appdata = os.environ.get("APPDATA")

# Check multiple IDE roots for Cline
ide_roots = [
    os.path.join(appdata, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "tasks"),
    os.path.join(appdata, "Code - Insiders", "User", "globalStorage", "saoudrizwan.claude-dev", "tasks"),
    os.path.join(appdata, "Cursor", "User", "globalStorage", "saoudrizwan.claude-dev", "tasks"),
    os.path.join(appdata, "Windsurf", "User", "globalStorage", "saoudrizwan.claude-dev", "tasks"),
]

# Find the first valid path
base = None
for path in ide_roots:
    if os.path.exists(path):
        base = path
        break

if base is None:
    print("Cline not found in any IDE")
    exit(1)

task_ids = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d))]
print('Task folders:', len(task_ids))

total_in = 0
total_out = 0
for tid in task_ids:
    ui = os.path.join(base, tid, 'ui_messages.json')
    if not os.path.exists(ui):
        continue
    msgs = json.load(open(ui, 'r', encoding='utf-8'))
    for m in msgs:
        if m.get('say') in ('api_req_started', 'deleted_api_reqs', 'subagent_usage'):
            try:
                data = json.loads(m.get('text', '{}'))
                total_in += data.get('tokensIn', 0) or 0
                total_out += data.get('tokensOut', 0) or 0
            except:
                pass

print('Total from ui_messages: in=%d, out=%d' % (total_in, total_out))
