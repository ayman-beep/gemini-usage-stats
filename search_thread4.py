import json, os, glob

f = glob.glob(os.path.expanduser("~/.local/share/amp/threads/T-019c14fa*"))[0]
data = json.load(open(f, "r", encoding="utf-8"))

msg = data["messages"][12]
for j, part in enumerate(msg.get("content", [])):
    part_str = json.dumps(part)
    if "gemini-3-pro-image-preview" in part_str:
        run = part.get("run", {})
        # Check run keys
        print(f"content[{j}] run keys: {list(run.keys())}")
        # Look for usage in run
        if "usage" in run:
            print(f"  run.usage: {json.dumps(run['usage'], indent=2)}")
        # Check result items
        for k, item in enumerate(run.get("result", [])):
            if isinstance(item, dict):
                print(f"  result[{k}] keys: {list(item.keys())}")
                if "usage" in item:
                    print(f"  result[{k}].usage: {json.dumps(item['usage'], indent=2)}")
        # Check subMessages
        for k, sub in enumerate(run.get("subMessages", [])):
            if isinstance(sub, dict) and "usage" in sub:
                print(f"  subMessages[{k}].usage: {json.dumps(sub['usage'], indent=2)}")
        # Deep search for usage
        def find_usage(obj, path=""):
            if isinstance(obj, dict):
                if "usage" in obj and isinstance(obj["usage"], dict) and "model" in obj["usage"]:
                    print(f"  FOUND at {path}.usage: {json.dumps(obj['usage'], indent=2)}")
                for k, v in obj.items():
                    if k != "data":  # skip base64 image data
                        find_usage(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    find_usage(v, f"{path}[{i}]")
        find_usage(part, f"content[{j}]")
        print("=====")
