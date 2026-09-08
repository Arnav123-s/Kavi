"""Compare inherited-path correction with the completed reconstruction course."""

import argparse
import hashlib
import json
from pathlib import Path
import traceback

from kavi.composable_configurations import Work, encoded
from kavi.english_configurations import features
from kavi.human_math_sources import gsm
from kavi.pathway_transfer import refine
from kavi.published_learning import load_science
from kavi.streaming_english import StreamingEnglishReasoner
from scripts.configuration_run_support import ROOT, Run
from scripts.run_english_configurations import dataset
from scripts.run_incremental_english import evaluate


def run(folder):
    session = Run(folder, 'docs/PATHWAY_TRANSFER_PROTOCOL.md', [
        'kavi/pathway_transfer.py', 'kavi/english_configurations.py',
        'kavi/streaming_english.py', 'kavi/signal_configurations.py',
        'scripts/run_incremental_english.py', 'scripts/run_pathway_transfer.py'])
    try:
        control = json.loads((ROOT/'runs/incremental-english-20260907/results.json').read_text(encoding='utf-8'))
        if control['state'] != 'completed':
            raise ValueError('The matched reconstruction course is incomplete')
        original, _, _ = dataset()
        extra, _ = gsm('train')
        by_id = {row['id']:row for row in original+extra}
        parts = control['partitions']
        teaching = [by_id[pid] for pid in parts['initial_training']]
        batches = [[by_id[pid] for pid in batch] for batch in parts['batches']]
        development = [by_id[pid] for pid in parts['development']]
        followup = [by_id[pid] for pid in parts['followup']]
        session.result['partitions'] = parts
        assert not {r['signature'] for r in teaching+sum(batches, [])} & {r['signature'] for r in development+followup}
        registry = load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json', extended=True).registry
        current = StreamingEnglishReasoner.load(ROOT/'experiments/english-20260907-initial-model.json')
        previous = evaluate(current, teaching, registry, session)
        dev = evaluate(current, development, registry, session)
        session.result.update(initial_training=previous, initial_development=dev, stages=[])
        for stage, batch in enumerate(batches, 1):
            required = {r['id'] for r in previous['rows'] if r['correct']}
            teaching += batch
            examples = [(features(r['input'], *pair), label) for r in teaching for pair, label in r['labels'].items()]
            baseline = evaluate(current, teaching, registry, session)
            choices = [(current, dev, baseline, len(encoded(current.record())), 'keep')]
            candidates = []
            parent_hash = hashlib.sha256(encoded(current.record())).hexdigest()
            session.present('Teach through the older pathways',
                'Use established routes to locate the relationships that need correction. Teach new distinctions at those destinations.',
                f'Increment {stage}: {len(batch)} new published questions; {len(teaching)} total',
                boxes=['Older configuration', 'Locate correction', 'Learn a refinement', 'Check retained skills'], active=1, delay=2)
            for depth in (2, 4, 8):
                work = Work(check=session.check, limit=60_000_000)
                candidate = StreamingEnglishReasoner(refine(current.router, examples, work, depth=depth))
                assert hashlib.sha256(encoded(current.record())).hexdigest() == parent_hash
                train = evaluate(candidate, teaching, registry, session)
                success = {r['id']:r['correct'] for r in train['rows']}
                lost = sorted(pid for pid in required if not success.get(pid, False))
                measured = evaluate(candidate, development, registry, session)
                size = len(encoded(candidate.record()))
                candidates.append({'depth':depth, 'bytes':size, 'nodes':len(candidate.router.nodes),
                    'learning_work':work.counts, 'training':train, 'development':measured,
                    'regressions':lost, 'admissible':not lost})
                if not lost:
                    choices.append((candidate, measured, train, size, depth))
                session.present('Check the inherited configuration',
                    'A learned refinement must retain earlier correct teaching answers before it can replace its teacher.',
                    f'Refinement depth {depth}: {measured["correct"]}/{measured["total"]} development; {len(lost)} teaching losses', active=3, delay=.5)
            current, dev, previous, size, selected = max(choices, key=lambda c:(c[1]['correct'], c[2]['correct'], -c[3]))
            session.result['stages'].append({'stage':stage, 'added':len(batch), 'teaching_total':len(teaching),
                'parent_sha256':parent_hash, 'parent_unchanged':True, 'precorrection_work':baseline['work'],
                'candidates':candidates, 'selected':selected, 'selected_bytes':size,
                'selected_training_correct':previous['correct'], 'selected_development_correct':dev['correct'],
                'earlier_correct_obligations':len(required), 'selected_regressions':0})
            session.save()
        raw = encoded(current.record())
        (session.folder/'model.json').write_bytes(raw)
        session.result['artifact'] = {'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest(), 'nodes':len(current.router.nodes)}
        session.result['selected_development'] = dev
        session.present('Freeze the transferred configuration',
            'The next score revisits the earlier test questions. Their answers did not choose the refinements.',
            f'{len(raw):,} bytes; {dev["correct"]}/{dev["total"]} development', active=3, delay=2)
        final = evaluate(current, followup, registry, session)
        initial = json.loads((ROOT/'experiments/2026-09-07-published-english.json').read_text(encoding='utf-8'))['initial']['test']['rows']
        a = {r['id']:r['correct'] for r in initial}
        b = {r['id']:r['correct'] for r in final['rows']}
        session.result['followup'] = final
        session.result['followup_retention'] = {'earlier_correct':sum(a.values()), 'current_correct':sum(b.values()),
            'lost':[pid for pid in a if a[pid] and not b[pid]],
            'gained':[pid for pid in a if not a[pid] and b[pid]], 'same_questions':len(a)}
        session.result['foundation_development_threshold_met'] = dev['correct'] >= .9*dev['total']
        session.present('Transfer course completed',
            'This measures learning through inherited routes. The update procedure itself is still supplied.',
            f'{final["correct"]}/{final["total"]} earlier test answers; {len(session.result["followup_retention"]["lost"])} earlier correct answers lost', active=3, delay=2)
        session.finish()
    except Exception as error:
        session.result['error'] = str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        session.finish('stopped' if isinstance(error, InterruptedError) else 'failed', str(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    run(parser.parse_args().run_dir)
