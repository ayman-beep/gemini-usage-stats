import os

roots = [
    r'C:\Users\User\AppData\Roaming\Code\User\globalStorage',
    r'C:\Users\User\AppData\Roaming\Code - Insiders\User\globalStorage',
    r'C:\Users\User\AppData\Roaming\Cursor\User\globalStorage',
    r'C:\Users\User\AppData\Roaming\Windsurf\User\globalStorage',
    r'C:\Users\User\AppData\Roaming\Antigravity\User\globalStorage',
]

exts = ['rooveterinaryinc.roo-cline', 'rooveterinaryinc.roo-code-nightly']

for root in roots:
    ide_name = os.path.basename(os.path.dirname(root))
    for ext in exts:
        state_path = os.path.join(root, ext, 'state', 'taskHistory.json')
        tasks_path = os.path.join(root, ext, 'tasks')
        
        has_history = os.path.exists(state_path)
        has_tasks = os.path.exists(tasks_path)
        num_tasks = len(os.listdir(tasks_path)) if has_tasks else 0
        
        if has_history or has_tasks:
            print(f'{ide_name}/{ext}: history={has_history}, tasks={num_tasks}')
