import json, os

base = os.path.join(os.environ['APPDATA'], 'Antigravity', 'User', 'globalStorage', 'saoudrizwan.claude-dev', 'tasks')
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
