"""Plain-language live view of a recurrent-configuration experiment."""

import json
import math
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk


def show(folder, *, coverage_repair=False, runner=None, heading=None, subtitle=None, intro=None, legend=None):
    folder = folder.resolve()
    root = tk.Tk()
    root.title('Kavi Live Learning | Connections, correction and retention')
    root.geometry('1180x850')
    root.minsize(1000, 740)
    panel = ttk.Frame(root, padding=20)
    panel.pack(fill='both', expand=True)
    ttk.Label(panel, text=heading or 'Can the connections learn and change?',
              font=('Segoe UI', 22, 'bold')).pack(anchor='w')
    ttk.Label(panel, text=subtitle or 'One correction • later evidence • earlier abilities retained',
              font=('Segoe UI', 12)).pack(anchor='w', pady=(5, 12))
    phase = tk.StringVar(value='Preparing — teaching starts in four seconds')
    message = tk.StringVar(value=intro or 'This experiment teaches a small stream rule. It tests a building block; it does not teach a complete language.')
    ttk.Label(panel, textvariable=phase, font=('Segoe UI', 14, 'bold')).pack(anchor='w')
    ttk.Label(panel, textvariable=message, wraplength=1100, font=('Segoe UI', 11)).pack(anchor='w', pady=10)
    middle = ttk.Frame(panel)
    middle.pack(fill='both', expand=True)
    canvas = tk.Canvas(middle, width=600, height=360, bg='#f6f8fb', highlightthickness=0)
    canvas.pack(side='left', fill='both', expand=True)
    side = ttk.Frame(middle, padding=(14, 0))
    side.pack(side='right', fill='both')
    ttk.Label(side, text='What the tokens mean in this task', font=('Segoe UI', 11, 'bold')).pack(anchor='w')
    ttk.Label(side, text=legend or 'a / b: an event in either stream\n?a / ?b: choose a stream\n0: an even count\n1: an odd count\n\nThe teacher supplies final answers.\nThe learner decides the state connections.\nState numbers have no supplied meaning.',
              font=('Segoe UI', 11), justify='left').pack(anchor='w', pady=8)
    graph_size = tk.StringVar(value='No configuration learned yet')
    ttk.Label(side, textvariable=graph_size, font=('Segoe UI', 11, 'bold')).pack(anchor='w', pady=8)
    stream = tk.StringVar(value='A live input trace appears during the final trial.')
    ttk.Label(side, textvariable=stream, wraplength=320, font=('Segoe UI', 11)).pack(anchor='w', pady=8)
    ttk.Label(panel, text='Circles: learned states   Arrows: token-selected connections   Gold: active state',
              font=('Segoe UI', 10)).pack(anchor='w', pady=8)
    table = ttk.Treeview(panel, columns=('seed', 'evidence'), height=8)
    table.heading('#0', text='Learning step')
    table.column('#0', width=450)
    table.heading('seed', text='Trial seed')
    table.column('seed', width=100)
    table.heading('evidence', text='Observed result')
    table.column('evidence', width=400)
    table.pack(fill='x', pady=5)
    bottom = ttk.Frame(panel)
    bottom.pack(fill='x', pady=(12, 0))
    worker = None
    cancelled = False
    pending_pause = False

    def control(action):
        nonlocal cancelled, pending_pause
        if folder.exists():
            if action == 'RESUME':
                (folder / 'PAUSE').unlink(missing_ok=True)
            else:
                (folder / action).touch()
        elif action == 'STOP':
            cancelled = True
            phase.set('Stopped before teaching')
        elif action == 'PAUSE':
            pending_pause = True
            phase.set('Paused before teaching')
        elif action == 'RESUME':
            pending_pause = False
            start()

    for name, action in (('Pause', 'PAUSE'), ('Resume', 'RESUME'), ('Stop', 'STOP')):
        ttk.Button(bottom, text=name, command=lambda a=action: control(a)).pack(side='left', padx=4)
    ttk.Label(bottom, text='One worker • five-minute limit • closing this window stops active teaching').pack(side='left', padx=12)

    def start():
        nonlocal worker
        if not cancelled and not pending_pause and worker is None and not folder.exists():
            command = runner or ['scripts.run_recurrent_configuration', 'repair-run' if coverage_repair else 'run']
            worker = subprocess.Popen([sys.executable, '-B', '-u', '-m',
                *command, '--run-dir', str(folder)],
                cwd=Path(__file__).resolve().parents[1], stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def draw(value):
        canvas.delete('all')
        graph = value.get('model')
        if not graph:
            canvas.create_text(300, 140, text='The learned connections will appear here.', font=('Segoe UI', 13))
            return
        n = len(graph['outputs'])
        graph_size.set(f"{n} states · {sum(t >= 0 for row in graph['transitions'] for t in row)} connections")
        if n > 16:
            canvas.create_text(300, 140, text=f'{n} states. Full graph is saved in the run folder.', font=('Segoe UI', 13))
            return
        width, height = max(canvas.winfo_width(), 580), max(canvas.winfo_height(), 280)
        cx, cy = width / 2, height / 2
        radius = min(width * .32, height * .34) if n > 1 else 0
        points = [(cx + radius * math.cos(2 * math.pi * i / n - math.pi / 2),
                   cy + radius * math.sin(2 * math.pi * i / n - math.pi / 2)) for i in range(n)]
        groups = {}
        for a, row in enumerate(graph['transitions']):
            for token, b in zip(graph['alphabet'], row):
                if b >= 0:
                    groups.setdefault((a, b), []).append(token)
        for (a, b), tokens in groups.items():
            x, y = points[a]
            xx, yy = points[b]
            if a == b:
                canvas.create_line(x-18, y-18, x-46, y-57, x+46, y-57, x+18, y-18,
                                   smooth=True, arrow='last', fill='#8c9db3')
                tx, ty = x, y-48
            else:
                dx, dy = xx-x, yy-y
                distance = math.hypot(dx, dy)
                ux, uy = dx/distance, dy/distance
                bend = 18
                tx, ty = (x+xx)/2-uy*bend, (y+yy)/2+ux*bend
                canvas.create_line(x+ux*26, y+uy*26, tx, ty, xx-ux*27, yy-uy*27,
                                   smooth=True, arrow='last', fill='#8c9db3')
            canvas.create_text(tx, ty, text=', '.join(tokens), font=('Segoe UI', 9), fill='#334b68')
        active = (value.get('trace') or {}).get('step', {}).get('to', 0)
        for i, (x, y) in enumerate(points):
            canvas.create_oval(x-25, y-25, x+25, y+25,
                               fill='#ffd47a' if i == active else '#dfeaf7', outline='#284c75', width=2)
            canvas.create_text(x, y, text=f"{i}\n→ {graph['outputs'][i]}", font=('Segoe UI', 10, 'bold'))
        if value.get('trace'):
            trace = value['trace']
            tokens = [f'[{s}]' if i == trace['index'] else s for i, s in enumerate(trace['tokens'])]
            stream.set('Input: ' + '  '.join(tokens))

    last = None
    def poll():
        nonlocal last
        try:
            path = folder / 'status.json'
            if path.exists():
                raw = path.read_text(encoding='utf-8')
                if raw != last:
                    value = json.loads(raw)
                    last = raw
                    phase.set(value['phase'] + ' — ' + value['state'])
                    message.set(value['message'])
                    for child in table.get_children():
                        table.delete(child)
                    for row in value['rows']:
                        table.insert('', 'end', text=row['lesson'], values=(row['trial'], row['status']))
                    if table.get_children():
                        table.see(table.get_children()[-1])
                    draw(value)
            elif worker is not None and worker.poll() is not None:
                phase.set('Worker ended before writing progress')
                message.set('No teaching result is available. Inspect the launch before retrying.')
        except (OSError, ValueError, KeyError):
            pass
        root.after(200, poll)

    root.protocol('WM_DELETE_WINDOW', lambda: (control('STOP'), root.destroy()))
    root.after(4000, start)
    root.after(100, lambda: draw({}))
    poll()
    root.mainloop()
