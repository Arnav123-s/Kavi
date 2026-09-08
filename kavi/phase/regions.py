"""Acquire bounded phase-region rules from supervised executions.

Intervals and the greedy covering procedure are supplied. Bounds and output ports
are learned. Inference checks conjunctions; it performs no nearest-example search.
"""

from dataclasses import replace
from .model import contains
from .runtime import PhaseActivity


def bind_regions(model, examples, work):
    labels = {}
    for events, port in examples:
        if type(port) is not int:
            raise ValueError('Teaching outcomes must be integer ports')
        run = PhaseActivity(model, work)
        for event in events:
            run.accept(event)
            if run.failed:
                return None
        if run.phases in labels and labels[run.phases] != port:
            return None
        labels[run.phases] = port
    rules = []
    for state, port in sorted(labels.items()):
        expanded = False
        for index, (box, output) in enumerate(rules):
            work.add('phase_region_merge_attempts')
            if output != port:
                continue
            candidate = tuple((min(lo, p), max(hi, p)) for (lo, hi), p in zip(box, state))
            conflict = False
            for other, expected in labels.items():
                work.add('phase_region_constraint_coordinates', len(other))
                if expected != port and contains(candidate, other):
                    conflict = True
                    break
            if not conflict:
                rules[index] = candidate, port
                expanded = True
                break
        if not expanded:
            rules.append((tuple((p, p) for p in state), port))
    # Intersections outside the teaching bank can still disagree. Runtime returns
    # unresolved for those states. Finite consistency is not a universal proof.
    return replace(model, outputs=tuple(rules))
