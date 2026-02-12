import json, os, glob, re

f = glob.glob(os.path.expanduser("~/.local/share/amp/threads/T-019c14fa*"))[0]
text = open(f, "r", encoding="utf-8").read()

# Search for gemini mentions
for m in re.finditer(r"gemini[^\"]{0,60}", text, re.IGNORECASE):
    start = max(0, m.start() - 80)
    end = min(len(text), m.end() + 80)
    print("..." + text[start:end] + "...")
    print("---")

# Also check for painter tool calls
for m in re.finditer(r"painter|image.preview", text, re.IGNORECASE):
    start = max(0, m.start() - 80)
    end = min(len(text), m.end() + 80)
    print("..." + text[start:end] + "...")
    print("---")
