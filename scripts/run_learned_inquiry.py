"""Teach question decisions from genuine worked-example corrections."""

import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import traceback
import xml.etree.ElementTree as ET

from kavi.composable_configurations import Work, encoded
from kavi.english_configurations import features, signature
from kavi.human_math_sources import EXCLUDED, gsm
from kavi.learned_inquiry import InquiryModel, decision_features, relations
from kavi.published_english import PredicateTree
from kavi.published_learning import load_science
from kavi.streaming_english import StreamingEnglishReasoner
from scripts.configuration_run_support import ROOT, Run
from scripts.run_english_configurations import dataset


def agrees(value, expected):
    return value is not None and math.isclose(value, expected, rel_tol=1e-8, abs_tol=1e-9)


def local_failure(error):
    if isinstance(error, InterruptedError) and str(error) != 'Configuration work budget exhausted':
        raise error


def evaluate(model, rows, registry, session, mode='learned'):
    answers = []
    counts = Counter()
    before_hash = hashlib.sha256(encoded(model.record())).hexdigest()
    for row in rows:
        work = Work(check=session.check, limit=1_000_000)
        record = {'id':row['id'], 'before_correct':False, 'after_correct':False, 'asked':False}
        try:
            turn = model.begin(row['text'], work)
            first = turn.answer(registry, work)
            record.update(before_value=first['value'], before_correct=agrees(first['value'], row['expected']))
            question = turn.ask(work) if mode == 'learned' else turn.request((0, 1)) if mode == 'always' else None
            if question is not None:
                record.update(asked=True, pair=question['pair'], question=question['text'])
                # This boundary is the teacher. No answer or annotation was
                # available to begin(), ask(), or the first calculation.
                reply = row['labels'][tuple(question['pair'])]
                record['teacher_relation'] = reply
                work.add('teacher_replies')
                turn.clarify(reply, work)
                final = turn.answer(registry, work)
            else:
                final = first
            record.update(after_value=final['value'], after_correct=agrees(final['value'], row['expected']))
        except (ValueError, ZeroDivisionError, OverflowError, InterruptedError) as error:
            local_failure(error)
            record['error'] = str(error)
        answers.append(record)
        counts.update(work.counts)
    asked = [row for row in answers if row['asked']]
    unassisted = [row for row in answers if not row['asked'] and 'before_value' in row]
    assert hashlib.sha256(encoded(model.record())).hexdigest() == before_hash
    return {'total':len(rows), 'before_correct':sum(row['before_correct'] for row in answers),
        'after_correct':sum(row['after_correct'] for row in answers), 'questions_asked':len(asked),
        'helpful':sum(not row['before_correct'] and row['after_correct'] for row in asked),
        'harmful':sum(row['before_correct'] and not row['after_correct'] for row in asked),
        'unchanged':sum(row['before_correct'] == row['after_correct'] for row in asked),
        'without_clarification_issued':len(unassisted),
        'without_clarification_correct':sum(row['after_correct'] for row in unassisted),
        'frozen_artifact_unchanged':True, 'work':dict(counts), 'rows':answers}


def teaching_feedback(model, rows, registry, session):
    examples, records = [], []
    counts, labels = Counter(), Counter()
    for row in rows:
        work = Work(check=session.check, limit=1_000_000)
        record = {'id':row['id'], 'prediction_correct':False}
        try:
            turn = model.begin(row['text'], work)
            prediction = turn.answer(registry, work)
            correct = agrees(prediction['value'], row['expected'])
            current = relations(turn.best.program)
            record['prediction_correct'] = correct
            feedback = []
            for pair, teacher_relation in sorted(row['labels'].items()):
                action = 'ask' if not correct and current[pair] != teacher_relation else 'answer'
                # These predicates use only the question and the model's
                # pre-correction proposal. The target is supplied afterward.
                inputs = decision_features(features(row['input'], *pair), pair, turn.best.program,
                    turn.alternative.program if turn.alternative else None, turn.preferences[pair])
                examples.append((inputs, action))
                labels[action] += 1
                feedback.append({'pair':list(pair), 'action':action})
                work.add('genuine_relation_feedback')
            record['feedback'] = feedback
        except (ValueError, ZeroDivisionError, OverflowError, InterruptedError) as error:
            local_failure(error)
            record['error'] = str(error)
        records.append(record)
        counts.update(work.counts)
    return examples, {'total':len(rows), 'correct_before_feedback':sum(row['prediction_correct'] for row in records),
        'labels':dict(labels), 'work':dict(counts), 'rows':records}


def order(rows):
    return sorted(rows, key=lambda row:(hashlib.sha256(row['signature'].encode()).hexdigest(), row['id']))


def run(folder):
    session = Run(folder, 'docs/LEARNED_INQUIRY_PROTOCOL.md', [
        'kavi/learned_inquiry.py', 'kavi/streaming_english.py', 'kavi/signal_configurations.py',
        'kavi/english_configurations.py', 'kavi/published_english.py',
        'kavi/human_math_sources.py', 'scripts/run_learned_inquiry.py'])
    try:
        incremental = json.loads((ROOT/'runs/incremental-english-20260907/results.json').read_text(encoding='utf-8'))
        if incremental['state'] != 'completed':
            raise ValueError('The incremental course must have completed')
        original, excluded, unsupported = dataset()
        published, errors = gsm('train')
        by_id = {row['id']:row for row in original+published}
        p = incremental['partitions']
        teaching_ids = p['initial_training'] + sum(p['batches'], [])
        teaching = [by_id[pid] for pid in teaching_ids]
        development = [by_id[pid] for pid in p['development']]
        followup = [by_id[pid] for pid in p['followup']]
        forbidden = {row['signature'] for row in teaching+development+followup}
        for problem in ET.fromstring((ROOT/'private/english-reasoning-20260907/ASDiv.xml').read_bytes()).findall('.//Problem'):
            if any(domain in problem.attrib['Source'] for domain in EXCLUDED):
                continue
            sig = signature(problem.findtext('Body')+' '+problem.findtext('Question'))
            if int(hashlib.sha256(sig.encode()).hexdigest()[:8], 16)%10 >= 8:
                forbidden.add(sig)
        extra = order([row for row in published if row['partition'] == 'train'
            and row['signature'] not in forbidden and len(row['indices']) == len(row['input'].numbers) == 3])[:240]
        teaching += extra
        assert not {row['signature'] for row in teaching} & {row['signature'] for row in development+followup}
        session.result['partitions'] = {name:[row['id'] for row in rows] for name, rows in
            (('teaching', teaching), ('extra_teaching', extra), ('development', development), ('asdiv_followup', followup))}
        session.result['admission'] = {'teaching':len(teaching), 'extra_teaching':len(extra),
            'development':len(development), 'asdiv_followup':len(followup),
            'gsm_training_annotation_failures':len(errors)}
        language_path = ROOT/'runs/incremental-english-20260907/model.json'
        session.result['language_artifact'] = {'bytes':language_path.stat().st_size,
            'sha256':hashlib.sha256(language_path.read_bytes()).hexdigest()}
        language = StreamingEnglishReasoner.load(language_path).router
        base = InquiryModel(language)
        registry = load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json', extended=True).registry
        session.present('Learn from real corrections',
            'Predict first. Then compare the proposed relationships with the original worked explanation.',
            f'{len(teaching)} published teaching questions',
            boxes=['Propose a calculation', 'Receive correction', 'Learn when to ask', 'Check new questions'], active=1, delay=2)
        examples, feedback = teaching_feedback(base, teaching, registry, session)
        session.result['teaching_feedback'] = feedback
        session.present('Learn the question decision',
            'Corrections teach which relationships warrant a question. The wording of the question is supplied by the interface.',
            f'{feedback["labels"].get("ask",0)} ask lessons; {feedback["labels"].get("answer",0)} answer lessons', active=2, delay=2)
        baseline = evaluate(base, development, registry, session)
        candidates = [{'depth':0, 'bytes':len(encoded(base.record())), 'development':baseline, 'learning_work':{}}]
        models = [base]
        for depth in (4, 8, 12):
            work = Work(check=session.check, limit=60_000_000)
            policy = PredicateTree(('answer', 'ask')).teach(examples, work, depth=depth, min_leaf=3)
            model = InquiryModel(language, policy)
            measured = evaluate(model, development, registry, session)
            candidates.append({'depth':depth, 'bytes':len(encoded(model.record())),
                'policy_nodes':len(policy.nodes), 'learning_work':work.counts, 'development':measured})
            models.append(model)
            session.present('Check whether the questions help',
                'Teacher-assisted answers are counted separately from independent answers. Harmful and unhelpful questions remain in the result.',
                f'Depth {depth}: {measured["after_correct"]}/{measured["total"]} after {measured["questions_asked"]} questions', active=2, delay=1)
        chosen = max(range(len(models)), key=lambda i:(
            10*candidates[i]['development']['after_correct']-candidates[i]['development']['questions_asked'],
            -candidates[i]['development']['questions_asked'], -candidates[i]['bytes']))
        model = models[chosen]
        session.result.update(candidates=candidates, selected_depth=candidates[chosen]['depth'])
        raw = encoded(model.record())
        (session.folder/'model.json').write_bytes(raw)
        session.result['artifact'] = {'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest(),
            'policy_bytes':len(encoded(model.policy.nodes)), 'language_nodes':len(language.nodes),
            'policy_nodes':len(model.policy.nodes)}
        session.present('Freeze the acquired question policy',
            'The saved artifact contains operation routes and question-decision routes. Teacher replies remain temporary input.',
            f'{len(raw):,} bytes; policy depth {candidates[chosen]["depth"]}', active=3, delay=2)
        official, test_errors = gsm('test')
        test = [row for row in official if 2 <= len(row['indices']) == len(row['input'].numbers) <= 3]
        session.result['admission']['gsm_followup'] = {'eligible':len(test), 'official_total':1319,
            'outside_selected_grammar':1319-len(test), 'annotation_failures':len(test_errors)}
        session.result['partitions']['gsm_followup'] = [row['id'] for row in test]
        session.result['followup'] = {}
        for name, rows in (('asdiv', followup), ('gsm', test)):
            session.result['followup'][name] = {}
            for mode in ('none', 'learned', 'always'):
                measured = evaluate(model, rows, registry, session, mode)
                session.result['followup'][name][mode] = measured
                session.present('Measure the questioning controls',
                    'The teacher supplies only the requested relation from the original solution, never the final answer.',
                    f'{name.upper()} {mode}: {measured["after_correct"]}/{measured["total"]}; {measured["questions_asked"]} questions', active=3, delay=.5)
        assert (session.folder/'model.json').read_bytes() == raw
        session.present('Questioning course completed',
            'The results distinguish learned asking, supplied question wording and answers that depended on a teacher.',
            'The frozen configuration and all failures are recorded.', active=3, delay=2)
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
