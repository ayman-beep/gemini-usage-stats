import os
import json

base = os.path.join(os.environ['APPDATA'], 'Antigravity', 'User', 'globalStorage', 'kilocode.kilo-code', 'tasks')
task_ids = os.listdir(base)[:5]

for tid in task_ids:
    task_path = os.path.join(base, tid)
    print(f'Task: {tid}')
    
    # Check task_metadata.json
    meta_file = os.path.join(task_path, 'task_metadata.json')
    if os.path.exists(meta_file):
        meta = json.load(open(meta_file, 'r', encoding='utf-8'))
        print(f'  task_metadata.json keys: {list(meta.keys())}')
    
    # Check api_conversation_history.json for model info
    api_file = os.path.join(task_path, 'api_conversation_history.json')
    if os.path.exists(api_file):
        api = json.load(open(api_file, 'r', encoding='utf-8'))
        if api:
            first_msg = api[0]
            print(f'  First msg keys: {list(first_msg.keys())}')
            if 'content' in first_msg:
                content = first_msg['content']
                if isinstance(content, list):
                    for item in content[:2]:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            text = item.get('text', '')[:200]
                            print(f'  First content: {text}...')
                            break
