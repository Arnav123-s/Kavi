"""Readable live progress for the finite multi-track curriculum."""

import json
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import ttk


def show(run_dir,runner='scripts.run_foundation_curriculum',label='Foundation teaching across three tracks'):
    run_dir=run_dir.resolve()
    root=tk.Tk()
    root.title('Kavi | '+label)
    root.geometry('1100x780')
    panel=ttk.Frame(root,padding=22)
    panel.pack(fill='both',expand=True)
    ttk.Label(panel,text='Learning, correcting, and checking what survives',font=('Segoe UI',20,'bold'),wraplength=1000).pack(anchor='w')
    ttk.Label(panel,text='Mathematics • scientific models • language and argument structure',font=('Segoe UI',12)).pack(anchor='w',pady=12)
    title=tk.StringVar(value='Preparing a bounded foundation trial')
    detail=tk.StringVar(value='Advanced competence will be assessed separately; these lessons are foundations.')
    ttk.Label(panel,textvariable=title,font=('Segoe UI',13,'bold'),wraplength=1000).pack(anchor='w',pady=8)
    ttk.Label(panel,textvariable=detail,wraplength=1000).pack(anchor='w',pady=8)
    bar=ttk.Progressbar(panel,maximum=32)
    bar.pack(fill='x',pady=10)
    area=ttk.Frame(panel)
    area.pack(fill='both',expand=True)
    scroll=ttk.Scrollbar(area)
    scroll.pack(side='right',fill='y')
    table=ttk.Treeview(area,columns=('trial','arm','state'),yscrollcommand=scroll.set)
    table.heading('#0',text='Lesson')
    table.column('#0',width=470)
    for key,label in [('trial','Trial'),('arm','Learning condition'),('state','Evidence')]:
        table.heading(key,text=label)
        table.column(key,width=160)
    table.pack(fill='both',expand=True)
    scroll.configure(command=table.yview)
    bottom=ttk.Frame(panel)
    bottom.pack(fill='x',pady=12)
    def control(action):
        if run_dir.exists():
            if action=='RESUME': (run_dir/'PAUSE').unlink(missing_ok=True)
            else: (run_dir/action).touch()
    for name,action in [('Pause','PAUSE'),('Resume','RESUME'),('Stop','STOP')]:
        ttk.Button(bottom,text=name,command=lambda a=action:control(a)).pack(side='left',padx=5)
    ttk.Label(bottom,text='One worker • five-minute maximum • completed evidence stays on disk').pack(side='left',padx=16)
    def start():
        if not run_dir.exists():
            subprocess.Popen([sys.executable,'-B','-u','-m',runner,'run','--run-dir',str(run_dir)],
                cwd=Path(__file__).resolve().parents[1],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    last=None
    def poll():
        nonlocal last
        try:
            path=run_dir/'status.json'
            if path.exists():
                raw=path.read_text(encoding='utf-8')
                if raw!=last:
                    last=raw
                    value=json.loads(raw)
                    title.set(value['phase']+' — '+value['state'])
                    detail.set(value['message'])
                    bar['maximum']=value['total']
                    bar['value']=value['finished']
                    for child in table.get_children(): table.delete(child)
                    for row in value['rows']:
                        table.insert('', 'end',text=row['lesson'],values=(row['trial'],row['arm'],row['status']))
                    if table.get_children(): table.see(table.get_children()[-1])
        except (OSError,ValueError,KeyError): pass
        root.after(250,poll)
    root.protocol('WM_DELETE_WINDOW',lambda:(control('STOP'),root.destroy()))
    root.after(1500,start)
    poll()
    root.mainloop()
