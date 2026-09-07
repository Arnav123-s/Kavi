"""Measure route reuse and prediction-before-correction on a finite stream."""

import argparse
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kavi.circuit_runtime import write_json
from kavi.experience_router import ExperienceRouter, probe_inputs, signature
from kavi.procedure_core import ProcedureLibrary
from kavi.procedure_search import ProgramExample
from kavi.route_memory import RouteMemory
from kavi.trial_resources import memory_reading
from scripts.run_experience_routing import TASKS


def run(run_dir):
    run_dir = run_dir.resolve()
    if not run_dir.is_relative_to(ROOT/'runs') or run_dir.exists():
        raise ValueError('Use a fresh directory under runs')
    run_dir.mkdir(parents=True)
    started = time.monotonic()
    result = {'schema':'kavi.route-memory-trial.v1','state':'running','episodes':[],
              'protocol':'Two teaching/reuse passes; separate prediction-before-correction stream. Four seconds per acquisition, 300 seconds total, sampled 512 MiB guard.'}
    progress = []
    last_memory = 0

    def check():
        nonlocal last_memory
        if (run_dir/'STOP').exists() or time.monotonic()-started>300:
            raise InterruptedError('Stopped or total time exhausted')
        while (run_dir/'PAUSE').exists():
            if (run_dir/'STOP').exists() or time.monotonic()-started>300:
                raise InterruptedError('Stopped while paused')
            time.sleep(.05)
        if time.monotonic()-last_memory>.3:
            last_memory=time.monotonic()
            if (memory_reading().get('working_set_bytes') or 0)>512*1024**2:
                raise InterruptedError('Memory guard reached')

    def emit(message):
        write_json(run_dir/'status.json',{'state':result['state'],'phase':'Route reuse and correction',
                   'message':message,'finished':len(progress),'total':23,'rows':progress})

    try:
        prior = json.loads((ROOT/'runs/experience-routing-20260907-01/results.json').read_text(encoding='utf-8'))
        lib = ProcedureLibrary.from_dict(prior['base'])
        router = ExperienceRouter(prior['router']['tree'])
        memory = RouteMemory(lib,router)
        for phase in (1,2):
            for index,(name,arity,oracle) in enumerate(TASKS):
                check()
                emit(f'Pass {phase}: {name.replace("_"," ")}. Try an existing route first; search only if none fits.')
                points = probe_inputs(arity)
                # Same probe context, different extra teaching inputs on each pass.
                points += [tuple(6+phase+i+j for j in range(arity)) for i in range(2)]
                observations = {xs:oracle(xs) for xs in points}
                features = signature(arity,observations)
                learned = memory.acquire(features,arity,[ProgramExample(xs,y) for xs,y in observations.items()],check=check)
                row = {'pass':phase,'task':name,'acquisition':learned,'predictions':[]}
                for value in (40+phase*10,43+phase*10,47+phase*10):
                    check()
                    xs = tuple(value+j for j in range(arity))
                    observed = None if learned['body'] is None else lib.execute_expr(learned['body'],xs,check=check).value
                    # These answers are measured but not fed back in the reuse comparison.
                    row['predictions'].append({'inputs':xs,'value':observed,'target':oracle(xs),
                                               'correct':observed==oracle(xs)})
                result['episodes'].append(row)
                progress.append({'trial':phase,'arm':'route memory','lesson':name.replace('_',' '),
                                 'status':'Reused without search' if learned['reused'] else 'Learned a route' if learned['body'] else 'Not acquired'})
                write_json(run_dir/'checkpoint.json',result)
        result.update(route_memory=json.loads(memory.encoded()),route_bytes=len(memory.encoded()),
                      router_bytes=len(router.encoded()),base_bytes=len(lib.encoded()))
        # A separate ambiguous lesson: square and cube agree at zero and one.
        # Explicit context is held constant; no unsupported intent inference is claimed.
        correction = RouteMemory(lib,router)
        context = (1,-1,-1,2,0,0)
        teaching = [ProgramExample((0,),0),ProgramExample((1,),1)]
        initial = correction.acquire(context,1,teaching,check=check)
        body = initial['body']
        stream = []
        for value in (2,3,4):
            check()
            emit(f'Correction stream: answer for input {value} is recorded before the teacher reveals the result.')
            prediction = None if body is None else lib.execute_expr(body,(value,),check=check).value
            expected = value**3
            event = {'input':value,'prediction_before_feedback':prediction,'target_revealed_after_prediction':expected,
                     'correct_before_feedback':prediction==expected}
            if prediction != expected:
                teaching.append(ProgramExample((value,),expected))
                repair = correction.acquire(context,1,teaching,check=check)
                body = repair['body']
                event['repair'] = repair
            stream.append(event)
            progress.append({'trial':'stream','arm':'answer then learn','lesson':f'Cube input {value}',
                             'status':'Correct before feedback' if prediction==expected else 'Wrong answer recorded; correction supplied'})
        result['correction'] = {'initial_acquisition':initial,'events':stream,
                                'memory':json.loads(correction.encoded()),'bytes':len(correction.encoded())}
        result['state']='completed'
    except Exception as error:
        result.update(state='stopped' if isinstance(error,InterruptedError) else 'failed',error=str(error))
    result.update(seconds=time.monotonic()-started,memory=memory_reading())
    write_json(run_dir/'results.json',result)
    emit('Completed evidence saved. The original wrong prediction remains in the score.')
    return 0 if result['state']=='completed' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['run','live'])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir,'scripts.run_route_memory','Reuse a pathway and learn from corrections')
        return 0
    return run(args.run_dir)


if __name__=='__main__': raise SystemExit(main())
