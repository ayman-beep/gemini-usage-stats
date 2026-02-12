import re
html = open('e:/gemini cli usage/dashboard.html', 'r', encoding='utf-8').read()
matches = re.findall(r"title='([^']+)'", html)
seen = set()
for m in matches:
    if m not in seen:
        seen.add(m)
        print(m)
