"""Compare learned component routing with flat and mismatched controls."""

import argparse
from dataclasses import asdict
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kavi.circuit_runtime import write_json
from kavi.experience_router import ExperienceRouter, called_components, probe_inputs, signature
from kavi.foundation_curriculum import LESSONS, target
from kavi.procedure_core import ProcedureLibrary, Limits, describe
from kavi.procedure_search import ProgramExample, ProgramSearch, SearchExhausted
from kavi.trial_resources import memory_reading


TASKS = [
    ('cube_plus_one', 1, lambda x: x[0]**3+1),
    ('square_plus_one', 1, lambda x: x[0]**2+1),
    ('shifted_sum_square', 2, lambda x: (x[0]+x[1]+1)**2),
    ('square_with_offset', 2, lambda x: x[0]**2+x[1]),
    ('product_plus_one', 2, lambda x: x[0]*x[1]+1),
    ('permuted_scaled_square', 2, lambda x: x[0]**2*x[1]),
    ('shifted_fourth', 1, lambda x: (x[0]+1)**4),
    ('sum_fourths', 2, lambda x: x[0]**4+x[1]**4),
    ('affine_plus_one', 3, lambda x: x[0]*x[1]+x[2]+1),
    ('combined_fourth_plus_one', 2, lambda x: (x[0]+x[1])**4+1),
]


def run(run_dir):
    run_dir = run_dir.resolve()
    if not run_dir.is_relative_to(ROOT/'runs') or run_dir.exists():
        raise ValueError('Use a fresh directory under runs')
    run_dir.mkdir(parents=True)
    started = time.monotonic()
    rows = []
    progress = []
    result = {'schema': 'kavi.experience-routing-trial.v1', 'state': 'running', 'rows': rows,
              'limits': {'wall_seconds': 300, 'working_set_mib': 512, 'task_seconds': 2,
                         'candidates': 4000, 'candidate_cases': 80000, 'max_nodes': 3},
              'source_hashes': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                               for name in ('kavi/experience_router.py', 'kavi/procedure_search.py',
                                            'scripts/run_experience_routing.py')}}
    last_memory = 0

    def check():
        nonlocal last_memory
        if (run_dir/'STOP').exists() or time.monotonic()-started > 300:
            raise InterruptedError('Stopped or five-minute budget exhausted')
        while (run_dir/'PAUSE').exists():
            if (run_dir/'STOP').exists() or time.monotonic()-started > 300:
                raise InterruptedError('Stopped while paused')
            time.sleep(.05)
        if time.monotonic()-last_memory > .3:
            last_memory = time.monotonic()
            if (memory_reading().get('working_set_bytes') or 0) > 512*1024**2:
                raise InterruptedError('Working-set guard reached')

    def emit(message, phase='Learning which components to try'):
        write_json(run_dir/'status.json', {'state': result['state'], 'phase': phase,
                   'message': message, 'finished': len(progress), 'total': 60, 'rows': progress})
        with (run_dir/'events.txt').open('a', encoding='utf-8') as stream:
            stream.write(message+'\n')

    limits = Limits(max_calls=5000, max_gates=200000, max_iterations=256)
    try:
        emit('Using past successful programs to learn a small routing tree. No new task hints are supplied.')
        previous_path = ROOT/'experiments/2026-09-07-composition-hints.json'
        previous = json.loads(previous_path.read_text(encoding='utf-8'))
        lib = ProcedureLibrary.from_dict(previous['base'])
        history = next(arm for arm in previous['arms'] if arm['seed']==17 and arm['arm']=='fixed')
        examples, evidence = [], []
        for lesson, old in zip(LESSONS, history['lessons']):
            check()
            observations = {xs: target(lesson.name, xs) for xs in probe_inputs(lesson.arity)}
            features = signature(lesson.arity, observations)
            components = called_components(old['body'])
            examples.append((features, components))
            evidence.append({'historical_task': lesson.name, 'features': features,
                             'components_from_acquired_body': components, 'body': old['body'],
                             'probes': [{'inputs': xs, 'target': y} for xs,y in observations.items()]})
        router = ExperienceRouter.fit(examples)
        # Cyclically mismatched experience has the same feature rows and label inventory.
        shuffled = ExperienceRouter.fit([(features, examples[(i+1)%len(examples)][1])
                                         for i,(features,_) in enumerate(examples)])
        result.update(history_sha256=hashlib.sha256(previous_path.read_bytes()).hexdigest(),
                      history=evidence, base=lib.to_dict(), base_digest=lib.digest,
                      base_bytes=len(lib.encoded()), router=json.loads(router.encoded()),
                      router_bytes=len(router.encoded()), mismatched_router=json.loads(shuffled.encoded()),
                      mismatched_router_bytes=len(shuffled.encoded()),
                      preparation_seconds=time.monotonic()-started)
        (run_dir/'router.json').write_bytes(router.encoded())
        for seed in (101,203):
            for index,(name,arity,oracle) in enumerate(TASKS):
                check()
                rng = random.Random(seed+index)
                points = sorted(set(probe_inputs(arity)) |
                                set(rng.sample(list(product(range(6),repeat=arity)), min(8,6**arity))))
                observations = {xs: oracle(xs) for xs in points}
                teaching = [ProgramExample(xs,y) for xs,y in observations.items()]
                # Rotate order to reduce a constant first-arm timing advantage.
                modes = ['flat','learned','mismatched']
                modes = modes[index%3:]+modes[:index%3]
                for mode in modes:
                    check()
                    emit(f'{name.replace("_"," ")}: {mode} routing, trial {seed}. Checking candidate configurations.')
                    task_start = time.monotonic()
                    features = signature(arity, observations)
                    chosen = None if mode=='flat' else (router if mode=='learned' else shuffled).select(features)
                    row = {'task':name, 'seed':seed, 'mode':mode, 'features':features,
                           'selected':chosen, 'teaching':[{'inputs':e.inputs,'target':e.target} for e in teaching],
                           'attempts':[], 'body':None}
                    used_candidates = used_cases = 0
                    for phase in (['broad'] if mode=='flat' else ['focused','broad']):
                        remaining = 2-(time.monotonic()-task_start)
                        if remaining <= 0 or used_candidates>=4000 or used_cases>=80000:
                            break
                        search = ProgramSearch(lib, max_nodes=3,
                            max_candidates=min(1000,4000-used_candidates) if phase=='focused' else 4000-used_candidates,
                            max_candidate_cases=min(20000,80000-used_cases) if phase=='focused' else 80000-used_cases,
                            max_seconds=min(.5,remaining) if phase=='focused' else remaining,
                            max_cache_entries=12000, limits=limits, check=check,
                            allowed_tags=('call',), allowed_names=chosen if phase=='focused' else None)
                        attempt = {'phase':phase}
                        try:
                            row['body'] = search.learn(arity, teaching)
                            row['description'] = describe(row['body'])
                        except SearchExhausted as error:
                            attempt['failure'] = str(error)
                        attempt['stats'] = asdict(search.stats)
                        row['attempts'].append(attempt)
                        used_candidates += search.stats.candidates
                        used_cases += search.stats.candidate_cases
                        if row['body'] is not None:
                            break
                    row.update(seconds=time.monotonic()-task_start, candidates=used_candidates,
                               candidate_cases=used_cases)
                    rows.append(row)
                    progress.append({'trial':seed,'arm':mode,'lesson':name.replace('_',' '),
                                     'status':'Configuration found' if row['body'] else 'Search limit reached'})
                    write_json(run_dir/'checkpoint.json',result)
        # Freeze both selectors and every candidate before accessing final inputs.
        for row in rows:
            check()
            emit('Testing fresh numbers. Final answers do not update the routing trees.', 'Independent evaluation')
            index = next(i for i,t in enumerate(TASKS) if t[0]==row['task'])
            _,arity,oracle = TASKS[index]
            held = random.Random(row['seed']+index+9000).sample(
                list(product(range(30,37),repeat=arity)), min(12,7**arity))
            answers = []
            for xs in held:
                check()
                answer = {'inputs':xs,'expected':oracle(xs),'correct':False}
                if row['body'] is not None:
                    try:
                        observed = lib.execute_expr(row['body'],xs,limits=limits,check=check)
                        answer.update(value=observed.value, correct=observed.value==oracle(xs))
                    except ValueError as error:
                        answer['error'] = str(error)
                answers.append(answer)
            row['final'] = {'correct':sum(x['correct'] for x in answers),'total':len(answers),'rows':answers}
            next(p for p in progress if p['trial']==row['seed'] and p['arm']==row['mode']
                 and p['lesson']==row['task'].replace('_',' '))['status'] = f"{row['final']['correct']}/{len(answers)} fresh answers"
        # No executable procedures were replaced. Recheck base outputs independently.
        retained = []
        for name,proc in lib.procedures.items():
            inputs = [(a,b) for a in range(10) for b in range(10)] if proc.arity==2 else [(a,) for a in range(6,24)]
            for xs in inputs:
                expected = xs[0]+xs[1] if name=='add' else xs[0]*xs[1] if name=='multiply' else xs[0]**{'square':2,'fourth':4,'eighth':8}[name]
                retained.append(lib.execute(name,xs,limits=limits,check=check).value==expected)
        result.update(retention={'correct':sum(retained),'total':len(retained)},
                      base_unchanged=lib.digest==result['base_digest'], state='completed')
    except Exception as error:
        result.update(state='stopped' if isinstance(error,InterruptedError) else 'failed',error=str(error))
    result.update(seconds=time.monotonic()-started,memory=memory_reading())
    write_json(run_dir/'results.json',result)
    emit('Results saved, including failures. The routing policy was frozen for fresh tests.', 'Finished')
    return 0 if result['state']=='completed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['run','live'])
    parser.add_argument('--run-dir', required=True, type=Path)
    args = parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir, 'scripts.run_experience_routing', 'Learning which pathways to try')
        return 0
    return run(args.run_dir)


if __name__=='__main__': raise SystemExit(main())
