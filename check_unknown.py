import re

html = open("e:/gemini cli usage/dashboard.html", "r", encoding="utf-8").read()

# Count unknown entries
count = html.count("title='unknown'")
print(f"'unknown' entries in dashboard: {count}")

# Find all model names from the model table rows
rows = re.findall(r"title='([^']+)'>\1</td>.*?\$([0-9,.]+)</td>", html, re.DOTALL)
for m, cost in rows:
    print(f"  {m}: ${cost}")
