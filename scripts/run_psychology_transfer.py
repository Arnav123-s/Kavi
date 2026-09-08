"""A finite visible comparison of cross-subject recurrent graph reuse."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import traceback

from kavi.composable_configurations import Work, encoded
from kavi.event_learning import EventConfiguration
from kavi.event_transfer import graft, preserves
from kavi.text_choice_events import REJECT, SUPPORT, TextChoice, events, words
from scripts.configuration_run_support import ROOT, Run

DATA = ROOT/'private/psychology-sources-20260907'
BASE = ROOT/'experiments/english-20260907-adaptive-model.json'


def partitions(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row['module']].append(row)
    training, development, final = [], [], []
    for group in groups.values():
        group.sort(key=lambda row: hashlib.sha256(row['id'].encode()).hexdigest())
        if len(group) >= 4:
            training.extend(group[:-2])
            development.append(group[-2])
            final.append(group[-1])
        elif len(group) >= 2:
            training.extend(group[:-1])
            final.append(group[-1])
        else:
            training.extend(group)
    seen = {}
    for name, group in (('training', training), ('development', development), ('final', final)):
        for row in group:
            signature = ' '.join(row['question'].casefold().split())
            if signature in seen and seen[signature] != name:
                raise ValueError('Duplicate question crosses partitions; review the split')
            seen[signature] = name
    return training, development, final


def evaluate(model, rows, session, *, adaptive=False):
    evidence, counts = [], Counter()
    for row in rows:
        work = Work(check=session.check, limit=2_000_000)
        item = {'id': row['id'], 'correct': False, 'state': 'unresolved'}
        try:
            response = model.answer(row['question'], row['options'], work, adaptive=adaptive)
            item.update(response, correct=response['answer'] == row['answer'])
        except (ValueError, InterruptedError) as error:
            if isinstance(error, InterruptedError) and str(error) != 'Configuration work budget exhausted':
                raise
            item['error'] = str(error)
        counts.update(work.counts)
        evidence.append(item)
    return {'correct': sum(row['correct'] for row in evidence), 'total': len(evidence),
        'unresolved': sum(row['state'] == 'unresolved' for row in evidence), 'work': dict(counts),
        'old_state_visits': sum(row.get('old_state_visits', 0) for row in evidence), 'rows': evidence}


def run(folder):
    session = Run(folder, 'docs/PSYCHOLOGY_TRANSFER_PROTOCOL.md', [
        'kavi/event_learning.py', 'kavi/event_transfer.py', 'kavi/text_choice_events.py',
        'kavi/adaptive_events.py', 'scripts/run_psychology_transfer.py',
        'scripts/acquire_psychology_sources.py', 'scripts/extract_psychology_exams.py'])
    try:
        source = json.loads((DATA/'questions.json').read_text(encoding='utf-8'))
        training, development, final = partitions(source['openstax'])
        base_record = json.loads(BASE.read_text(encoding='utf-8'))
        base = EventConfiguration(**base_record['graph'])
        vocabulary = sorted({token for row in training for text in [row['question'], *row['options']] for token in words(text)})
        session.result.update(source_manifest=json.loads((DATA/'manifest.json').read_text(encoding='utf-8')),
            data_hashes={name: hashlib.sha256((DATA/name).read_bytes()).hexdigest()
                         for name in ('questions.json', 'exams.json', 'manifest.json')},
            base={'file': str(BASE.relative_to(ROOT)).replace('\\', '/'), 'bytes': BASE.stat().st_size,
                  'sha256': hashlib.sha256(BASE.read_bytes()).hexdigest()},
            partitions={name: [row['id'] for row in group] for name, group in
                        (('training', training), ('development', development), ('final_openstax', final))},
            vocabulary=len(vocabulary), arms={}, teaching_pairs_presented=0)
        current = {name: TextChoice(EventConfiguration([dict(row) for row in base.transitions], list(base.outputs)),
                                   vocabulary, list(range(len(base.outputs)))) for name in ('reuse', 'separate')}
        stages = [('Learning and research', {2, 6, 8}), ('Thinking and intelligence', {7}),
                  ('Personality and psychological disorders', {11, 15})]
        cumulative = []
        for name in current:
            session.result['arms'][name] = {'stages': []}
        session.present('Original lessons are ready',
            'The same psychology lessons will teach two configurations. One can connect new routes to its earlier English states; the other cannot.',
            f'{len(training)} teaching questions; {len(development)} development questions; final keys withheld',
            boxes=['Original lesson', 'Earlier learned shape', 'New connections', 'Check the answer'], active=1, delay=3)
        for title, chapters in stages:
            batch = sorted([row for row in training if row['chapter'] in chapters], key=lambda row: row['id'])
            cumulative += batch
            samples = [(tuple(events(row['question'], option, vocabulary)), SUPPORT if i == row['answer'] else REJECT)
                       for row in cumulative for i, option in enumerate(row['options'])]
            for name, previous in list(current.items()):
                before = evaluate(previous, batch, session)
                old_train = evaluate(previous, cumulative, session)
                old_dev = evaluate(previous, development, session)
                stage = {'title': title, 'new_questions': len(batch), 'total_teaching': len(cumulative),
                    'before': before, 'earlier_evaluation': old_train, 'earlier_development': old_dev}
                session.present(title,
                    'Original answer keys correct the new routes. Previously correct teaching answers must survive; the earlier arithmetic paths have an exact preservation check.',
                    f'{name}: {before["correct"]}/{len(batch)} new questions before correction; {len(cumulative)} accumulated lessons',
                    boxes=['Published correction', 'Reuse old states' if name == 'reuse' else 'Control: new states',
                           'Check earlier skills', 'Completed answer'], active=1, delay=.6)
                work = Work(check=session.check, limit=35_000_000)
                try:
                    graph, embedding, stats = graft(base, samples, work, reuse=name == 'reuse', seed=7)
                    candidate = TextChoice(graph, vocabulary, embedding)
                    taught = evaluate(candidate, cumulative, session)
                    dev = evaluate(candidate, development, session)
                    required = {row['id'] for row in old_train['rows'] if row['correct']}
                    correct = {row['id'] for row in taught['rows'] if row['correct']}
                    regressions = sorted(required-correct)
                    stage.update(fitting=stats, training=taught, development=dev, regressions=regressions,
                                 bytes=len(encoded(candidate.record())))
                    new_rank = (taught['correct'], dev['correct'], -len(encoded(candidate.record())))
                    old_rank = (old_train['correct'], old_dev['correct'], -len(encoded(previous.record())))
                    if not regressions and new_rank >= old_rank:
                        current[name] = candidate
                        stage['selected'] = 'candidate'
                    else:
                        stage['selected'] = 'previous'
                    session.present(title+' checked',
                        'A completed graph stores learned routes. The source questions remain outside inference.',
                        f'{name}: {taught["correct"]}/{len(cumulative)} teaching; {dev["correct"]}/{len(development)} development; {stats["old_state_merges"]} joins to earlier states',
                        active=2, delay=.7)
                except (ValueError, InterruptedError) as error:
                    if isinstance(error, InterruptedError) and str(error) != 'Configuration work budget exhausted':
                        raise
                    stage.update(failure=str(error), selected='previous')
                    session.present('Candidate stopped at its bound',
                        'The failure is recorded, and the earlier accepted configuration is retained.',
                        f'{name}: {error}', active=2, delay=.5)
                stage['learning_work'] = work.counts
                session.result['teaching_pairs_presented'] += len(samples)
                session.result['arms'][name]['stages'].append(stage)
                session.save()
        # Independent examination text and keys enter only after fitting and selection.
        examination = json.loads((DATA/'exams.json').read_text(encoding='utf-8'))
        earlier_signatures = {' '.join(row['question'].casefold().split()) for row in training+development+final}
        duplicates = [row['id'] for row in examination['rows']
                      if ' '.join(row['question'].casefold().split()) in earlier_signatures]
        independent = [row for row in examination['rows'] if row['id'] not in duplicates]
        session.result['independent_duplicate_exclusions'] = duplicates
        session.result['independent_sources'] = {key: value for key, value in examination.items() if key != 'rows'}
        session.result['partitions']['final_mit'] = [row['id'] for row in independent]
        session.present('Freeze learning and open the independent exams',
            'The final questions cannot change persistent routes or select a model. Direct execution and provisional connections are scored separately.',
            f'{len(final)} withheld textbook questions; {len(independent)} independent MIT questions', active=3, delay=2)
        majority = Counter(row['answer'] for row in training).most_common(1)[0][0]
        for name, model in current.items():
            record = model.record()
            raw = encoded(record)
            (session.folder/(name+'-model.json')).write_bytes(raw)
            arm = session.result['arms'][name]
            arm['artifact'] = {'file': name+'-model.json', 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                'states': len(model.graph.outputs), 'edges': sum(map(len, model.graph.transitions)),
                'license': 'CC BY-NC-SA 4.0'}
            arm['final_training'] = evaluate(model, training, session)
            preservation_work = Work(check=session.check)
            arm['old_defined_execution_preserved'] = preserves(base, model.graph, model.embedding, preservation_work)
            arm['preservation_work'] = preservation_work.counts
            for bank, rows in (('openstax', final), ('mit', independent)):
                arm[bank] = evaluate(model, rows, session)
                arm[bank+'_adaptive'] = evaluate(model, rows, session, adaptive=True)
            arm['frozen_unchanged'] = encoded(model.record()) == raw
            session.present('Transfer comparison measured',
                'Reused connections count as useful only if they improve new-question results. Unresolved and wrong answers remain in the denominator.',
                f'{name}: textbook {arm["openstax"]["correct"]}/{len(final)}; MIT {arm["mit"]["correct"]}/{len(independent)} direct',
                active=3, delay=1)
        session.result['controls'] = {bank: {'total': len(rows),
            'fixed_first_correct': sum(row['answer'] == 0 for row in rows),
            'most_common_training_position': majority,
            'most_common_training_position_correct': sum(row['answer'] == majority for row in rows)}
            for bank, rows in (('openstax', final), ('mit', independent))}
        session.finish(message='Psychology transfer and its control are complete. The evidence includes every failure; no teaching is still running.')
    except Exception as error:
        session.result['error'] = str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        session.finish('stopped' if isinstance(error, InterruptedError) else 'failed', str(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    run(parser.parse_args().run_dir)
