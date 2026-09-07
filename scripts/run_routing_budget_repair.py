"""Retain the learned focus for its full allowance; do not widen on a sublimit."""

import argparse
from dataclasses import asdict
from itertools import product
import json
from pathlib import Path
import random
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kavi.circuit_runtime import write_json
from kavi.experience_router import ExperienceRouter
from kavi.procedure_core import ProcedureLibrary,Limits,describe
from kavi.procedure_search import ProgramSearch,ProgramExample,SearchExhausted


def run(folder):
    folder=folder.resolve()
    if not folder.is_relative_to(ROOT/'runs') or folder.exists(): raise ValueError('Use a new directory')
    folder.mkdir(parents=True)
    started=time.monotonic()
    result={'state':'running','rows':[],'change':'Full existing per-task budget retained in learned component set; no premature broadening.'}
    progress=[]
    def check():
        if (folder/'STOP').exists() or time.monotonic()-started>60: raise InterruptedError('Stopped or time exhausted')
        while (folder/'PAUSE').exists():
            if (folder/'STOP').exists() or time.monotonic()-started>60: raise InterruptedError('Stopped while paused')
            time.sleep(.05)
    def emit(message):
        write_json(folder/'status.json',{'state':result['state'],'phase':'Keep a useful route active','message':message,
                   'finished':len(progress),'total':2,'rows':progress})
    try:
        prior=json.loads((ROOT/'runs/experience-routing-20260907-01/results.json').read_text(encoding='utf-8'))
        library=ProcedureLibrary.from_dict(prior['base'])
        router=ExperienceRouter(prior['router']['tree'])
        for previous in prior['rows']:
            if previous['mode']!='learned' or previous['task']!='affine_plus_one': continue
            check()
            emit('The learned add/multiply route keeps its full allowance; no new operation hint is supplied.')
            teaching=[ProgramExample(tuple(e['inputs']),e['target']) for e in previous['teaching']]
            search=ProgramSearch(library,max_nodes=3,max_candidates=4000,max_candidate_cases=80000,
                                 max_seconds=2,max_cache_entries=12000,allowed_tags=('call',),
                                 allowed_names=router.select(previous['features']),check=check,
                                 limits=Limits(max_calls=5000,max_gates=200000,max_iterations=256))
            row={'seed':previous['seed'],'body':None}
            try:
                row['body']=search.learn(3,teaching)
                row['description']=describe(row['body'])
            except SearchExhausted as error: row['failure']=str(error)
            row['stats']=asdict(search.stats)
            result['rows'].append(row)
            progress.append({'trial':row['seed'],'arm':'retain learned focus','lesson':'Product plus two offsets',
                             'status':'Found' if row['body'] else 'Not acquired'})
        for row in result['rows']:
            final=[]
            for xs in random.Random(row['seed']).sample(list(product(range(80,87),repeat=3)),12):
                check()
                expected=xs[0]*xs[1]+xs[2]+1
                value=None if row['body'] is None else library.execute_expr(row['body'],xs,check=check).value
                final.append({'inputs':xs,'expected':expected,'value':value,'correct':value==expected})
            row['final']=final
        result['state']='completed'
    except Exception as error: result.update(state='failed',error=str(error))
    result['seconds']=time.monotonic()-started
    write_json(folder/'results.json',result)
    emit('Results saved against fresh inputs; original scores remain unchanged.')
    return 0 if result['state']=='completed' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['run','live'])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir,'scripts.run_routing_budget_repair','Keep the learned focus until its budget is used')
        return 0
    return run(args.run_dir)


if __name__=='__main__': raise SystemExit(main())
