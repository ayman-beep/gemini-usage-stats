import json, os, glob

base = os.path.join(os.environ['APPDATA'], 'Antigravity', 'User', 'globalStorage', 'saoudrizwan.claude-dev')
files = glob.glob(os.path.join(base, 'tasks', '*', 'api_conversation_history.json'))
print('api_conversation_history.json files:', len(files))

total = 0
total_out = 0

for f in files:
    data = json.load(open(f, 'r', encoding='utf-8'))
    # Check the structure of the first file
    if total == 0:
        print('Sample message structure:', json.dumps(data[0], indent=2)[:500] if data else 'empty')
    
    for m in data:
        tokens = m.get('tokens', {})
        if tokens:
            total += tokens.get('input_tokens', 0)
            total_out += tokens.get('output_tokens', 0)

print(f'From api_conversation_history: in={total}, out={total_out}')
