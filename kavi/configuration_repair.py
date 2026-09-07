"""Finite structural search with an exact old-domain retention constraint."""

import math
import random

from .finite_state_audit import compare
from .recurrent_configuration import Configuration


def redirect(model, state, column, target):
    rows = list(model.transitions)
    row = list(rows[state])
    row[column] = target
    rows[state] = tuple(row)
    return Configuration(model.alphabet, tuple(rows), model.outputs)


def assess(model, examples, *, check=lambda: None):
    """Score every example and count traversals, including failed-path priority."""
    width = len(model.alphabet)
    weights = [1] * (len(model.outputs) * width)
    columns = {token: i for i, token in enumerate(model.alphabet)}
    errors = steps = priority_steps = 0
    for tokens, expected in examples:
        state, path = 0, []
        for token in tokens:
            check()
            column = columns.get(token)
            if state < 0 or column is None:
                state = -1
                break
            edge = state * width + column
            path.append(edge)
            state = model.transitions[state][column]
            steps += 1
        observed = model.outputs[state] if state >= 0 else None
        if observed != expected:
            errors += 1
            for edge in path:
                weights[edge] += 1
                priority_steps += 1
    return {'errors': errors, 'total': len(examples), 'token_steps': steps,
            'priority_steps': priority_steps, 'weights': weights}


def acceptance_probability(delta, temperature, reverse_forward=1.0):
    if temperature <= 0 or reverse_forward <= 0:
        raise ValueError('Positive temperature and proposal ratio are required')
    return math.exp(min(0.0, delta / temperature + math.log(reverse_forward)))


def repair(start, examples, old_model, old_alphabet, *, seed=7, budget=128,
           priority=False, heated=False, exhaustive=False, check=lambda: None):
    examples = list(examples)
    if not examples or not 0 <= budget <= 10000:
        raise ValueError('Examples and a finite nonnegative search budget are required')
    initial_retention = compare(old_model, start, old_alphabet, check=check)
    if not initial_retention['equivalent']:
        raise ValueError('Starting configuration fails the old-domain contract')
    width, size = len(start.alphabet), len(start.outputs)
    if size < 2 or width < 1 or any(t < 0 for row in start.transitions for t in row):
        raise ValueError('Repair requires a complete graph with at least two states')
    stats = {'proposals': 0, 'retention_rejections': 0, 'accepted': 0,
             'accepted_worse': 0, 'score_calls': 0, 'token_steps': 0,
             'priority_steps': 0, 'retention_audits': 1,
             'retention_pairs': initial_retention['visited_pairs'], 'history': []}

    def score(model):
        result = assess(model, examples, check=check)
        stats['score_calls'] += 1
        stats['token_steps'] += result['token_steps']
        stats['priority_steps'] += result['priority_steps']
        return result

    current, current_score = start, score(start)
    best, best_score = current, current_score
    stats['initial_errors'] = current_score['errors']
    rng = random.Random(seed)
    if exhaustive:
        proposals = [(state, column, target) for state in range(size)
                     for column in range(width) for target in range(size)
                     if target != start.transitions[state][column]]
        if len(proposals) > budget:
            raise ValueError('Exhaustive neighborhood exceeds the proposal budget')
    else:
        proposals = [None] * budget
    for index, fixed in enumerate(proposals):
        check()
        if best_score['errors'] == 0 and not exhaustive:
            break
        origin = start if exhaustive else current
        if fixed is None:
            edge = (rng.choices(range(size * width), weights=current_score['weights'])[0]
                    if priority else rng.randrange(size * width))
            state, column = divmod(edge, width)
            targets = [t for t in range(size) if t != origin.transitions[state][column]]
            target = rng.choice(targets)
        else:
            state, column, target = fixed
            edge = state * width + column
        candidate = redirect(origin, state, column, target)
        stats['proposals'] += 1
        retention = compare(old_model, candidate, old_alphabet, check=check)
        stats['retention_audits'] += 1
        stats['retention_pairs'] += retention['visited_pairs']
        if not retention['equivalent']:
            stats['retention_rejections'] += 1
            continue
        candidate_score = score(candidate)
        delta = (current_score['errors'] - candidate_score['errors']) / len(examples)
        if heated and not exhaustive:
            temperature = .15 * (.005 / .15) ** (index / max(1, budget - 1))
            ratio = ((candidate_score['weights'][edge] / sum(candidate_score['weights'])) /
                     (current_score['weights'][edge] / sum(current_score['weights']))) if priority else 1.0
            accepted = rng.random() < acceptance_probability(delta, temperature, ratio)
        else:
            accepted = candidate_score['errors'] <= current_score['errors']
        if accepted and not exhaustive:
            stats['accepted'] += 1
            stats['accepted_worse'] += delta < 0
            current, current_score = candidate, candidate_score
        if candidate_score['errors'] < best_score['errors']:
            best, best_score = candidate, candidate_score
            stats['history'].append({'proposal': index + 1, 'errors': best_score['errors']})
    stats['best_errors'] = best_score['errors']
    stats['best_model_bytes'] = len(best.encoded())
    return best, stats
