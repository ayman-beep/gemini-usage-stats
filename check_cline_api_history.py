import json, os, glob

appdata = os.environ.get("APPDATA")

# Check multiple IDE roots for Cline
ide_roots = [
    os.path.join(appdata, "Code", "User", "globalStorage", "saoudrizwan.claude-dev"),
    os.path.join(appdata, "Code - Insiders", "User", "globalStorage", "saoudrizwan.claude-dev"),
    os.path.join(appdata, "Cursor", "User", "globalStorage", "saoudrizwan.claude-dev"),
    os.path.join(appdata, "Windsurf", "User", "globalStorage", "saoudrizwan.claude-dev"),
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
