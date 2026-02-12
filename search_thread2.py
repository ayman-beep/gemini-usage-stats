import json, os, glob

f = glob.glob(os.path.expanduser("~/.local/share/amp/threads/T-019c14fa*"))[0]
data = json.load(open(f, "r", encoding="utf-8"))

for i, msg in enumerate(data.get("messages", [])):
    # Check top-level usage
    usage = msg.get("usage", {})
    # Also recursively search for nested usage with gemini
    raw = json.dumps(msg)
    if "gemini-3-pro-image-preview" in raw:
        # Find where the usage is nested
        for key in msg:
            if key == "content" and isinstance(msg[key], list):
                for j, part in enumerate(msg[key]):
                    part_str = json.dumps(part)
                    if "gemini-3-pro-image-preview" in part_str:
                        print(f"Message {i}, role={msg.get('role')}, content[{j}] type={part.get('type')}")
                        # Look for usage inside
                        if isinstance(part, dict):
                            for k, v in part.items():
                                if isinstance(v, list):
                                    for item in v:
                                        if isinstance(item, dict) and "usage" in item:
                                            print(f"  Found usage: {json.dumps(item['usage'], indent=2)}")
                                elif isinstance(v, dict) and "usage" in v:
                                    print(f"  Found usage in {k}: {json.dumps(v['usage'], indent=2)}")
            elif isinstance(msg[key], list):
                for j, item in enumerate(msg[key]):
                    if isinstance(item, dict) and "gemini-3-pro-image-preview" in json.dumps(item):
                        print(f"Message {i}, role={msg.get('role')}, {key}[{j}]")
                        if "usage" in item:
                            print(f"  usage: {json.dumps(item['usage'], indent=2)}")
