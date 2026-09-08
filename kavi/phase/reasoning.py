"""Bounded assignment search using learned connective evaluations."""

from itertools import product
from .logic import evaluate_formula


def models(circuit, premises, variables, work):
    variables = tuple(variables)
    if (len(variables) > 12 or len(set(variables)) != len(variables)
            or any(type(v) is not str or not v for v in variables)):
        raise ValueError('Invalid finite variable domain')
    premises = tuple(premises)
    solutions, unresolved = [], 0
    for bits in product((0, 1), repeat=len(variables)):
        work.add('logic_assignments')
        assignment = dict(zip(variables, bits))
        values = [evaluate_formula(circuit, p, assignment, work) for p in premises]
        if 0 in values:
            continue
        if None in values:
            unresolved += 1
        else:
            solutions.append(assignment)
    return {'solutions': solutions, 'unresolved_assignments': unresolved,
            'complete': unresolved == 0}
