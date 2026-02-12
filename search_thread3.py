import json, os, glob

f = glob.glob(os.path.expanduser("~/.local/share/amp/threads/T-019c14fa*"))[0]
data = json.load(open(f, "r", encoding="utf-8"))

msg = data["messages"][12]
for j, part in enumerate(msg.get("content", [])):
    part_str = json.dumps(part)
    if "gemini-3-pro-image-preview" in part_str:
        # Print a trimmed version focusing on usage
        print(f"content[{j}] keys: {list(part.keys()) if isinstance(part, dict) else type(part)}")
        print(json.dumps(part, indent=2)[:2000])
        print("=====")
