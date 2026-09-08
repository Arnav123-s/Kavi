"""A local conversation window with visible source and calculation provenance."""

import queue
import threading
import tkinter as tk
from tkinter import ttk
import webbrowser

from .conversation import Conversation


def main():
    model=Conversation()
    root=tk.Tk()
    root.title('Talk to Kavi')
    root.geometry('1080x790')
    root.minsize(800,600)
    root.configure(bg='#f2f4f8')
    frame=ttk.Frame(root,padding=24)
    frame.pack(fill='both',expand=True)
    ttk.Label(frame,text='Talk to Kavi',font=('Segoe UI',24,'bold')).pack(anchor='w')
    ttk.Label(frame,text='Calculations • Science • Source passages',font=('Segoe UI',12)).pack(anchor='w',pady=(5,15))
    status=tk.StringVar(value=f'Ready · {len(model.sources.records)} source documents · {len(model.dictionary.senses):,} dictionary entries · runs on this device')
    ttk.Label(frame,textvariable=status,font=('Segoe UI',11)).pack(anchor='w',pady=(0,12))
    area=ttk.Frame(frame)
    area.pack(fill='both',expand=True)
    history=tk.Text(area,wrap='word',font=('Segoe UI',12),bg='white',relief='flat',padx=18,pady=15,state='disabled')
    history.pack(side='left',fill='both',expand=True)
    scroll=ttk.Scrollbar(area,command=history.yview)
    scroll.pack(side='right',fill='y')
    history.configure(yscrollcommand=scroll.set)
    history.tag_configure('speaker',foreground='#174e85',font=('Segoe UI',12,'bold'))
    history.tag_configure('note',foreground='#5a6472',font=('Segoe UI',10))
    line=ttk.Frame(frame)
    line.pack(fill='x',pady=(16,8))
    entry=ttk.Entry(line,font=('Segoe UI',13))
    entry.pack(side='left',fill='x',expand=True,ipady=9)
    messages=queue.Queue()
    stopping=threading.Event()
    paused=threading.Event()
    busy=False
    latest=None

    def append(who,text,note=''):
        history.configure(state='normal')
        history.insert('end',who+'\n','speaker')
        history.insert('end',text+'\n')
        if note: history.insert('end',note+'\n','note')
        history.insert('end','\n')
        history.configure(state='disabled')
        history.see('end')

    def check():
        while paused.is_set():
            if stopping.wait(.05): raise InterruptedError('Stopped')
        if stopping.is_set(): raise InterruptedError('Stopped')

    def submit():
        nonlocal busy
        question=entry.get().strip()
        if busy or not question: return
        busy=True
        stopping.clear()
        paused.clear()
        append('You',question)
        entry.delete(0,'end')
        status.set('Working on your question…')
        def worker():
            try: messages.put(model.answer(question,check))
            except Exception as error: messages.put({'kind':'unknown','text':'The question could not be completed: '+str(error)})
        threading.Thread(target=worker,daemon=True).start()

    ttk.Button(line,text='Send',command=submit).pack(side='left',padx=(10,0),ipady=7)
    entry.bind('<Return>',lambda event:submit())
    buttons=ttk.Frame(frame)
    buttons.pack(fill='x')
    def pause():
        if paused.is_set(): paused.clear(); status.set('Resumed')
        else: paused.set(); status.set('Paused')
    ttk.Button(buttons,text='Pause / Resume',command=pause).pack(side='left')
    ttk.Button(buttons,text='Stop answer',command=stopping.set).pack(side='left',padx=8)
    def explain():
        if latest: append('How this answer was made',latest.get('explanation','No calculation or source evidence was available.'))
    ttk.Button(buttons,text='Show reasoning / source',command=explain).pack(side='left')
    def source():
        if latest and latest.get('sources'): webbrowser.open(latest['sources'][0]['url'])
    ttk.Button(buttons,text='Open source',command=source).pack(side='left',padx=8)
    ttk.Label(frame,text='Try: What causes earthquakes?    |    (17 + 19) * (17 + 19)    |    Kinetic energy for mass 80 kg and speed 2.4 m/s',
              wraplength=990,font=('Segoe UI',10)).pack(anchor='w',pady=(12,0))
    append('Kavi','Hello. Ask me a question. I can calculate and look up material in my source library. I will tell you when I cannot answer.',
           'Source passages are retrieved text. They do not demonstrate unrestricted language understanding.')
    def poll():
        nonlocal busy,latest
        try: result=messages.get_nowait()
        except queue.Empty: pass
        else:
            busy=False
            latest=result
            append('Kavi',result['text'],{'source':'Source lookup','dictionary':'Dictionary lookup','calculation':'Calculated answer','unknown':'Not answered'}.get(result['kind'],'Conversation'))
            status.set(f"Ready · last answer {result.get('seconds',0):.3f} seconds")
        root.after(100,poll)
    root.protocol('WM_DELETE_WINDOW',lambda:(stopping.set(),root.destroy()))
    entry.focus_set()
    root.after(100,poll)
    root.mainloop()


if __name__=='__main__':
    main()
