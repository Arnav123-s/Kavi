"""Teach and audit learned recurrence and whole-configuration replacement."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kavi.circuit_runtime import write_json
from kavi.finite_state_audit import compare
from kavi.recurrent_configuration import Configuration, learn, prefix_configuration
from kavi.trial_resources import memory_reading

SEEDS = (7, 19, 43)
ALPHABET = ('a', 'b', '?a', '?b')


def sequences(alphabet, maximum):
    for length in range(maximum + 1):
        yield from itertools.product(alphabet, repeat=length)


def label(tokens):
    """Teacher: count events; the latest selector chooses a count's parity."""
    selected = 'a'
    for token in tokens:
        if token in ('?a', '?b'):
            selected = token[1:]
    return tokens.count(selected) % 2


def reference():
    """Independent evaluator, constructed only after the candidates freeze."""
    states = list(itertools.product(range(2), range(2), range(2)))
    transitions, outputs = [], []
    for a, b, selected in states:
        transitions.append(tuple(states.index(next_state) for next_state in (
            (1-a, b, selected), (a, 1-b, selected), (a, b, 0), (a, b, 1))))
        outputs.append(a if selected == 0 else b)
    return Configuration(ALPHABET, tuple(transitions), tuple(outputs))


def bank(alphabet, seed, low, high, count=256):
    rng = random.Random(seed)
    rows = set()
    while len(rows) < count:
        rows.add(tuple(rng.choice(alphabet) for _ in range(rng.randint(low, high))))
    return sorted(rows, key=lambda tokens: (len(tokens), tokens))


def evaluate(model, rows, check):
    correct = unresolved = 0
    failures = []
    for tokens in rows:
        check()
        prediction = model.predict(tokens, check=check)
        expected = label(tokens)
        correct += prediction == expected
        unresolved += prediction is None
        if prediction != expected:
            failures.append({'tokens': list(tokens), 'prediction': prediction, 'expected': expected})
    return {'correct': correct, 'total': len(rows), 'unresolved': unresolved, 'failures': failures}


def run(folder, *, coverage_repair=False):
    if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    folder = folder.resolve()
    if folder.exists() or not folder.is_relative_to(ROOT / 'runs'):
        raise ValueError('Use a fresh directory inside runs')
    folder.mkdir(parents=True)
    teaching_depth = 6 if coverage_repair else 4
    prefix_limit = 6000 if coverage_repair else 2000
    started = time.monotonic()
    cpu_started = time.process_time()
    next_memory_check = started
    pacing_seconds = 0.0
    memory = memory_reading()
    rows = []
    result = {'state': 'running', 'protocol': 'docs/RECURRENT_CONFIGURATION_PROTOCOL.md',
              'condition': 'coverage-repair' if coverage_repair else 'initial',
              'seeds': list(SEEDS), 'trials': [], 'python': sys.version.split()[0],
              'limits': {'seconds': 300, 'working_set_bytes': 512 * 1024**2,
                         'prefix_states': prefix_limit, 'merge_proposals_per_call': 20000,
                         'repair_rounds': 12, 'labels_per_round': 12},
              'scope': 'Finite token-stream classification; supplied state-merging learner.'}
    current = {'state': 'running', 'phase': 'Starting', 'message': '', 'rows': rows,
               'finished': 0, 'total': 24, 'model': None}

    def check():
        nonlocal next_memory_check, memory
        now = time.monotonic()
        if (folder / 'STOP').exists():
            raise InterruptedError('Stop requested')
        if now - started >= 300:
            raise InterruptedError('Five-minute run budget exhausted')
        if now >= next_memory_check:
            memory = memory_reading()
            next_memory_check = now + 0.5
            if (memory.get('working_set_bytes') or 0) > 512 * 1024**2:
                raise InterruptedError('Worker memory limit exceeded')
        if (folder / 'PAUSE').exists():
            paused = dict(current, state='paused', message='Paused. Resume continues; Stop ends the run.')
            write_json(folder / 'status.json', paused)
            while (folder / 'PAUSE').exists():
                if (folder / 'STOP').exists() or time.monotonic() - started >= 300:
                    raise InterruptedError('Stopped or time exhausted while paused')
                time.sleep(0.05)
            write_json(folder / 'status.json', current)

    def present(phase, message, *, model=None, seed='', evidence='', delay=1.2, trace=None):
        nonlocal pacing_seconds
        check()
        if evidence:
            rows.append({'lesson': phase, 'trial': seed, 'arm': 'learned configuration', 'status': evidence})
        current.update(phase=phase, message=message, finished=len(rows), rows=rows,
                       model=model.as_dict() if model else current['model'], trace=trace)
        write_json(folder / 'status.json', current)
        if sys.stdout is not None:
            print(phase + ': ' + message, flush=True)
        before = time.monotonic()
        while time.monotonic() - before < delay:
            check()
            time.sleep(0.05)
        pacing_seconds += time.monotonic() - before

    def fit(evidence, seed, name, trial):
        model, stats = learn(evidence, seed=seed, max_states=prefix_limit, check=check)
        stats.update(stage=name, teaching_sequences=len(evidence),
                     evidence_bytes=len(json.dumps(evidence, separators=(',', ':')).encode('utf-8')))
        trial['fits'].append(stats)
        write_json(folder / f'{seed}-{name}-evidence.json', evidence)
        (folder / f'{seed}-{name}-model.json').write_bytes(model.encoded())
        return model

    try:
        development = bank(ALPHABET, 11311, 5, 12)
        write_json(folder / 'development-bank.json', development)
        for seed in SEEDS:
            trial = {'seed': seed, 'fits': [], 'repair_rounds': []}
            result['trials'].append(trial)
            ambiguous_evidence = [((), 0), (('b',), 0), (('a', 'a'), 0)]
            ambiguous = fit(ambiguous_evidence, seed, 'ambiguous', trial)
            trial['before_feedback'] = {'tokens': ['a'], 'prediction': ambiguous.predict(('a',)), 'expected': 1}
            present('A missing distinction', 'The first three examples all end in zero. The current graph also says zero for a; that answer is wrong.',
                    model=ambiguous, seed=seed, evidence=f"a → {trial['before_feedback']['prediction']}; expected 1")
            corrected = fit(ambiguous_evidence + [(('a',), 1)], seed, 'one-correction', trial)
            present('One correction', 'Teach a → 1. The learner changes connections using the examples; it receives no target graph.',
                    model=corrected, seed=seed, evidence=f'{len(corrected.outputs)} states')
            if coverage_repair:
                corrected_twice = fit(ambiguous_evidence + [(('a',), 1), (('a', 'b'), 1)],
                                      seed, 'two-corrections', trial)
                present('Correct the missing continuation', 'One correction left ab unresolved. Teach ab → 1, then test whether the same repaired loop works on longer streams.',
                        model=corrected_twice, seed=seed, evidence=f'{len(corrected_twice.outputs)} states')
            foundation_evidence = [(tokens, label(tokens)) for tokens in sequences(('a', 'b'), 4)]
            foundation = fit(foundation_evidence, seed, 'foundation', trial)
            foundation_control = prefix_configuration(foundation_evidence, check=check)
            present('Reuse the same states', 'Teach 31 short streams. Folding compatible histories can create loops that handle much longer streams.',
                    model=foundation, seed=seed, evidence=f'{len(foundation_control.outputs)} → {len(foundation.outputs)} states')

            # Preserve behavior via the old configuration, not its stored lessons.
            obligations = [(tokens, foundation.predict(tokens, check=check))
                           for tokens in sequences(('a', 'b'), teaching_depth)]
            new_evidence = [(tokens, label(tokens)) for tokens in sequences(ALPHABET, teaching_depth)
                            if '?a' in tokens or '?b' in tokens]
            successor_evidence = obligations + new_evidence
            trial['old_obligations'] = len(obligations)
            trial['new_labeled_sequences'] = len(new_evidence)
            successor = fit(successor_evidence, seed, 'late-evidence', trial)
            present('Learn a later instruction', 'Now ?b means read the b stream, even when it arrives after the events. Earlier answers come from the old graph; new lessons build one replacement graph.',
                    model=successor, seed=seed, evidence=f'{len(successor.outputs)} states')
            for round_index in range(12):
                assessment = evaluate(successor, development, check)
                if not assessment['failures']:
                    break
                additions = assessment['failures'][:12]
                trial['repair_rounds'].append({'round': round_index + 1,
                                              'before_feedback': assessment, 'teaching': additions})
                successor_evidence.extend((tuple(row['tokens']), row['expected']) for row in additions)
                successor = fit(successor_evidence, seed, f'repair-{round_index+1}', trial)
                present('Correct development errors', 'These answers were scored before feedback. Their corrected labels now constrain a new configuration.',
                        model=successor, seed=seed, evidence=f"{assessment['correct']}/256 before repair {round_index+1}")
            trial['development_after'] = evaluate(successor, development, check)
            successor_control = prefix_configuration(successor_evidence, max_states=prefix_limit, check=check)

            models = {'ambiguous': ambiguous, 'one-correction': corrected, 'foundation': foundation,
                      'successor': successor, 'foundation-prefix': foundation_control,
                      'successor-prefix': successor_control}
            if coverage_repair:
                models['two-corrections'] = corrected_twice
            frozen = {name: graph.encoded() for name, graph in models.items()}
            for name, raw in frozen.items():
                (folder / f'{seed}-frozen-{name}.json').write_bytes(raw)
            trial['frozen_hashes'] = {name: hashlib.sha256(raw).hexdigest() for name, raw in frozen.items()}
            present('Freeze before the final exam', 'Learning is finished for this trial. Fresh test answers and the exact audit cannot alter these saved graphs.',
                    model=successor, seed=seed, evidence='frozen')
            parity_final = bank(('a', 'b'), 90003 if coverage_repair else 90001, 13, 64)
            late_final = bank(ALPHABET, 90004 if coverage_repair else 90002, 13, 64)
            write_json(folder / 'final-parity-bank.json', parity_final)
            write_json(folder / 'final-late-bank.json', late_final)
            trial['final'] = {name: evaluate(graph, late_final if name.startswith('successor') else parity_final, check)
                              for name, graph in models.items()}
            exact_reference = reference()
            parity_reference = Configuration(('a', 'b'), ((1, 0), (0, 1)), (0, 1))
            trial['exact'] = {'correction': compare(corrected, parity_reference, ('a', 'b'), check=check),
                              'foundation': compare(foundation, parity_reference, ('a', 'b'), check=check),
                              'retention': compare(foundation, successor, ('a', 'b'), check=check),
                              'new_task': compare(successor, exact_reference, ALPHABET, check=check)}
            if coverage_repair:
                trial['exact']['two-corrections'] = compare(corrected_twice, parity_reference, ('a', 'b'), check=check)
            trial['model_bytes'] = {name: len(raw) for name, raw in frozen.items()}
            trial['state_counts'] = {name: len(graph.outputs) for name, graph in models.items()}
            trial['frozen_unchanged'] = all(graph.encoded() == frozen[name] for name, graph in models.items())
            present('Fresh longer inputs', 'The exam uses streams of 13–64 tokens. The prefix control has the same teaching data but cannot fold histories into cycles.',
                    model=successor, seed=seed,
                    evidence=f"new task {trial['final']['successor']['correct']}/256; prefix {trial['final']['successor-prefix']['correct']}/256")
            retained = trial['exact']['retention']['equivalent']
            present('Check every earlier stream', 'An independent comparison checks all reachable old/new state pairs under a and b. This covers every finite stream in that old domain.',
                    model=successor, seed=seed, evidence='retained exactly' if retained else 'retention failed')
            demo_tokens = tuple('a b a a ?b b ?a b ?b'.split())
            trial['demonstration'] = {'tokens': list(demo_tokens), 'trace': successor.trace(demo_tokens)}
            if seed == SEEDS[-1]:
                for index, step in enumerate(trial['demonstration']['trace']):
                    explanation = (f"Read {step['token']}: state {step['from']} → {step['to']}. "
                                   f"Current answer: {step['output']}. " +
                                   ('This state has been used earlier in this stream.' if step['revisit'] else ''))
                    present('Watch one stream flow', explanation, model=successor, delay=0.7,
                            trace={'tokens': list(demo_tokens), 'index': index, 'step': step})
            write_json(folder / 'results.json', result)

        result['state'] = 'completed'
        result['criteria'] = {
            'correction_transfers': all(t['final']['two-corrections' if coverage_repair else 'one-correction']['correct'] > t['final']['ambiguous']['correct'] for t in result['trials']),
            'folding_beats_prefix': all(t['final']['successor']['correct'] > t['final']['successor-prefix']['correct'] for t in result['trials']),
            'late_selection_exact': all(t['exact']['new_task']['equivalent'] for t in result['trials']),
            'old_domain_retained_exactly': all(t['exact']['retention']['equivalent'] for t in result['trials']),
            'frozen_models_unchanged': all(t['frozen_unchanged'] for t in result['trials'])}
    except Exception as error:
        result.update(state='stopped' if isinstance(error, InterruptedError) else 'failed',
                      error=f'{type(error).__name__}: {error}')
    result.update(seconds=time.monotonic() - started, ui_pacing_seconds=pacing_seconds,
                  worker_cpu_seconds=time.process_time() - cpu_started,
                  resources=memory_reading(),
                  external_bytes_before_final_results=sum(path.stat().st_size for path in folder.rglob('*') if path.is_file()),
                  unavailable=['CPU temperature', 'energy use', 'GUI process memory', 'per-object Python heap peak'])
    result['work'] = {key: sum(fit[key] for t in result['trials'] for fit in t['fits'])
                      for key in ('proposed_merges', 'accepted_merges', 'rejected_merges',
                                  'closure_pairs', 'copied_transition_cells', 'seconds')}
    write_json(folder / 'results.json', result)
    passed = sum(result.get('criteria', {}).values())
    current.update(state=result['state'], phase='Experiment finished',
                   finished=len(rows), total=max(24, len(rows)),
                   message=(f'{passed}/5 declared criteria passed. Results include the initial wrong answer, controls and exact retention checks. The graph remains available for inspection.'
                            if result['state'] == 'completed' else
                            f"Run ended before completing the evaluation. {result.get('error', '')}"))
    write_json(folder / 'status.json', current)
    return 0 if result['state'] == 'completed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'live', 'repair-run', 'repair-live'))
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.mode in ('live', 'repair-live'):
        from scripts.recurrent_window import show
        show(args.run_dir, coverage_repair=args.mode == 'repair-live')
        return 0
    return run(args.run_dir, coverage_repair=args.mode == 'repair-run')


if __name__ == '__main__':
    raise SystemExit(main())
