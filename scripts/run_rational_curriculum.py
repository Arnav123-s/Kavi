"""Teach exact signed and fractional compositions using acquired circuit arithmetic."""

import argparse
from dataclasses import asdict
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import random
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kavi.circuit_runtime import write_json
from kavi.procedure_core import ProcedureLibrary,Limits,describe
from kavi.procedure_search import ProgramSearch,ProgramExample,SearchExhausted
from kavi.rational_paths import RationalLibrary
from kavi.trial_resources import memory_reading


def partitions(arity,seed):
    if arity not in (1,2,3): raise ValueError('Use one through three scalar inputs')
    rng=random.Random(seed)
    training_values=sorted({Fraction(n,d) for n in (-5,-3,-1,1,2,4,6) for d in (1,2,3)})
    final_values=sorted({Fraction(n,d) for n in (-19,-17,-13,11,17,23) for d in (5,7)})
    training_pool=list(product(training_values,repeat=arity))
    final_pool=list(product(final_values,repeat=arity))
    return rng.sample(training_pool,8),rng.sample(final_pool,min(24,len(final_pool)))


def run(run_dir,hinted=False):
    run_dir=run_dir.resolve()
    if not run_dir.is_relative_to(ROOT/'runs') or run_dir.exists(): raise ValueError('Use a new run directory')
    run_dir.mkdir(parents=True)
    started=time.monotonic()
    source=ProcedureLibrary.load(ROOT/'experiments/library-20260907-compiled.json')
    backend=ProcedureLibrary(p for n,p in source.procedures.items() if n in {'add','subtract','multiply'})
    lib=RationalLibrary(backend)
    limits=Limits(max_calls=10000,max_gates=400000,max_iterations=1024)
    tasks=[('reciprocal',1,lambda x:1/x[0]),('ratio',2,lambda x:x[0]/x[1]),
           ('signed_affine',3,lambda x:x[0]*x[1]+x[2]),
           ('secant_slope',3,lambda x:(x[0]-x[1])/x[2]),
           ('mean_pair',2,lambda x:(x[0]+x[1])/2)]
    if hinted: tasks=tasks[-2:]
    result={'schema':'kavi.rational-curriculum.v1','state':'running','seed':71,'lessons':[],
            'teacher_operation_hints':hinted,
            'initial_bytes':len(lib.encoded()),'backend_digest':backend.digest,
            'scope':'Engineered sign/fraction semantics; learned expression selection/composition; teacher uses Fraction independently.',
            'limits':{'max_seconds':120,'search_seconds':30 if hinted else 10,'candidates':20000,'candidate_cases':200000,'nodes':3,'execution':asdict(limits)}}
    progress=[]
    def status(message,state='running'):
        write_json(run_dir/'status.json',{'state':state,'phase':'Exact fractions and signs','message':message,
            'finished':len(progress),'total':len(tasks),'rows':progress})
    def check():
        if (run_dir/'STOP').exists() or time.monotonic()-started>120: raise InterruptedError('Stopped or total wall limit reached')
        while (run_dir/'PAUSE').exists():
            if (run_dir/'STOP').exists() or time.monotonic()-started>120: raise InterruptedError('Stopped while paused')
            time.sleep(.05)
    held=[]
    try:
        for name,arity,oracle in tasks:
            status('Learning '+name.replace('_',' ')+' from exact examples. Fresh tests are reserved.')
            train,final=partitions(arity,71+sum(map(ord,name)))
            if hinted:
                # A new final bank after adding teacher hints; not a re-score of old failures.
                values=[Fraction(n,d) for n in (-41,-37,-31,29,37,43) for d in (11,13)]
                final=random.Random(907+sum(map(ord,name))).sample(list(product(values,repeat=arity)),24)
                assert not set(train)&set(final)
            hints=('subtract','divide') if name=='secant_slope' else ('add','divide')
            check()
            assert not set(train)&set(final)
            search=ProgramSearch(lib,max_nodes=3,max_candidates=20000,max_candidate_cases=200000,
                max_seconds=30 if hinted else 10,max_cache_entries=20000,limits=limits,check=check,
                allowed_tags=('call',),allowed_names=hints if hinted else None)
            row={'name':name,'train':[[str(x) for x in xs] for xs in train],'body':None}
            try:
                body=search.learn(arity,[ProgramExample(xs,oracle(xs)) for xs in train])
                row.update(body=body,description=describe(body))
                lib.add(name,arity,body)
            except SearchExhausted as error: row['failure']=str(error)
            row['search']=asdict(search.stats)
            result['lessons'].append(row)
            held.append((final,oracle))
            progress.append({'trial':71,'arm':'exact rational','lesson':name.replace('_',' '),'status':'Provisional' if row['body'] else 'Not acquired'})
        # Freeze all acquired expressions before opening final values.
        result['library']=lib.to_dict()
        for index,(row,(final,oracle)) in enumerate(zip(result['lessons'],held)):
            if row['body'] is None: continue
            rows=[]
            for xs in final:
                check()
                expected=oracle(xs)
                try:
                    observed=lib.execute_expr(row['body'],xs,limits=limits,check=check)
                    rows.append({'inputs':[str(x) for x in xs],'expected':str(expected),'value':str(observed.value),
                        'correct':observed.value==expected,'gates':observed.gates,'calls':observed.calls,'iterations':observed.iterations})
                except ValueError as error: rows.append({'inputs':[str(x) for x in xs],'correct':False,'error':str(error)})
            row['final']={'correct':sum(x['correct'] for x in rows),'total':len(rows),'rows':rows}
            progress[index]['status']=f"{row['final']['correct']}/{len(rows)} fresh tests"
        result['final_bytes']=len(lib.encoded())
        (run_dir/'library.json').write_bytes(lib.encoded())
        result['state']='completed'
    except Exception as error:
        result.update(state='stopped' if isinstance(error,InterruptedError) else 'failed',error=str(error))
    result.update(seconds=time.monotonic()-started,memory=memory_reading())
    write_json(run_dir/'results.json',result)
    status('Exact arithmetic results saved. Supplied numeric semantics are separate from learned compositions.',result['state'])
    return 0 if result['state']=='completed' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['run','live'])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir,'scripts.run_rational_curriculum','Closing the signed-number and fraction gap')
        return 0
    return run(args.run_dir)


if __name__=='__main__': raise SystemExit(main())
