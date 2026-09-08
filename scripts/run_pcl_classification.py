"""Visible, source-based comparison of exact and interval phase readouts."""

import argparse
from collections import Counter, defaultdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import traceback

from kavi.composable_configurations import Work, encoded
from kavi.phase import PhaseConfiguration, CircuitTemplate, CircuitGeneration, reconstruct
from kavi.phase.evaluation import evaluate
from scripts.configuration_run_support import ROOT, Run

DATA = ROOT/'private/iris-source-20260908'
CLASSES = ('Iris-setosa', 'Iris-versicolor', 'Iris-virginica')


def load_source():
    rows = []
    for number, line in enumerate((DATA/'bezdekIris.data').read_text().splitlines(), 1):
        if not line.strip():
            continue
        fields = line.split(',')
        if len(fields) != 5 or fields[4] not in CLASSES:
            raise ValueError('Invalid original source row')
        exact = tuple(Decimal(value)*10 for value in fields[:4])
        if any(value != int(value) or not 0 < value < 256 for value in exact):
            raise ValueError('Source precision or range violates the declared codec')
        values = tuple(map(int, exact))
        events = tuple(f'field:{i}' for i, value in enumerate(values) for _ in range(value))
        rows.append({'id': number, 'values': values, 'signature': ','.join(fields[:4]),
                     'events': events, 'label': CLASSES.index(fields[4])})
    if len(rows) != 150:
        raise ValueError('Unexpected source edition size')
    return rows


def partition(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['values']].append(row)
    if any(len({row['label'] for row in group}) != 1 for group in groups.values()):
        raise ValueError('Conflicting duplicate measurements')
    banks = {name: [] for name in ('first', 'training', 'development', 'final')}
    for label in range(3):
        species = [g for g in groups.values() if g[0]['label'] == label]
        species.sort(key=lambda g: hashlib.sha256(g[0]['signature'].encode()).hexdigest())
        a, b = len(species)*3//5, len(species)*4//5
        for name, selected in [('first', species[:a//2]), ('training', species[:a]),
                               ('development', species[a:b]), ('final', species[b:])]:
            banks[name].extend(row for group in selected for row in group)
    return banks, len(groups)


def pairs(rows):
    return [(row['events'], row['label']) for row in rows]


def majority(rows):
    counts = Counter(row['label'] for row in rows)
    return min(counts, key=lambda label: (-counts[label], label))


def fit_stump(rows, work):
    best = None
    for feature in range(4):
        values = sorted({row['values'][feature] for row in rows})
        for lo, hi in zip(values, values[1:]):
            work.add('stump_threshold_candidates')
            work.add('stump_row_comparisons', 3*len(rows))
            threshold_twice = lo+hi
            left = [r for r in rows if 2*r['values'][feature] <= threshold_twice]
            right = [r for r in rows if 2*r['values'][feature] > threshold_twice]
            a, b = majority(left), majority(right)
            errors = sum(r['label'] != (a if 2*r['values'][feature] <= threshold_twice else b) for r in rows)
            candidate = errors, feature, threshold_twice, a, b
            if best is None or candidate < best:
                best = candidate
    return best


def run(folder):
    source_names = ['kavi/phase/model.py', 'kavi/phase/runtime.py', 'kavi/phase/layers.py',
                    'kavi/phase/learning.py', 'kavi/phase/regions.py', 'kavi/phase/selection.py',
                    'kavi/phase/evaluation.py', 'scripts/run_pcl_classification.py',
                    'scripts/acquire_iris_source.py', 'scripts/configuration_run_support.py']
    session = Run(folder, 'docs/PCL_CLASSIFICATION_PROTOCOL.md', source_names)
    try:
        manifest = json.loads((DATA/'manifest.json').read_text())
        for item in manifest['files']:
            raw = (DATA/item['name']).read_bytes()
            if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['sha256']:
                raise ValueError('Local source fingerprint mismatch')
        rows = load_source()
        banks, groups = partition(rows)
        session.result.update(source=manifest, records=len(rows), unique_measurements=groups,
                              partitions={key: [r['id'] for r in value] for key, value in banks.items()}, arms={})
        session.present('Original measurements; separate questions',
                        'These are measured flower dimensions, not generated examples. Identical measurements stay in the same partition.',
                        '; '.join(f'{key}: {len(value)}' for key, value in banks.items()),
                        boxes=['Original measurements', 'Stable phase template', 'Rebuilt circuit', 'Unseen specimens'], active=0)
        base = CircuitGeneration(CircuitTemplate((256,)*4, max_couplings=2),
                                 PhaseConfiguration((256,)*4, tuple((f'field:{i}', i, 1) for i in range(4))))
        selected = {}
        for readout in ('exact', 'regions'):
            for seed in (7, 19, 41):
                name = f'{readout}-{seed}'
                model = base
                arm = {'readout': readout, 'seed': seed, 'stages': []}
                session.result['arms'][name] = arm
                for stage_name in ('first', 'training'):
                    stage = {'bank': stage_name}
                    teaching = pairs(banks[stage_name])
                    protected = [] if stage_name == 'first' else pairs(banks['first'])
                    work = Work(check=session.check, limit=30_000_000)
                    session.present('Constructing a complete successor',
                                    'The template stays fixed. Candidates combine old and new relationships; the teacher checks the resulting answers.',
                                    f'{name}: {len(teaching)} source lessons', active=2, delay=.3)
                    try:
                        successor, stats = reconstruct(model, teaching, protected, work,
                                                        candidates=12, seed=seed, readout=readout)
                        stage['selection'] = stats
                        model = successor
                    except InterruptedError as error:
                        if str(error) != 'Configuration work budget exhausted':
                            raise
                        stage['failure'] = str(error)
                    stage['learning_work'] = dict(work.counts)
                    score_work = Work(check=session.check)
                    stage['teaching'] = evaluate(model, teaching, score_work)
                    stage['development'] = evaluate(model, pairs(banks['development']), score_work)
                    stage['protected'] = evaluate(model, protected, score_work)
                    stage['evaluation_work'] = dict(score_work.counts)
                    stage['bytes'] = len(encoded(model.record()))
                    stage['output_rules'] = len(model.circuit.outputs)
                    stage['couplings'] = len(model.circuit.couplings)
                    stage['original_dynamics_unchanged'] = (model.circuit.impulses == base.circuit.impulses
                                                           and model.circuit.couplings == base.circuit.couplings)
                    arm['stages'].append(stage)
                    session.present('Teaching checked; new specimens next',
                                    'Correct teaching answers do not prove generalization. Development scores are recorded without selecting another model.',
                                    f'{name}: teaching {stage["teaching"]["correct"]}/{len(teaching)}; development {stage["development"]["correct"]}/{len(banks["development"])}',
                                    active=2, delay=.5)
                selected[name] = model
        # Fit the conventional controls before exposing any final scores.
        control_work = Work(check=session.check)
        constant, stump = majority(banks['training']), fit_stump(banks['training'], control_work)
        session.result['control_work'] = dict(control_work.counts)
        session.present('All circuits frozen',
                        'Learning is finished. The final specimens cannot change a circuit or select a candidate.',
                        f'{len(banks["final"])} held-out original specimens', active=3)
        for name, model in selected.items():
            work = Work(check=session.check)
            arm = session.result['arms'][name]
            arm['final'] = evaluate(model, pairs(banks['final']), work)
            arm['final_work'] = dict(work.counts)
            raw = encoded(model.record())
            (session.folder/(name+'.json')).write_bytes(raw)
            arm['artifact'] = {'file': name+'.json', 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
            session.present('Final result measured',
                            'This tests a small classification problem. It does not establish language understanding or an internal world.',
                            f'{name}: {arm["final"]["correct"]}/{arm["final"]["total"]} correct; {arm["final"]["unresolved"]} unresolved',
                            active=3, delay=.5)
        _, feature, threshold, left, right = stump
        session.result['controls'] = {
            'majority': {'class': constant, 'correct': sum(r['label'] == constant for r in banks['final'])},
            'stump': {'feature': feature, 'threshold_twice_tenths': threshold, 'left': left, 'right': right,
                      'correct': sum(r['label'] == (left if 2*r['values'][feature] <= threshold else right) for r in banks['final'])},
            'final_total': len(banks['final'])}
        session.finish(message='The phase classification comparison is complete. All results, including failures, are saved; teaching has stopped.')
    except Exception as error:
        session.result['error'] = str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        session.finish('stopped' if isinstance(error, InterruptedError) else 'failed', str(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    run(parser.parse_args().run_dir)
