"""Visible ordered-relation teaching from original dependency annotations."""

import argparse
import hashlib
from pathlib import Path
import traceback

from kavi.composable_configurations import Work, encoded
from kavi.phase import PhaseConfiguration, CircuitTemplate, CircuitGeneration, reconstruct
from kavi.phase.evaluation import evaluate
from kavi.phase.runtime import PhaseActivity
from scripts.configuration_run_support import Run
from scripts.pcl_relation_source import packet, fingerprints, REVISION


def pairs(rows):
    return [(row['events'], row['label']) for row in rows]


def run(folder):
    sources = ['scripts/run_pcl_relations.py', 'scripts/pcl_relation_source.py',
               'scripts/configuration_run_support.py', 'kavi/phase/model.py',
               'kavi/phase/runtime.py', 'kavi/phase/layers.py', 'kavi/phase/regions.py',
               'kavi/phase/learning.py', 'kavi/phase/selection.py', 'kavi/phase/evaluation.py']
    session = Run(folder, 'docs/PCL_RELATION_PROTOCOL.md', sources)
    try:
        banks = packet()
        session.result.update(source_revision=REVISION, source_files=fingerprints(),
                              partitions={name: [row['id'] for row in rows] for name, rows in banks.items()},
                              packet_sha256=hashlib.sha256(encoded(banks)).hexdigest(), arms={})
        session.present('Learning a small piece of sentence structure',
                        'Original sentences provide the lessons. The verb and a selected word are already marked; Kavi must learn subject versus object.',
                        '24 first lessons; 48 total lessons; 24 development; 48 final questions',
                        boxes=['Original annotations', 'Ordered input', 'Whole new circuit', 'Unfamiliar positions'])
        selected = {}
        for capacity in (0, 4):
            for seed in (7, 19, 41):
                name = f'couplings-{capacity}-seed-{seed}'
                model = CircuitGeneration(CircuitTemplate((3, 5, 7, 11), max_couplings=capacity),
                    PhaseConfiguration((3, 5, 7, 11), tuple((event, i, 1) for i, event in
                                        enumerate(('candidate', 'predicate', 'other')))))
                arm = {'stages': []}
                session.result['arms'][name] = arm
                for stage_name in ('first', 'training'):
                    teaching = pairs(banks[stage_name])
                    protected = [] if stage_name == 'first' else pairs(banks['first'])
                    work = Work(check=session.check, limit=5_000_000)
                    stage = {'bank': stage_name}
                    session.present('Trying complete circuit configurations',
                        'The same ordered examples teach every model. Earlier valid answers must survive the second teaching round.',
                        f'{name}: {len(teaching)} lessons, 64 candidate ceiling', delay=.4)
                    try:
                        model, stage['selection'] = reconstruct(model, teaching, protected, work,
                                                               candidates=64, seed=seed, readout='regions')
                    except InterruptedError as error:
                        if str(error) != 'Configuration work budget exhausted':
                            raise
                        stage['failure'] = str(error)
                    stage['learning_work'] = dict(work.counts)
                    score_work = Work(check=session.check)
                    for label, examples in [('teaching', teaching), ('protected', protected),
                                            ('development', pairs(banks['development']))]:
                        stage[label] = evaluate(model, examples, score_work)
                    stage.update(evaluation_work=dict(score_work.counts),
                                 bytes=len(encoded(model.record())), couplings=len(model.circuit.couplings))
                    arm['stages'].append(stage)
                    session.present('Checking what the teaching accomplished',
                        'An unresolved result counts as incorrect. No final answer is used to improve this circuit.',
                        f'{name}: {stage["teaching"]["correct"]}/{len(teaching)} teaching; '
                        f'{stage["development"]["correct"]}/24 development', delay=.4)
                selected[name] = model
        session.present('Learning finished; final questions are now opened',
                        'Every candidate choice is fixed. These position patterns and documents were excluded from earlier banks.', active=3)
        for name, model in selected.items():
            arm = session.result['arms'][name]
            work = Work(check=session.check)
            arm['final'] = evaluate(model, pairs(banks['final']), work)
            equivalent = 0
            for row in banks['final']:
                events = row['events']
                split = events.index('candidate')
                parent = PhaseActivity(model.circuit, work)
                for event in events[:split]:
                    parent.accept(event)
                state = parent.phases
                child = parent.fork()
                for event in events[split:]:
                    child.accept(event)
                equivalent += (child.finish() == model.circuit.predict(events, work)
                               and parent.phases == state and not parent.closed)
            arm['branch_replay_equal'] = equivalent
            arm['final_and_branch_work'] = dict(work.counts)
            raw = encoded(model.record())
            (session.folder/(name+'.json')).write_bytes(raw)
            arm['artifact'] = {'file': name+'.json', 'bytes': len(raw),
                               'sha256': hashlib.sha256(raw).hexdigest()}
            session.present('Final result',
                'This is a narrow grammar test with supplied annotations, not a conversation test.',
                f'{name}: {arm["final"]["correct"]}/48 correct, '
                f'{arm["final"]["unresolved"]} unresolved', active=3, delay=.5)
        rows = banks['final']
        session.result['controls'] = {'total': len(rows),
            'constant_subject': sum(row['label'] == 0 for row in rows),
            'supplied_position_rule': sum(row['label'] == int(row['events'].index('candidate') >
                                           row['events'].index('predicate')) for row in rows),
            'position_comparisons': 2*len(rows), 'constant_comparisons': len(rows)}
        session.finish(message='The ordered-relation course is finished. Results and failures are saved. No teaching remains active.')
    except Exception as error:
        session.result['error'] = str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        session.finish('stopped' if isinstance(error, InterruptedError) else 'failed', str(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    run(parser.parse_args().run_dir)
