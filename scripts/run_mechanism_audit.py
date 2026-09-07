"""Visible, bounded tests of configuration reuse, repair and capability limits."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import time

from kavi.circuit_runtime import write_json
from kavi.configuration_composition import (COST_FIELDS, ArithmeticBridge, GraphCatalog,
    add_cost, fit_bridge, fit_graph)
from kavi.configuration_repair import redirect, repair
from kavi.finite_state_audit import compare
from kavi.grounded_language import LanguageModel
from kavi.procedure_core import ProcedureLibrary
from kavi.procedure_optimizations import addition_certificate
from kavi.recurrent_configuration import Configuration, learn
from kavi.trial_resources import memory_reading
from scripts.run_recurrent_configuration import ALPHABET, SEEDS, bank, sequences

ROOT = Path(__file__).resolve().parents[1]
EXPANDED = ALPHABET + ('α',)


def label(tokens):
    selected = 'a'
    for token in tokens:
        if token in ('?a', '?b'):
            selected = token[1:]
    return ((tokens.count('a') + tokens.count('α')) if selected == 'a'
            else tokens.count('b')) % 2


def reference(alphabet):
    states = list(itertools.product(range(2), range(2), range(2)))
    rows, outputs = [], []
    for a, b, selected in states:
        next_states = {'a': (1-a, b, selected), 'α': (1-a, b, selected),
                       'b': (a, 1-b, selected), '?a': (a, b, 0), '?b': (a, b, 1)}
        rows.append(tuple(states.index(next_states[s]) for s in alphabet))
        outputs.append(a if selected == 0 else b)
    return Configuration(tuple(alphabet), tuple(rows), tuple(outputs))


def evaluate(model, inputs, check):
    failures = []
    for tokens in inputs:
        observed = model.predict(tokens, check=check)
        expected = label(tokens)
        if observed != expected:
            failures.append({'tokens': list(tokens), 'observed': observed, 'expected': expected})
    return {'correct': len(inputs) - len(failures), 'total': len(inputs),
            'token_steps': sum(map(len, inputs)), 'failures': failures}


def rename(model, order):
    inverse = {old: new for new, old in enumerate(order)}
    return Configuration(model.alphabet, tuple(tuple(inverse[t] for t in model.transitions[old])
                         for old in order), tuple(model.outputs[old] for old in order))


def run(folder):
    if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    folder = folder.resolve()
    if folder.exists() or not folder.is_relative_to(ROOT / 'runs'):
        raise ValueError('Use a fresh directory inside runs')
    folder.mkdir(parents=True)
    started, cpu_started = time.monotonic(), time.process_time()
    next_check = pacing = 0.0
    rows = []
    result = {'state': 'running', 'protocol': 'docs/MECHANISM_AUDIT_PROTOCOL.md',
              'python': sys.version.split()[0], 'limits': {'seconds': 300,
              'worker_bytes': 512 * 1024**2, 'prefix_states': 21000,
              'merge_proposals_per_fit': 20000, 'repair_proposals_per_arm': 128}}
    current = {'state': 'running', 'phase': 'Preparing', 'message': '', 'rows': rows,
               'finished': 0, 'total': 25, 'model': None}

    def check():
        nonlocal next_check
        now = time.monotonic()
        if now < next_check:
            return
        next_check = now + .05
        if (folder / 'STOP').exists() or now - started >= 300:
            raise InterruptedError('Stopped or five-minute run budget exhausted')
        if (memory_reading().get('working_set_bytes') or 0) > 512 * 1024**2:
            raise InterruptedError('Worker memory limit exceeded')
        if (folder / 'PAUSE').exists():
            write_json(folder / 'status.json', dict(current, state='paused',
                       message='Paused. Resume continues; Stop ends the run.'))
            while (folder / 'PAUSE').exists():
                if (folder / 'STOP').exists() or time.monotonic() - started >= 300:
                    raise InterruptedError('Stopped or time exhausted while paused')
                time.sleep(.05)
            write_json(folder / 'status.json', current)

    def present(phase, message, *, evidence='', seed='', model=None, delay=.8):
        nonlocal pacing
        check()
        if evidence:
            rows.append({'lesson': phase, 'trial': seed, 'status': evidence})
        current.update(phase=phase, message=message, finished=len(rows))
        if model is not None:
            current['model'] = model.as_dict()
        write_json(folder / 'status.json', current)
        write_json(folder / 'results.json', result)
        with (folder / 'transcript.txt').open('a', encoding='utf-8') as handle:
            handle.write(f'{phase}: {message}\n{evidence}\n')
        if sys.stdout is not None:
            print(phase + ': ' + message, flush=True)
        before = time.monotonic()
        while time.monotonic() - before < delay:
            check()
            time.sleep(.05)
        pacing += time.monotonic() - before

    def save_model(name, model):
        raw = model.encoded()
        (folder / name).write_bytes(raw)
        return {'file': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

    try:
        old = Configuration.decode((ROOT / 'experiments/recurrent-20260907-model.json').read_bytes())
        foundation = Configuration.decode((ROOT / 'experiments/recurrent-20260907-foundation.json').read_bytes())
        library = ProcedureLibrary.load(ROOT / 'experiments/library-20260907-compiled.json')
        result['dependencies'] = {'base_library_bytes': len(library.encoded()),
                                  'base_library_digest': library.digest,
                                  'old_controller_bytes': len(old.encoded()),
                                  'foundation_controller_bytes': len(foundation.encoded())}
        present('Do the connections matter?', 'I will change one connection at a time, then check whether the answers change. Renaming a state should change nothing.', model=old)
        interventions = []
        for state, row in enumerate(old.transitions):
            for column, target in enumerate(row):
                for destination in range(len(old.outputs)):
                    if destination == target:
                        continue
                    audit = compare(old, redirect(old, state, column, destination), ALPHABET, check=check)
                    interventions.append({'state': state, 'token': old.alphabet[column],
                                          'target': destination, **audit})
        renamings = []
        for seed in range(10):
            order = list(range(1, len(old.outputs)))
            random.Random(seed).shuffle(order)
            renamings.append(compare(old, rename(old, [0] + order), ALPHABET, check=check))
        extra = Configuration(old.alphabet, old.transitions + ((8,) * 4,), old.outputs + (57,))
        commutations = {}
        for left, right in (('a', 'b'), ('?a', '?b')):
            lcol, rcol = old.alphabet.index(left), old.alphabet.index(right)
            commutations[left + ',' + right] = [q for q in range(8)
                if old.transitions[old.transitions[q][lcol]][rcol] == old.transitions[old.transitions[q][rcol]][lcol]]
        result['causal'] = {'interventions': interventions, 'renamings': renamings,
                           'unreachable_state': compare(old, extra, ALPHABET, check=check),
                           'commuting_states': commutations}
        changed = sum(not row['equivalent'] for row in interventions)
        present('Connections carry the rule', f'{changed} of 224 connection changes alter behavior. All ten renamings preserve it. State labels are not the knowledge.', evidence=f'{changed}/224 changes detected; 10/10 renamings retained')

        evidence = [(tokens, old.predict(tokens, check=check) if 'α' not in tokens else label(tokens))
                    for tokens in sequences(EXPANDED, 6)]
        write_json(folder / 'alias-teaching.json', evidence)
        result['alias'] = {'teaching_cases': len(evidence), 'old_cases': sum('α' not in t for t, _ in evidence), 'trials': []}
        alias_models = []
        for seed in SEEDS:
            present('Teach another spelling', 'Alpha is a new symbol. Only final answers are supplied. The learner must discover where its connections belong.', seed=seed)
            model, stats = learn(evidence, seed=seed, max_states=21000, max_merges=20000, check=check)
            alias_models.append(model)
            artifact = save_model(f'alias-{seed}.json', model)
            result['alias']['trials'].append({'seed': seed, 'learning': stats, 'artifact': artifact})
            present('New notation acquired', f'Trial {seed} produced {len(model.outputs)} states. The model is frozen before the new questions.', seed=seed,
                    model=model, evidence=f'{len(model.outputs)} states; {len(model.encoded())} bytes')
        final_inputs = bank(EXPANDED, 94001, 13, 64, 128)
        write_json(folder / 'alias-final.json', final_inputs)
        for model, trial in zip(alias_models, result['alias']['trials']):
            a, alpha = model.alphabet.index('a'), model.alphabet.index('α')
            trial.update(final=evaluate(model, final_inputs, check),
                         old_retention=compare(old, model, ALPHABET, check=check),
                         whole_task=compare(reference(EXPANDED), model, EXPANDED, check=check),
                         shared_destinations=sum(row[a] == row[alpha] for row in model.transitions))
        controller = alias_models[0]
        passed = sum(row['final']['correct'] == 128 for row in result['alias']['trials'])
        present('Check new streams', f'{passed} of three frozen trials answered all 128 new streams. Exact graph checks also test every finite stream in the declared task.', evidence=f'{passed}/3 trials pass the new stream bank', model=controller)

        ambiguous = [((), (2, 2), 4), (('a',), (2, 2), 4)]
        bridge, initial_stats = fit_bridge(controller, ambiguous, library, check=check)
        first_answers = [bridge.answer(tokens, (2, 3), library, check=check) for tokens in ((), ('a',))]
        present('A connection is still uncertain', 'With two and two, both adding and multiplying give four. Kavi keeps both choices open.', evidence=', '.join(row['state'] for row in first_answers))
        bridge_examples = ambiguous + [((), (2, 3), 5), (('a',), (2, 3), 6)]
        write_json(folder / 'bridge-teaching.json', bridge_examples)
        bridge, fit_stats = fit_bridge(controller, bridge_examples, library, check=check)
        artifact = save_model('arithmetic-bridge.json', bridge)
        bridge = ArithmeticBridge.decode(bridge.encoded())
        rng = random.Random(94002)
        bridge_inputs = [(tuple(rng.choice(EXPANDED) for _ in range(rng.randint(13, 64))),
                          (rng.randint(0, 1000000), rng.randint(0, 1000000))) for _ in range(128)]
        bridge_rows, bridge_cost = [], {}
        for tokens, args in bridge_inputs:
            response = bridge.answer(tokens, args, library, check=check)
            expected = args[0] + args[1] if label(tokens) == 0 else args[0] * args[1]
            bridge_rows.append({'tokens': list(tokens), 'args': list(args), 'expected': expected, **response})
            for key in COST_FIELDS:
                bridge_cost[key] = bridge_cost.get(key, 0) + response.get(key, 0)
        write_json(folder / 'bridge-final.json', bridge_rows)
        result['bridge'] = {'initial_fit': initial_stats, 'initial_answers': first_answers,
                            'corrected_fit': fit_stats, 'artifact': artifact,
                            'choices': bridge.choices, 'final_correct': sum(r.get('value') == r['expected'] for r in bridge_rows),
                            'final_total': 128, 'final_cost': bridge_cost,
                            'final_controller_steps': sum(len(tokens) for tokens, _ in bridge_inputs),
                            'unknown_input': bridge.answer(('unknown',), (2, 3), library, check=check)}
        present('Feedback connects old skills', 'Different examples resolve the choice. The token configuration now selects an acquired arithmetic procedure.',
                evidence=f"{result['bridge']['final_correct']}/128 new numerical answers")

        teaching = [((2, 3), 25), ((1, 4), 25), ((0, 3), 9), ((4, 2), 36)]
        write_json(folder / 'composition-teaching.json', teaching)
        present('Build a new computation', 'Try small configurations made from acquired addition, subtraction and multiplication. Reuse intermediate results. Keep candidates that match the four examples.')
        graph, fit_stats = fit_graph(teaching, library, check=check)
        result['composition'] = {'search': fit_stats, 'selected_graph': graph.as_dict() if graph else None}
        if graph is None:
            raise RuntimeError('No composed configuration satisfies the teaching examples')
        rng = random.Random(94005)
        promotion = [((x := rng.randrange(1001), y := rng.randrange(1001)), (x+y)**2) for _ in range(48)]
        write_json(folder / 'composition-promotion.json', promotion)
        catalog, promotion_stats = GraphCatalog(library.digest).admit('relation_01', graph, promotion, library, check=check)
        artifact = save_model('composed-catalog.json', catalog)
        catalog = GraphCatalog.decode(catalog.encoded())
        rng = random.Random(94006)
        final_rows, cost = [], {}
        for _ in range(128):
            x, y = rng.randrange(1000001), rng.randrange(1000001)
            execution = catalog.execute('relation_01', (x, y), library, check=check)
            add_cost(cost, execution)
            final_rows.append({'args': [x, y], 'expected': (x+y)**2, 'observed': execution.value})
        write_json(folder / 'composition-final.json', final_rows)
        retention_rows, retention_cost = [], {}
        for name, procedure in library.procedures.items():
            for _ in range(8):
                args = tuple(rng.randrange(6) for _ in range(procedure.arity))
                if procedure.contract in ('ordered_pair', 'ordered_prefix') and args[0] < args[1]:
                    args = (args[1], args[0], *args[2:])
                earlier = library.execute(name, args, check=check)
                newer = catalog.execute(name, args, library, check=check)
                add_cost(retention_cost, earlier)
                add_cost(retention_cost, newer)
                retention_rows.append({'name': name, 'args': args, 'old': earlier.value, 'new': newer.value})
        write_json(folder / 'composition-retention.json', retention_rows)
        result['composition'].update(promotion=promotion_stats, artifact=artifact,
            final_correct=sum(r['observed'] == r['expected'] for r in final_rows), final_total=128,
            final_cost=cost, old_checks=len(retention_rows), old_correct=sum(r['old'] == r['new'] for r in retention_rows),
            retention_cost=retention_cost)
        present('Admit the new configuration', 'The candidate passed a separate promotion bank. It has been saved beside the original skills, with their exact dependency version retained.',
                evidence=f"{result['composition']['final_correct']}/128 new inputs; {result['composition']['old_correct']}/{len(retention_rows)} earlier checks")

        development = [(tokens, label(tokens)) for tokens in bank(ALPHABET, 94003, 5, 12, 128)]
        write_json(folder / 'repair-development.json', development)
        result['repair'] = {'cases': [], 'development_cases': len(development)}
        final_models = []
        for (state, token), seed in zip(((0, '?b'), (2, '?b'), (3, '?a')), SEEDS):
            column = old.alphabet.index(token)
            damaged = redirect(old, state, column, (old.transitions[state][column] + 2) % 8)
            case = {'fault_state': state, 'fault_token': token, 'seed': seed, 'arms': []}
            result['repair']['cases'].append(case)
            for priority, heated in itertools.product((False, True), repeat=2):
                arm = ('priority' if priority else 'uniform') + (' heated' if heated else ' greedy')
                present('Compare ways to search', f'Case {seed}: {arm}. A candidate must keep the old skill. Temperature may help explore a temporarily worse candidate; it cannot bypass that rule.', model=damaged, delay=.25)
                candidate, stats = repair(damaged, development, foundation, ('a', 'b'), seed=seed,
                                          priority=priority, heated=heated, check=check)
                name = f'repair-{seed}-{arm.replace(" ", "-")}.json'
                record = {'arm': arm, 'search': stats, 'artifact': save_model(name, candidate)}
                case['arms'].append(record)
                final_models.append((candidate, record))
                present('Search result recorded', f'{arm} leaves {stats["best_errors"]} errors on the development bank. Fresh evaluation comes after every search is frozen.', seed=seed,
                        evidence=f'{arm}: {stats["proposals"]} proposals; {stats["best_errors"]} development errors', model=candidate, delay=.25)
            candidate, stats = repair(damaged, development, foundation, ('a', 'b'), budget=224,
                                      exhaustive=True, check=check)
            record = {'arm': 'exhaustive one-edge', 'search': stats,
                      'artifact': save_model(f'repair-{seed}-exhaustive.json', candidate)}
            case['arms'].append(record)
            final_models.append((candidate, record))
            present('Close the small repair gap', 'Check every single-connection replacement from the damaged model. This covers 224 candidates, not every possible new brain.', seed=seed,
                    evidence=f'224 candidates; {stats["best_errors"]} development errors', model=candidate)
        repair_final = bank(ALPHABET, 94004, 13, 64, 128)
        write_json(folder / 'repair-final.json', repair_final)
        for candidate, record in final_models:
            record.update(final=evaluate(candidate, repair_final, check),
                          whole_task=compare(reference(ALPHABET), candidate, ALPHABET, check=check),
                          old_retention=compare(foundation, candidate, ('a', 'b'), check=check))

        circuit = library.procedures['add'].circuit
        certificate = addition_certificate(circuit)
        pairs = [(0, 0), (1, 1), (255, 1), (2**64-1, 1), (2**128-1, 2**127),
                 (2**512, 2**511), (2**1024-1, 1), (2**2048-1, 2**2048-1),
                 (2**4095, 2**4095), (2**4096-1, 1)]
        additions = []
        for x, y in pairs:
            check()
            execution = circuit.execute(x, y)
            additions.append({'left_bits': x.bit_length(), 'right_bits': y.bit_length(),
                              'correct': execution.value == x+y, 'output_bits': execution.value.bit_length(),
                              'frames': execution.frames, 'gates': execution.gate_evaluations})
        try:
            circuit.execute(2**4096, 1)
            above_limit = 'incorrectly accepted'
        except ValueError:
            above_limit = 'rejected'
        natural = ProcedureLibrary.load(ROOT / 'experiments/foundation-natural-20260907.json')
        language = LanguageModel.load(ROOT / 'experiments/foundation-language-20260907.json')
        known = [('what is 27 plus 38', 65), ('what is 13 times 17', 221),
                 ('cube of 7', 343), ('twice kinetic energy for mass 7 and speed 11', 847),
                 ('position after speed 3 time 7 starting at 11', 32), ('force for mass 7 and acceleration 9', 63)]
        unsupported = ['Prove that there are infinitely many prime numbers',
                       'Derive the derivative of sine from first principles',
                       'Explain why orbital motion conserves angular momentum',
                       'Interpret the conflict between duty and love in Antigone',
                       'Compare Confucius and Aristotle on moral education',
                       'Write a new poem about rain and memory']
        probes = [{'question': q, 'expected': expected, 'response': language.answer(q, natural, check=check)} for q, expected in known]
        probes += [{'question': q, 'response': language.answer(q, natural, check=check)} for q in unsupported]
        result['boundaries'] = {'certificate_rows': certificate, 'large_additions': additions,
                                'above_limit_input': above_limit, 'language_probes': probes}
        correct = sum(p['response'].get('value') == p['expected'] for p in probes if 'expected' in p)
        absent = sum(p['response']['state'] == 'unsupported' for p in probes if 'expected' not in p)
        present('Check what it can actually do', f'{correct} of six supported calculation questions worked. {absent} of six broad reasoning and writing requests were unsupported. The addition certificate and ten large cases were checked separately.',
                evidence=f'{correct}/6 calculation probes; {absent}/6 broader requests unsupported', model=controller)
        result['state'] = 'completed'
        current.update(state='completed', phase='Audit complete',
                       message='All scheduled tests finished. This is evidence about specific skills and search methods; broad language understanding and graduate mastery remain unproven.')
    except Exception as error:
        result.update(state='stopped' if isinstance(error, InterruptedError) else 'failed',
                      error=type(error).__name__ + ': ' + str(error))
        current.update(state=result['state'], phase='Run ended', message=result['error'])
        import traceback
        (folder / 'error.txt').write_text(traceback.format_exc(), encoding='utf-8')
    finally:
        result['resources'] = {'wall_seconds': time.monotonic()-started,
            'cpu_seconds': time.process_time()-cpu_started, 'visual_pacing_seconds': pacing,
            'worker': memory_reading(), 'gui_memory': 'separate process; not included in worker peak'}
        write_json(folder / 'results.json', result)
        write_json(folder / 'status.json', current)
        files = [p for p in folder.iterdir() if p.is_file() and p.name != 'storage.json']
        write_json(folder / 'storage.json', {'bytes': sum(p.stat().st_size for p in files),
                   'files': len(files), 'scope': 'All completed run files except this storage census.'})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('run', 'watch'))
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'watch':
        from scripts.recurrent_window import show
        show(args.run_dir, runner=['scripts.run_mechanism_audit', 'run'],
             heading='Can Kavi reuse and improve its configurations?',
             subtitle='New notation • connected skills • new computations • repair comparisons',
             intro='Watch the plain-language results below. Earlier skills must survive; new questions are held back until learning ends.',
             legend='a / α: an event in stream a\nb: an event in stream b\n?a / ?b: select a stream\n0 / 1: even / odd count\n\nThe same graph can select arithmetic.\nNew graphs can reuse old arithmetic.\nSearch methods are compared fairly.')
    else:
        outcome = run(args.run_dir)
        if outcome['state'] != 'completed':
            sys.exit(1)


if __name__ == '__main__':
    main()
