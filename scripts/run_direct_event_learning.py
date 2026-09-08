"""Teach direct recurrent word transitions using original arithmetic lessons."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import traceback

from kavi.composable_configurations import Work, encoded
from kavi.english_configurations import OPS, WORD, stem
from kavi.event_learning import EventConfiguration, learn, prefix
from kavi.event_english import EventEnglish, events
from kavi.published_learning import load_science
from scripts.configuration_run_support import ROOT, Run
from scripts.run_english_configurations import dataset


def evaluate(model, rows, registry, session):
    results = []
    counts = Counter()
    for row in rows:
        work = Work(check=session.check, limit=1_000_000)
        record = {'id':row['id'], 'correct':False}
        try:
            response = model.answer(row['text'], registry, work)
            value = response['value']
            record.update(correct=value is not None and math.isclose(value, row['expected'], rel_tol=1e-8, abs_tol=1e-9),
                value=value, state=response['state'], events=response['events'], live_values=response['live_values'])
        except (ValueError, ZeroDivisionError, OverflowError, InterruptedError) as error:
            if isinstance(error, InterruptedError) and str(error) != 'Configuration work budget exhausted':
                raise
            record['error'] = str(error)
        results.append(record)
        counts.update(work.counts)
    return {'correct':sum(row['correct'] for row in results), 'total':len(rows),
        'unresolved':sum(row.get('state') == 'unresolved' for row in results),
        'work':dict(counts), 'rows':results}


def ordered(rows):
    return sorted(rows, key=lambda row:(hashlib.sha256(row['signature'].encode()).hexdigest(), row['id']))


def run(folder):
    session = Run(folder, 'docs/DIRECT_EVENT_LEARNING_PROTOCOL.md', [
        'kavi/event_learning.py', 'kavi/event_english.py', 'kavi/signal_configurations.py',
        'scripts/run_direct_event_learning.py'])
    try:
        rows, excluded, unsupported = dataset()
        eligible = [row for row in rows if len(row['input'].numbers) == 2 and len(WORD.findall(row['text'])) <= 60]
        training = ordered([row for row in eligible if row['partition'] == 'train'])[:144]
        development = ordered([row for row in eligible if row['partition'] == 'development'])[:80]
        final = ordered([row for row in eligible if row['partition'] == 'test'])
        assert not {row['signature'] for row in training} & {row['signature'] for row in development+final}
        counts = Counter(stem(word) for row in training for word in WORD.findall(row['text']) if word.isalpha())
        vocabulary = sorted(counts, key=lambda word:(-counts[word], word))[:128]
        session.result['admission'] = {'source_total':2305, 'source_excluded':len(excluded),
            'earlier_unsupported':len(unsupported), 'eligible_direct_event_questions':len(eligible),
            'selected_training':len(training), 'development':len(development), 'followup':len(final),
            'earlier_supported_test_total':150}
        session.result['partitions'] = {name:[row['id'] for row in group]
            for name, group in (('training', training), ('development', development), ('followup', final))}
        registry = load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json', extended=True).registry
        current = EventEnglish(EventConfiguration([{}], [None]), vocabulary)
        previous = {'rows':[]}
        taught = []
        session.result['stages'] = []
        for start in range(0, len(training), 48):
            batch = training[start:start+48]
            before = evaluate(current, batch, registry, session)
            required = {row['id'] for row in previous['rows'] if row['correct']}
            taught += batch
            examples = [(tuple(token for token, _ in events(row['text'], vocabulary)),
                OPS.index(row['labels'][0, 1])) for row in taught]
            # Detect an encoding collision before fitting; preserve it as a
            # measured limitation and use only the declared literal fallback.
            labels = {}
            collision = False
            for sequence, label in examples:
                if sequence in labels and labels[sequence] != label:
                    collision = True
                labels[sequence] = label
            if collision:
                vocabulary = sorted({stem(word) for row in taught for word in WORD.findall(row['text']) if word.isalpha()})
                examples = [(tuple(token for token, _ in events(row['text'], vocabulary)),
                    OPS.index(row['labels'][0, 1])) for row in taught]
            session.present('Teach the changing interpretation state',
                'Each word drives a learned transition. Correct source explanations constrain a successor graph and its arithmetic output ports.',
                f'{len(taught)} genuine lessons; {before["correct"]}/{before["total"]} new questions correct before teaching',
                boxes=['Word event', 'Changing learned state', 'Held quantities', 'Existing arithmetic path'], active=1, delay=2)
            baseline = evaluate(current, taught, registry, session)
            old_dev = evaluate(current, development, registry, session)
            choices = [(current, old_dev, baseline, len(encoded(current.record())), 'keep')]
            candidates = []
            for seed in (7, 19):
                work = Work(check=session.check, limit=100_000_000)
                item = {'seed':seed}
                try:
                    graph, stats = learn(examples, work, seed=seed)
                    candidate = EventEnglish(graph, vocabulary)
                    train = evaluate(candidate, taught, registry, session)
                    dev = evaluate(candidate, development, registry, session)
                    correct = {row['id'] for row in train['rows'] if row['correct']}
                    lost = sorted(required-correct)
                    size = len(encoded(candidate.record()))
                    item.update(stats=stats, training=train, development=dev, regressions=lost,
                        admissible=not lost, bytes=size)
                    if not lost:
                        choices.append((candidate, dev, train, size, seed))
                    session.present('Check the new recurrent connections',
                        'The state graph was inferred from the lessons. It must execute its chosen operation through the older acquired arithmetic paths.',
                        f'Seed {seed}: {dev["correct"]}/{dev["total"]} development; {len(graph.outputs)} states; {len(lost)} teaching losses', active=1, delay=.5)
                except (ValueError, InterruptedError) as error:
                    if isinstance(error, InterruptedError) and str(error) != 'Configuration work budget exhausted':
                        raise
                    item['failure'] = str(error)
                    session.present('Candidate did not complete',
                        'This failure is retained. The earlier configuration remains available.',
                        f'Seed {seed}: {error}', active=1, delay=.5)
                item['learning_work'] = work.counts
                candidates.append(item)
            current, dev, previous, size, selected = max(choices, key=lambda c:(c[1]['correct'], c[2]['correct'], -c[3]))
            session.result['stages'].append({'teaching_total':len(taught), 'new_questions_before_correction':before,
                'encoding_collision':collision, 'fitting_vocabulary':len(vocabulary),
                'candidates':candidates, 'selected':selected, 'selected_bytes':size,
                'selected_training_correct':previous['correct'], 'selected_development_correct':dev['correct'],
                'earlier_correct_obligations':len(required), 'selected_regressions':0,
                'precorrection_work':baseline['work'], 'previous_development_work':old_dev['work']})
            session.save()
        raw = encoded(current.record())
        (session.folder/'model.json').write_bytes(raw)
        session.result['artifact'] = {'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest(),
            'states':len(current.graph.outputs), 'edges':sum(map(len, current.graph.transitions)),
            'vocabulary':len(current.vocabulary)}
        session.result['selected_development'] = dev
        session.present('Freeze direct event learning',
            'The saved object contains recurrent transitions and output connections. The original source questions remain outside inference.',
            f'{len(raw):,} bytes; {dev["correct"]}/{dev["total"]} development', active=3, delay=2)
        session.result['followup'] = evaluate(current, final, registry, session)
        work = Work(check=session.check, limit=100_000_000)
        examples = [(tuple(token for token, _ in events(row['text'], current.vocabulary)),
            OPS.index(row['labels'][0, 1])) for row in taught]
        control = EventEnglish(prefix(examples, work, 10000), current.vocabulary)
        control_raw = encoded(control.record())
        (session.folder/'prefix-control.json').write_bytes(control_raw)
        session.result['prefix_control'] = {'states':len(control.graph.outputs), 'bytes':len(control_raw),
            'work':work.counts, 'followup':evaluate(control, final, registry, session),
            'public_artifact':False, 'reason':'Unfolded source event paths remain private.'}
        initial = json.loads((ROOT/'experiments/2026-09-07-published-english.json').read_text(encoding='utf-8'))['initial']['test']['rows']
        old = {row['id']:row['correct'] for row in initial}
        session.result['initial_predicate_control'] = {'same_questions':len(final),
            'correct':sum(old[row['id']] for row in final), 'additional_training':False}
        session.result['frozen_artifact_unchanged'] = encoded(current.record()) == raw
        session.result['foundation_development_threshold_met'] = dev['correct'] >= .9*dev['total']
        session.present('Direct state correction completed',
            'This score measures learned word-event transitions, not the earlier predicate-tree wrapper. Weak results and unresolved questions remain included.',
            f'{session.result["followup"]["correct"]}/{len(final)} eligible follow-up answers; {session.result["followup"]["unresolved"]} unresolved', active=3, delay=2)
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
