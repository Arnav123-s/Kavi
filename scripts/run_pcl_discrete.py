"""Visible original-textbook teaching of reusable logical connectives."""

import argparse
import hashlib
from pathlib import Path
import traceback

from kavi.composable_configurations import Work, encoded
from kavi.phase import PhaseConfiguration, CircuitTemplate, CircuitGeneration, reconstruct
from kavi.phase.evaluation import evaluate
from kavi.phase.logic import evaluate_formula
from scripts.configuration_run_support import Run
from scripts.pcl_discrete_source import DATA, URL, DIGEST, packet


def score(circuit, cases, work):
    correct = unresolved = 0
    for case in cases:
        answer = evaluate_formula(circuit, case['formula'], case['assignments'], work)
        correct += answer == case['answer']
        unresolved += answer is None
    return {'total': len(cases), 'correct': correct, 'unresolved': unresolved,
            'wrong': len(cases)-correct-unresolved}


def run(folder):
    paths = ['scripts/run_pcl_discrete.py', 'scripts/pcl_discrete_source.py',
             'scripts/configuration_run_support.py', 'kavi/phase/model.py', 'kavi/phase/runtime.py',
             'kavi/phase/layers.py', 'kavi/phase/learning.py', 'kavi/phase/selection.py',
             'kavi/phase/logic.py', 'kavi/phase/evaluation.py']
    session = Run(folder, 'docs/PCL_DISCRETE_PROTOCOL.md', paths)
    try:
        banks = packet()
        session.result.update(source={'author': 'Oscar Levin', 'url': URL, 'sha256': DIGEST,
                                     'bytes': (DATA/'logic.html').stat().st_size, 'license': 'CC BY-SA 4.0'},
                              packet_sha256=hashlib.sha256(encoded(banks)).hexdigest(),
                              counts={k:len(v) for k,v in banks.items()}, arms={})
        session.present('Discrete mathematics: start with logic',
            'Teach the meanings of AND, OR, NOT, IF-THEN and equivalence from the original textbook truth tables.',
            '8 initial cases; 18 total primitive cases; 32 untrained compound cases',
            boxes=['Original truth tables', 'Learn a circuit', 'Reuse learned operations', 'Check new formulas'])
        selected = {}
        for capacity in (0, 6):
            for seed in (7, 19, 41):
                name = f'couplings-{capacity}-seed-{seed}'
                base = PhaseConfiguration((3,5,7,11), tuple((event,i%4,1) for i,event in
                      enumerate(('true','false','and','or','implies','iff','not'))))
                model = CircuitGeneration(CircuitTemplate(base.moduli, max_couplings=capacity), base)
                arm = {'stages': []}
                session.result['arms'][name] = arm
                for stage_name in ('first','training'):
                    work = Work(check=session.check, limit=10_000_000)
                    stage = {'bank': stage_name}
                    protected = [] if stage_name == 'first' else banks['first']
                    session.present('Constructing complete successor circuits',
                        'No built-in Boolean answer rule is installed. Candidates must match the textbook teaching cells.',
                        f'{name}: {len(banks[stage_name])} cases; 256 proposals', delay=.4)
                    try:
                        model, stage['selection'] = reconstruct(model, banks[stage_name], protected,
                                               work, candidates=256, seed=seed, readout='exact')
                    except InterruptedError as error:
                        if str(error) != 'Configuration work budget exhausted': raise
                        stage['failure'] = str(error)
                    stage['learning_work'] = dict(work.counts)
                    checks = Work(check=session.check)
                    stage['teaching'] = evaluate(model, banks[stage_name], checks)
                    stage['protected'] = evaluate(model, protected, checks)
                    stage['development'] = score(model.circuit, banks['development'], checks)
                    stage.update(check_work=dict(checks.counts), bytes=len(encoded(model.record())),
                                 couplings=len(model.circuit.couplings))
                    arm['stages'].append(stage)
                    session.present('Checking learned operations',
                        'Correct primitive operations can be reused, but formula decomposition is supplied software.',
                        f'{name}: {stage["teaching"]["correct"]}/{len(banks[stage_name])} teaching; '
                        f'{stage["development"]["correct"]}/4 compound development',delay=.4)
                selected[name] = model
        session.present('All learning finished; testing new formulas',
            'Final textbook examples have not entered teaching or candidate selection.',active=3)
        for name,model in selected.items():
            arm = session.result['arms'][name]
            work = Work(check=session.check)
            before = hashlib.sha256(encoded(model.record())).hexdigest()
            arm['final'] = score(model.circuit, banks['final'], work)
            arm['primitive_complete_domain'] = evaluate(model, banks['training'], work)
            raw = encoded(model.record())
            assert hashlib.sha256(raw).hexdigest() == before
            arm['frozen_unchanged'] = True
            arm['final_work'] = dict(work.counts)
            arm['artifact'] = {'file': name+'.json', 'bytes': len(raw), 'sha256': before}
            (session.folder/(name+'.json')).write_bytes(raw)
            session.present('Compound formula result',
                'This measures learned truth functions with supplied composition, not unrestricted mathematical understanding.',
                f'{name}: {arm["final"]["correct"]}/32 correct; {arm["final"]["unresolved"]} unresolved',
                active=3,delay=.5)
        work = Work(check=session.check)
        session.result['controls'] = {'constant_true_correct': sum(c['answer']==1 for c in banks['final']),
                                     'total': len(banks['final']),
                                     'untrained': score(PhaseConfiguration((3,5,7,11)),banks['final'],work),
                                     'work': dict(work.counts)}
        session.finish(message='The discrete-logic course is complete. Teaching has stopped; every result is saved.')
    except Exception as error:
        session.result['error'] = str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
