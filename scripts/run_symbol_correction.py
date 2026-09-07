"""Teach one missing symbol construction and test structural transfer."""

import argparse
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kavi.circuit_runtime import write_json
from kavi.grounded_language import LanguageModel
from kavi.incremental_paths import IncrementalPaths
from kavi.procedure_core import ProcedureLibrary
from scripts.run_incremental_paths import lessons,trace


def run(folder):
    folder=folder.resolve()
    if not folder.is_relative_to(ROOT/'runs') or folder.exists(): raise ValueError('Use a new directory')
    folder.mkdir(parents=True)
    started=time.monotonic()
    result={'state':'running','scope':'Teacher-annotated missing symbol construction; no global alias rule or mistake memory in model.'}
    progress=[]
    def check():
        if (folder/'STOP').exists() or time.monotonic()-started>60: raise InterruptedError('Stopped or time exhausted')
        while (folder/'PAUSE').exists():
            if (folder/'STOP').exists() or time.monotonic()-started>60: raise InterruptedError('Stopped while paused')
            time.sleep(.05)
    def present(word,state):
        check()
        write_json(folder/'status.json',{'state':'running','phase':'Correct a missing symbol pathway',
                   'message':f"Token {word}: {', '.join(state['possible_roles']) or 'no compatible pathway'}",
                   'finished':len(progress),'total':4,'rows':progress})
        time.sleep(.2)
    try:
        model=LanguageModel()
        model.teach([row for row in lessons() if not row['text'].startswith('α')],check=check)
        before=IncrementalPaths(model.rules)
        result['before']=trace(before,'α equals 12 plus 13',present)
        result['before_bytes']=len(before.encoded())
        result['before_nodes']=len(before.nodes)
        progress.append({'trial':1,'arm':'before correction','lesson':'Greek alpha in arithmetic','status':result['before']['final']['state']})
        teaching=[row for row in lessons() if row['text'].startswith('α equals')]
        model.teach(teaching,check=check)
        after=IncrementalPaths(model.rules)
        result['teaching']=teaching
        result['fresh']=trace(after,'α equals 17 plus 19',present)
        result['article_retained']=trace(before,'a fox is alert')['final']['complete']==trace(after,'a fox is alert')['final']['complete']
        result['invalid_article']=trace(after,'α fox is alert')['final']['state']
        other=trace(after,'a equals 17 plus 19')
        result['shared_final_nodes']=sorted(set(result['fresh']['final']['active_nodes']) & set(other['final']['active_nodes']))
        meaning=result['fresh']['final']['complete'][0]
        library=ProcedureLibrary.load(ROOT/'experiments/library-20260907-compiled.json')
        result['value']=library.execute(meaning['label'],tuple(meaning['inputs']),check=check).value
        result.update(after_bytes=len(after.encoded()),after_nodes=len(after.nodes),model_bytes=len(model.encoded()),state='completed')
        progress.extend([{'trial':2,'arm':'after correction','lesson':'New numbers 17 and 19','status':str(result['value'])},
                         {'trial':2,'arm':'retention','lesson':'English article a','status':str(result['article_retained'])},
                         {'trial':2,'arm':'negative case','lesson':'Greek alpha as article','status':result['invalid_article']}])
        (folder/'model.json').write_bytes(model.encoded())
        (folder/'graph.json').write_bytes(after.encoded())
    except Exception as error: result.update(state='failed',error=str(error))
    result['seconds']=time.monotonic()-started
    write_json(folder/'results.json',result)
    write_json(folder/'status.json',{'state':result['state'],'phase':'Finished','message':'The correction changed structure; original failure stays in the experiment log.',
               'finished':len(progress),'total':4,'rows':progress})
    return 0 if result['state']=='completed' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['run','live'])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir,'scripts.run_symbol_correction','Correct the symbol pathway and test new inputs')
        return 0
    return run(args.run_dir)


if __name__=='__main__': raise SystemExit(main())
