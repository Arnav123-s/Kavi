"""Demonstrate context emerging from input and teaching after an unsupported route."""

import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kavi.circuit_runtime import write_json
from kavi.grounded_language import LanguageModel,tokens
from kavi.incremental_paths import IncrementalPaths
from kavi.procedure_core import ProcedureLibrary


def lessons():
    rows=[]
    for symbol in ('a','α','alpha'):
        for left,right in ((2,3),(4,5)):
            rows.append({'text':f'{symbol} equals {left} plus {right}', 'source':'authored:incremental-paths',
                         'target':{'kind':'calculation','label':'add','inputs':[left,right]}})
        for letter in ('alpha','beta'):
            rows.append({'text':f'{symbol} denotes the Greek letter {letter}', 'source':'authored:incremental-paths',
                         'target':{'kind':'relation','label':'notation_mapping','slots':{'letter':letter}}})
    for subject,quality in (('bird','small'),('child','curious')):
        rows.append({'text':f'a {subject} is {quality}', 'source':'authored:incremental-paths',
                     'target':{'kind':'relation','label':'description','slots':{'subject':subject,'quality':quality}}})
    return rows


def trace(graph,text,notify=lambda *_:None):
    graph.reset()
    states=[]
    for word in tokens(text):
        state={'token':word,**graph.feed(word)}
        states.append(state)
        notify(word,state)
    return {'text':text,'states':states,'final':graph.finish()}


def run(run_dir):
    run_dir=run_dir.resolve()
    if not run_dir.is_relative_to(ROOT/'runs') or run_dir.exists(): raise ValueError('Use a new run directory')
    run_dir.mkdir(parents=True)
    started=time.monotonic()
    def check():
        if (run_dir/'STOP').exists() or time.monotonic()-started>60: raise InterruptedError('Stopped or time exhausted')
        while (run_dir/'PAUSE').exists():
            if (run_dir/'STOP').exists() or time.monotonic()-started>60: raise InterruptedError('Stopped while paused')
            time.sleep(.05)
    progress=[]
    def emit(message):
        write_json(run_dir/'status.json',{'state':'running','phase':'Meaning from incoming words','message':message,
                   'finished':len(progress),'total':8,'rows':progress})
    def present(word,state):
        check()
        roles=', '.join(state['possible_roles']) or 'no compatible learned pathway'
        emit(f'Incoming token: {word}. Still possible: {roles}. Active signal bindings: {state["active_bindings"]}.')
        # Declared input-presentation pacing, not additional learning or compute.
        time.sleep(.2)
    result={'schema':'kavi.incremental-path-trial.v1','state':'running'}
    try:
        emit('Learning annotated constructions. No subject-context label is supplied at query time.')
        language=LanguageModel()
        language.teach(lessons(),check=check)
        graph=IncrementalPaths(language.rules)
        result.update(teaching=lessons(),initial_graph_bytes=len(graph.encoded()),initial_nodes=len(graph.nodes))
        prompts=['a equals 12 plus 13','α equals 12 plus 13','alpha equals 12 plus 13',
                 'a fox is alert','a denotes the Greek letter gamma']
        before=[]
        for text in prompts:
            check()
            row=trace(graph,text,present)
            row['batch_reference']=language.interpret(text)
            row['agrees_with_reference']=row['final']['complete']==[row['batch_reference'].get('meaning')]
            before.append(row)
            progress.append({'trial':1,'arm':'incremental graph','lesson':text,'status':row['final']['state']})
            emit('More words narrow possible interpretations: '+text)
        unknown='a multiplies 12 by 13'
        result['before_teaching_new_construction']=trace(graph,unknown,present)
        # Its unsupported answer is retained. Teach two different examples, then
        # assess a fresh query rather than re-score the original as successful.
        new_lessons=[{'text':f'a multiplies {a} by {b}','source':'authored:incremental-correction',
                     'target':{'kind':'calculation','label':'multiply','inputs':[a,b]}}
                     for a,b in ((2,3),(4,5))]
        language.teach(new_lessons,check=check)
        graph=IncrementalPaths(language.rules)
        result['new_teaching']=new_lessons
        result['after_teaching_fresh_query']=trace(graph,'a multiplies 17 by 19',present)
        result['retention']=[trace(graph,text)['final']['complete']==old['final']['complete'] for text,old in zip(prompts,before)]
        lib=ProcedureLibrary.load(ROOT/'experiments/library-20260907-compiled.json')
        result['arithmetic_answers']=[language.answer(text,lib) for text in (prompts[0],'a multiplies 17 by 19')]
        result.update(traces=before,final_graph=json.loads(graph.encoded()),final_graph_bytes=len(graph.encoded()),
                      final_nodes=len(graph.nodes),language_bytes=len(language.encoded()),state='completed')
        progress.extend([{'trial':2,'arm':'teach after no path','lesson':unknown,'status':'Unsupported answer preserved'},
                         {'trial':2,'arm':'new input','lesson':'a multiplies 17 by 19','status':'Fresh result checked'},
                         {'trial':2,'arm':'retention','lesson':'Earlier interpretations','status':f"{sum(result['retention'])}/5 retained"}])
        (run_dir/'language.json').write_bytes(language.encoded())
    except Exception as error: result.update(state='failed',error=str(error))
    result['seconds']=time.monotonic()-started
    write_json(run_dir/'results.json',result)
    write_json(run_dir/'status.json',{'state':result['state'],'phase':'Finished','message':'Token-by-token evidence and the original unsupported answer are saved.',
               'finished':len(progress),'total':8,'rows':progress})
    return 0 if result['state']=='completed' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['run','live'])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir,'scripts.run_incremental_paths','Follow meaning as words arrive')
        return 0
    return run(args.run_dir)


if __name__=='__main__': raise SystemExit(main())
