"""Readable live display shared by finite configuration and science lessons."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--runner', default='scripts.run_configuration_lab')
    args = parser.parse_args()
    folder = args.run_dir.resolve()
    root = tk.Tk()
    root.title('Kavi Live Learning | Reuse, correction and science')
    root.geometry('1120x790')
    root.minsize(940, 700)
    panel = ttk.Frame(root, padding=24)
    panel.pack(fill='both', expand=True)
    ttk.Label(panel, text='Kavi: learning reusable configurations', font=('Segoe UI', 22, 'bold')).pack(anchor='w')
    ttk.Label(panel, text='Learn a rule  →  try new questions  →  correct it  →  check earlier skills',
              font=('Segoe UI', 12)).pack(anchor='w', pady=(8, 20))
    phase = tk.StringVar(value='Preparing — the run starts in four seconds')
    message = tk.StringVar(value='The display will explain each experiment in ordinary language. No lesson has started yet.')
    ttk.Label(panel, textvariable=phase, font=('Segoe UI', 16, 'bold')).pack(anchor='w')
    ttk.Label(panel, textvariable=message, font=('Segoe UI', 12), wraplength=1020).pack(anchor='w', pady=12)
    canvas = tk.Canvas(panel, height=180, bg='#f3f6fa', highlightthickness=0)
    canvas.pack(fill='x', pady=12)
    detail = tk.StringVar(value='Blue boxes are retained computations. Gold marks the part being investigated.')
    ttk.Label(panel, textvariable=detail, font=('Segoe UI', 11), wraplength=1020).pack(anchor='w', pady=8)
    table = ttk.Treeview(panel, columns=('evidence',), height=12)
    table.heading('#0', text='Experiment or lesson')
    table.heading('evidence', text='What happened')
    table.column('#0', width=340)
    table.column('evidence', width=650)
    table.pack(fill='both', expand=True)
    buttons = ttk.Frame(panel)
    buttons.pack(fill='x', pady=(18, 0))
    worker = None
    pause = stopped = False

    def control(action):
        nonlocal pause, stopped
        if action == 'STOP':
            stopped = True
        elif action == 'PAUSE':
            pause = True
        else:
            pause = False
        if folder.exists():
            if action == 'RESUME':
                (folder / 'PAUSE').unlink(missing_ok=True)
            else:
                (folder / action).touch()
        elif stopped:
            phase.set('Stopped before learning')
        elif pause:
            phase.set('Paused before learning')

    for label, action in (('Pause', 'PAUSE'), ('Resume', 'RESUME'), ('Stop', 'STOP')):
        ttk.Button(buttons, text=label, command=lambda a=action: control(a)).pack(side='left', padx=4)
    ttk.Label(buttons, text='One worker · five-minute limit · closing this window stops the run').pack(side='left', padx=16)

    def draw(labels, active):
        canvas.delete('all')
        width = max(canvas.winfo_width(), 900)
        cell = (width-40)/len(labels)
        for i, label in enumerate(labels):
            x, y = 20+i*cell, 36
            canvas.create_rectangle(x, y, x+cell-30, y+100, fill='#ffe0a0' if i == active else '#dceafa', outline='#7090b8', width=2)
            canvas.create_text(x+(cell-30)/2, y+50, text=label, font=('Segoe UI', 12, 'bold'), width=cell-50)
            if i+1 < len(labels):
                canvas.create_line(x+cell-28, y+50, x+cell-4, y+50, arrow='last', width=2, fill='#496685')

    last = None
    def poll():
        nonlocal worker, last
        if worker is None and not folder.exists() and not stopped and not pause:
            worker = subprocess.Popen([sys.executable, '-B', '-u', '-m', args.runner, '--run-dir', str(folder)],
                cwd=Path(__file__).resolve().parents[1], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        path = folder / 'status.json'
        if path.exists():
            try:
                raw = path.read_text(encoding='utf-8')
                if raw != last:
                    status = json.loads(raw)
                    last = raw
                    phase.set(status['phase'] + ' — ' + status['state'])
                    message.set(status['message'])
                    detail.set(status.get('detail', 'Each retained configuration is checked on new inputs.'))
                    draw(status.get('boxes', ['Input', 'Known work', 'Learning', 'Result']), status.get('active', 2))
                    for child in table.get_children():
                        table.delete(child)
                    for row in status['rows']:
                        table.insert('', 'end', text=row['lesson'], values=(row['status'],))
                    if table.get_children():
                        table.see(table.get_children()[-1])
            except (OSError, ValueError, KeyError):
                pass
        elif worker is not None and worker.poll() is not None:
            phase.set('Worker ended before recording progress')
        root.after(200, poll)

    root.protocol('WM_DELETE_WINDOW', lambda: (control('STOP'), root.destroy()))
    root.after(200, lambda: draw(['Inputs', 'Existing pathways', 'Unknown part', 'Checked output'], 2))
    root.after(4000, poll)
    root.mainloop()


if __name__ == '__main__':
    main()
