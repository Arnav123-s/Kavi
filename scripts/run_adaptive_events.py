"""Teach bounded input-time graph extensions and repair from original sources."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import traceback

from kavi.adaptive_events import AdaptiveActivity
from kavi.composable_configurations import Work, encoded
from kavi.english_configurations import OPS
from kavi.event_learning import learn
from kavi.event_english import EventEnglish, events
from kavi.published_learning import load_science
from kavi.published_english import PredicateTree
from scripts.configuration_run_support import ROOT, Run
from scripts.run_direct_event_learning import evaluate as direct_evaluate, ordered
from scripts.run_english_configurations import dataset


def propose(model, text, registry, work):
    activity = AdaptiveActivity(model.graph, work)
    quantities = []
    for event, value in events(text, model.vocabulary):
        if value is not None:
            quantities.append(value)
        activity.feed(event)
    activity.close()
    proposed = activity.proposals()
    value = None
    if proposed:
        relation = OPS[proposed[0][1]]
        args = tuple(reversed(quantities)) if relation.startswith('r') else tuple(quantities)
        name = {'+':'science_sum', '-':'science_difference', '*':'science_work', '/':'science_ratio'}[relation.removeprefix('r')]
        value = registry.execute(name, args, work)
    return activity, proposed, value


def competence_features(activity, proposals):
    result = {'surviving_candidates='+str(len(proposals)),
        'maximum_active='+str(activity.maximum_active)}
    if proposals:
        first, port = proposals[0]
        result.update(('proposed_relation='+OPS[port], 'new_connections='+str(len(first.links))))
        result.add('existing_path' if not first.links else 'provisional_path')
        if len({label for _, label in proposals}) == 1:
            result.add('candidate_agreement')
    else:
        result.add('no_completed_proposal')
    return frozenset(result)


def assess(model, rows, registry, session, competence=None):
    records, counts = [], Counter()
    for row in rows:
        work = Work(check=session.check, limit=1_000_000)
        item = {'id':row['id'], 'correct':False}
        try:
            activity, proposals, value = propose(model, row['text'], registry, work)
            item.update(correct=value is not None and math.isclose(value, row['expected'], rel_tol=1e-8, abs_tol=1e-9),
                unresolved=value is None, candidate_count=len(proposals),
                candidate_answer_agreement=len({label for _, label in proposals}) == 1,
                maximum_active=activity.maximum_active)
            if competence is not None:
                ports, _ = competence.activate(competence_features(activity, proposals), work)
                item['self_assessment'] = ports[0]
        except (ValueError, ZeroDivisionError, OverflowError, InterruptedError) as error:
            if isinstance(error, InterruptedError) and str(error) != 'Configuration work budget exhausted':
                raise
            item['error'] = str(error)
        counts.update(work.counts)
        records.append(item)
    assessments = {label:{'total':sum(r.get('self_assessment') == label for r in records),
        'correct':sum(r.get('self_assessment') == label and r['correct'] for r in records)}
        for label in ('needs_help', 'can_propose')}
    return {'correct':sum(row['correct'] for row in records), 'total':len(records),
        'unresolved':sum(row.get('unresolved', False) for row in records),
        'self_assessment':assessments, 'work':dict(counts), 'rows':records}


def run(folder):
    session = Run(folder, 'docs/ADAPTIVE_EVENT_PROTOCOL.md', [
        'kavi/adaptive_events.py', 'kavi/event_learning.py', 'kavi/event_english.py',
        'kavi/published_english.py',
        'scripts/run_adaptive_events.py', 'scripts/run_direct_event_learning.py'])
    try:
        old = json.loads((ROOT/'runs/direct-event-learning-20260907/results.json').read_text(encoding='utf-8'))
        if old['state'] != 'completed':
            raise ValueError('Direct event learning must have completed')
        from kavi.english_configurations import WORD
        data = dataset()[0]
        by_id = {row['id']:row for row in data}
        taught = [by_id[pid] for pid in old['partitions']['training']]
        ids = set(old['partitions']['training'])
        extra = ordered([row for row in data if row['partition'] == 'train' and row['id'] not in ids
            and len(row['input'].numbers) == 2 and len(WORD.findall(row['text'])) <= 60])[:24]
        development = [by_id[pid] for pid in old['partitions']['development']]
        final = [by_id[pid] for pid in old['partitions']['followup']]
        assert not {row['signature'] for row in taught+extra} & {row['signature'] for row in development+final}
        session.result['partitions'] = {'initial_training':[row['id'] for row in taught],
            'new_teaching':[row['id'] for row in extra], 'development':[row['id'] for row in development],
            'followup':[row['id'] for row in final]}
        initial = EventEnglish.from_record(json.loads((ROOT/'runs/direct-event-learning-20260907/model.json').read_text(encoding='utf-8')))
        model = EventEnglish.from_record(initial.record())
        registry = load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json', extended=True).registry
        previous = direct_evaluate(model, taught, registry, session)
        session.result['initial_training'] = previous
        session.result['corrections'] = []
        rebuilds = 0
        self_lessons = []
        for number, row in enumerate(extra, 1):
            work = Work(check=session.check, limit=1_000_000)
            activity, proposals, value = propose(model, row['text'], registry, work)
            item = {'id':row['id'], 'before_correct':value is not None and math.isclose(value, row['expected'], rel_tol=1e-8, abs_tol=1e-9),
                'candidate_count':len(proposals), 'maximum_active':activity.maximum_active,
                'input_work':dict(work.counts), 'after_correct':False, 'action':'unresolved correction'}
            self_lessons.append((competence_features(activity, proposals),
                'can_propose' if item['before_correct'] else 'needs_help'))
            # Only now does the teacher disclose the source's relation.
            expected = OPS.index(row['labels'][0, 1])
            matches = [candidate for candidate, label in proposals if label == expected]
            taught.append(row)
            required = {r['id'] for r in previous['rows'] if r['correct']}
            candidate = None
            if matches:
                candidate = EventEnglish(activity.commit(matches[0], model.graph), model.vocabulary)
                item.update(action='extension' if matches[0].links else 'already consistent',
                    added_connections=len(matches[0].links), defined_execution_preservation=True)
            elif rebuilds < 6:
                rebuilds += 1
                fitting = Work(check=session.check, limit=100_000_000)
                examples = [(tuple(token for token, _ in events(source['text'], model.vocabulary)),
                    OPS.index(source['labels'][0, 1])) for source in taught]
                item.update(action='global repair proposed', replayed_source_lessons=len(examples))
                try:
                    graph, stats = learn(examples, fitting, seed=19)
                    candidate = EventEnglish(graph, model.vocabulary)
                    item['fitting'] = stats
                except (ValueError, InterruptedError) as error:
                    if isinstance(error, InterruptedError) and str(error) != 'Configuration work budget exhausted':
                        raise
                    item['repair_failure'] = str(error)
                item['learning_work'] = fitting.counts
            if candidate is not None:
                checked = direct_evaluate(candidate, taught, registry, session)
                correct = {r['id'] for r in checked['rows'] if r['correct']}
                lost = sorted(required-correct)
                item.update(retention_work=checked['work'], regressions=lost,
                    earlier_correct_obligations=len(required))
                if not lost and row['id'] in correct:
                    model, previous = candidate, checked
                    item['after_correct'] = True
                    if item['action'] == 'global repair proposed':
                        item['action'] = 'global repair accepted'
                else:
                    item['action'] = 'candidate rejected'
            if not item['after_correct']:
                previous = direct_evaluate(model, taught, registry, session)
                item['unchanged_evaluation_work'] = previous['work']
            session.result['corrections'].append(item)
            session.present('Input proposes a shape; correction checks it',
                'New words can open provisional connections. The original worked relation decides whether a proposed change can become lasting structure.',
                f'Lesson {number}/{len(extra)}: {item["action"]}; {previous["correct"]}/{previous["total"]} teaching answers',
                boxes=['Word input', 'Provisional connections', 'Original correction', 'Accepted configuration'], active=2, delay=.3)
        self_work = Work(check=session.check, limit=1_000_000)
        competence = PredicateTree(('needs_help', 'can_propose')).teach(self_lessons, self_work, depth=3, min_leaf=3)
        snapshot = model.record()
        snapshot['competence'] = {'feature_semantics':'activity-observations-1', 'nodes':competence.nodes}
        session.result['competence_learning'] = {'examples':len(self_lessons),
            'labels':dict(Counter(label for _, label in self_lessons)), 'work':self_work.counts,
            'nodes':len(competence.nodes), 'bytes':len(encoded(snapshot['competence']))}
        raw = encoded(snapshot)
        (session.folder/'model.json').write_bytes(raw)
        session.result['artifact'] = {'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest(),
            'states':len(model.graph.outputs), 'edges':sum(map(len, model.graph.transitions))}
        session.result['online_before_correct'] = sum(row['before_correct'] for row in session.result['corrections'])
        session.result['online_after_correct'] = sum(row['after_correct'] for row in session.result['corrections'])
        session.result['global_reconstructions'] = rebuilds
        session.result['final_training'] = previous
        session.present('Freeze a snapshot for follow-up measurement',
            'Temporary candidate construction remains enabled in its comparison. No follow-up answer can change persistent connections.',
            f'{len(raw):,} bytes; {previous["correct"]}/{previous["total"]} teaching answers', active=3, delay=1)
        session.result['development_direct'] = direct_evaluate(model, development, registry, session)
        session.result['development_adaptive'] = assess(model, development, registry, session, competence)
        session.result['followup_direct'] = direct_evaluate(model, final, registry, session)
        session.result['followup_adaptive'] = assess(model, final, registry, session, competence)
        session.result['initial_adaptive_control'] = assess(initial, final, registry, session)
        after = model.record()
        after['competence'] = {'feature_semantics':'activity-observations-1', 'nodes':competence.nodes}
        session.result['frozen_artifact_unchanged'] = encoded(after) == raw
        session.result['actions'] = dict(Counter(row['action'] for row in session.result['corrections']))
        session.present('Adaptive structure experiment completed',
            'The report separates first answers, corrections, structure changes and follow-up results.',
            f'{session.result["followup_adaptive"]["correct"]}/{len(final)} follow-up answers with provisional adaptation', active=3, delay=2)
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
