"""Live bounded comparison of local completion, correction and equation reuse."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import time
import traceback

from kavi.composable_configurations import (Configuration, Work, StaleConfiguration,
    agrees, differentiate, encoded, fit)
from kavi.equation_kernels import make_registry
from kavi.procedure_core import ProcedureLibrary
from scripts.configuration_run_support import ROOT, Run, safe


def physics_inputs(kind, count, seed):
    rng = random.Random(seed)
    rows = []
    for _ in range(count):
        t = rng.uniform(.001, 2.8)
        if kind == 'heat':
            state = tuple(rng.uniform(-100, 500) for _ in range(3))
        else:
            theta, phase = rng.uniform(0, math.pi/2), rng.uniform(-math.pi, math.pi)
            state = (complex(math.cos(theta)), math.sin(theta)*complex(math.cos(phase), math.sin(phase)))
        rows.append((state, t))
    return rows


def deviation(a, b):
    return max((abs(x-y) for x, y in zip(a, b)), default=0) if isinstance(a, tuple) else abs(a-b)


def run(folder):
    session = Run(folder, 'docs/CONFIGURATION_LAB_PROTOCOL.md', [
        'kavi/composable_configurations.py', 'kavi/equation_kernels.py',
        'scripts/run_configuration_lab.py', 'scripts/configuration_run_support.py',
        'scripts/configuration_lab_window.py'])
    work = lambda: Work(check=session.check)
    r = make_registry(ProcedureLibrary.load(ROOT/'experiments/library-20260907-compiled.json'))
    base_bytes = (ROOT/'experiments/library-20260907-compiled.json').stat().st_size
    result = session.result
    result['base_library_bytes'] = base_bytes
    evidence = {}
    try:
        session.present('Find the unknown part', 'The first addition already works. Kavi will learn the missing middle from final answers.',
            boxes=['Add first two inputs', 'Unknown middle', 'Add last input', 'Check answer'], active=1)
        r.install('outer', Configuration(4, (('add', (0, 1)), ('middle', (4, 2)), ('add', (5, 3))), 6))
        inputs = [(1, 1, 3, 2), (1, 2, 4, 1), (0, 2, 1, 3), (2, 3, 1, 4)]
        lessons = [(args, sum(args[:3])**2+args[3]) for args in inputs]
        arms = []
        for local in (False, True):
            w = work()
            started = time.process_time()
            graph = fit(r, 'middle', lessons, ('add', 'subtract', 'multiply'), w, outer='outer', local=local)
            assert graph is not None
            arms.append({'method': 'local' if local else 'whole', 'work': w.counts,
                         'cpu_seconds': time.process_time()-started, 'graph': graph.record()})
            session.present('Compare discovery work', 'Both methods search the same possibilities. Local learning reuses the known beginning.',
                f"{arms[-1]['method']}: {w.counts['candidate_proposals']} candidates; {w.counts['kernel_calls']} component calls")
        assert arms[0]['graph'] == arms[1]['graph']
        candidate = r.copy()
        candidate.install('middle', graph)
        banks = {}
        for label, seed, count, low, high in [('promotion',95001,48,9,40), ('final',95002,128,41,300)]:
            rng = random.Random(seed)
            examples = [tuple(rng.randint(low, high) for _ in range(4)) for _ in range(count)]
            w = work()
            correct = sum(candidate.execute('outer', args, w) == sum(args[:3])**2+args[3] for args in examples)
            banks[label] = {'correct': correct, 'total': count, 'work': w.counts}
            evidence[label+'_arithmetic'] = examples
            assert correct == count
        r = candidate
        ew = work()
        expansion = r.expand('outer', ew)
        direct = work()
        assert expansion.execute((17, 19, 23, 5), r, direct) == 3486
        result['local_completion'] = {'arms': arms, 'banks': banks, 'expansion_work': ew.counts,
                                     'expanded_query_work': direct.counts}
        session.present('Retain the new pathway', 'The learned middle is now a component inside the larger pathway. New inputs execute it without candidate search.',
            '128 / 128 new arithmetic questions passed', boxes=['Add', 'Learned squared sum', 'Add', 'Answer'], active=1)

        session.present('Correct a provisional rule', 'One example fits both addition and multiplication. A new example will distinguish them.',
            boxes=['Ambiguous lesson', 'Provisional route', 'Correction', 'Updated route'], active=2)
        c = r.copy()
        w0 = work()
        initial = fit(c, 'rule', [((2,2),4)], ('add','subtract','multiply'), w0)
        c.install('rule', initial)
        c.install('wrapper', Configuration(2, (('rule',(0,1)),), 2))
        old_work = work()
        stale = c.expand('wrapper', old_work)
        before = c.execute('rule', (2,3), old_work)
        cw = work()
        repaired = fit(c, 'rule', [((2,2),4),((2,3),6),((3,4),12),((1,5),5)],
                       ('add','subtract','multiply'), cw)
        c.install('rule', repaired)
        guard_work = work()
        try:
            stale.execute((11,13), c, guard_work)
            rejected = False
        except StaleConfiguration:
            rejected = True
        assert rejected
        rebuilt_work = work()
        rebuilt = c.expand('wrapper', rebuilt_work)
        rng = random.Random(95003)
        correction_inputs = [tuple(rng.randint(11,300) for _ in range(2)) for _ in range(128)]
        ew, uw = work(), work()
        corrected = sum(rebuilt.execute(args,c,ew) == args[0]*args[1] for args in correction_inputs)
        unsafe = sum(stale.execute(args,c,uw,verify=False) == args[0]*args[1] for args in correction_inputs)
        result['correction'] = {'initial_consistent_candidates': w0.counts['consistent_candidates'],
            'initial_graph': initial.record(), 'before_correction_at_2_3': before,
            'initial_work': w0.counts, 'old_expansion_work': old_work.counts,
            'repair_work': cw.counts, 'repaired_graph': repaired.record(),
            'stale_rejected': rejected, 'guard_work': guard_work.counts,
            'rebuild_work': rebuilt_work.counts, 'corrected': corrected, 'unsafe': unsafe,
            'total':128, 'corrected_work':ew.counts,'unsafe_work':uw.counts}
        r = c
        evidence['correction_inputs'] = correction_inputs
        session.present('Prevent an old mistake returning', 'The old shortcut notices its rule changed. Rebuilding it gives the corrected answer on new inputs.',
            f'Corrected: {corrected}/128. Deliberately skipping the guard: {unsafe}/128.')

        dw = work()
        derivative = differentiate(r, 'middle', 0, dw)
        r.install('derivative', derivative)
        rng = random.Random(95004)
        derivative_inputs = [tuple(rng.randint(31,300) for _ in range(2)) for _ in range(128)]
        ev = work()
        correct = sum(r.execute('derivative', args, ev) == 2*sum(args) for args in derivative_inputs)
        result['calculus'] = {'correct':correct,'total':128,'transformation_work':dw.counts,
                              'evaluation_work':ev.counts,'graph':derivative.record(), 'transformer':'supplied'}
        session.present('A configuration produces another', 'A supplied calculus transformer turns the learned squared-sum pathway into its derivative. The result runs as a normal component.',
            f'{correct}/128 new derivative inputs passed', boxes=['Learned function','Differentiate','New configuration','Run it'],active=2)

        result['physics'] = {}
        for kind, pseed, fseed in [('heat',95005,95006),('schrodinger',95007,95008)]:
            session.present('Learn a shorter '+kind+' configuration', 'The teacher shows the result of two evolution steps. Kavi searches for a cheaper arrangement using the supplied equation and addition.',
                boxes=['Initial state','Evolve once','Evolve again','Final state'], active=2)
            states = [(1.,4.,7.),(0.,3.,9.),(7.,2.,5.),(-3.,4.,12.)] if kind == 'heat' else [
                (1+0j,0j),(0j,1+0j),(2**-.5,1j*2**-.5),(math.sqrt(.75),-.5j)]
            training_inputs = list(zip(states, (.1,.2,.35,.7)))
            r.install('two_'+kind, Configuration(2, ((kind,(0,1)),(kind,(2,1))),3))
            teaching_work = work()
            lessons = [(args,r.execute('two_'+kind,args,teaching_work)) for args in training_inputs]
            lw = work()
            graph = fit(r,'short_'+kind,lessons,(kind,'real_add'),lw)
            assert graph is not None
            r.install('short_'+kind,graph)
            banks = {}
            for label, seed, count in [('promotion',pseed,48),('final',fseed,128)]:
                cases = physics_inputs(kind,count,seed)
                bw, sw = work(), work()
                before_time = time.perf_counter()
                baseline = [r.execute('two_'+kind,args,bw) for args in cases]
                baseline_seconds = time.perf_counter()-before_time
                before_time = time.perf_counter()
                selected = [r.execute('short_'+kind,args,sw) for args in cases]
                selected_seconds = time.perf_counter()-before_time
                invariant_error = max(abs(sum(out)-sum(args[0])) if kind=='heat' else
                    abs(sum(abs(v)**2 for v in out)-1) for args,out in zip(cases,selected))
                range_violations = sum(not min(args[0])-1e-9 <= v <= max(args[0])+1e-9
                    for args,out in zip(cases,selected) for v in out) if kind=='heat' else None
                banks[label] = {'correct':sum(agrees(a,b) for a,b in zip(baseline,selected)),
                    'total':count,'max_difference':max(deviation(a,b) for a,b in zip(baseline,selected)),
                    'invariant_error':invariant_error,'range_violations':range_violations,
                    'baseline_work':bw.counts,'selected_work':sw.counts,
                    'baseline_seconds':baseline_seconds,'selected_seconds':selected_seconds}
                evidence[kind+'_'+label] = cases
                assert banks[label]['correct'] == count
            result['physics'][kind] = {'graph':graph.record(),'teacher_work':teaching_work.counts,
                'learning_work':lw.counts,'banks':banks}
            session.present('Check the shorter '+kind+' pathway', 'The new configuration combines the time intervals and calls the equation once. Its result agrees with the two-step path on new inputs.',
                f"128/128 passed; evolution calls {banks['final']['baseline_work']['kernel_'+kind]} → {banks['final']['selected_work']['kernel_'+kind]}",
                boxes=['Initial state','Combine intervals','Evolve once','Checked result'],active=2)

        phase_work = work()
        a = 2**-.5
        populations = [abs(r.execute('schrodinger',((a,sign*1j*a),math.pi/4),phase_work)[1])**2 for sign in (1,-1)]
        result['interference'] = {'observed_populations':populations,'phase_discarded_prediction':[.5,.5],
                                  'work':phase_work.counts}
        session.present('Does phase matter?', 'Two inputs have the same starting probabilities but different phases. The equation sends them to different outputs.',
            f'With phase: {populations[0]:.4f} and {populations[1]:.4f}. Without phase: 0.5 and 0.5.')
        rw = work()
        retained = sum(r.execute(op,(a,b),rw) == (a+b if op=='add' else a*b)
            for op in ('add','multiply') for a in range(16) for b in range(16))
        result['retention'] = {'correct':retained,'total':512,'work':rw.counts}
        assert retained == 512
        raw = encoded(r.record())
        (session.folder/'configurations.json').write_bytes(raw)
        (session.folder/'evidence.json').write_text(json.dumps(safe(evidence),ensure_ascii=False,indent=2),encoding='utf-8')
        result['artifact'] = {'file':'configurations.json','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        session.present('Earlier skills retained', 'All tested earlier additions and multiplications still work. This run learned arrangements of supplied components; it did not learn to read scientific prose.',
            '512/512 earlier arithmetic checks passed')
        session.finish()
    except Exception as error:
        result['error'] = str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
