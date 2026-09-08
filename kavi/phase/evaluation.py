"""Frozen complete-input evaluation; no teacher or proposal generator is called."""

import hashlib
from ..composable_configurations import encoded


def evaluate(generation, examples, work):
    fingerprint = hashlib.sha256(encoded(generation.record())).hexdigest()
    total = correct = unresolved = 0
    for events, expected in examples:
        if type(expected) is not int:
            raise ValueError('Evaluation outcomes must be integer ports')
        prediction = generation.circuit.predict(events, work)
        total += 1
        correct += prediction == expected
        unresolved += prediction is None
        work.add('phase_evaluation_cases')
    unchanged = hashlib.sha256(encoded(generation.record())).hexdigest() == fingerprint
    if not unchanged:
        raise RuntimeError('Frozen evaluation changed the circuit')
    return {'total': total, 'correct': correct, 'unresolved': unresolved,
            'wrong': total-correct-unresolved, 'model_sha256': fingerprint,
            'frozen_unchanged': unchanged}
