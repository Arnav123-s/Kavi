"""Learn discrete component-routing rules from past executable programs.

Probes and tree induction are supplied. Branches and leaf component sets are
fitted from experience; finite probe agreement is not a polynomial proof.
"""

from itertools import combinations
import json


def probe_inputs(arity):
    if arity not in (1, 2, 3):
        raise ValueError('Use one through three inputs')
    points = {(0,) * arity, (1,) * arity}
    for axis in range(arity):
        for value in range(5):
            xs = [1] * arity
            xs[axis] = value
            points.add(tuple(xs))
    for left, right in combinations(range(arity), 2):
        xs = [1] * arity
        xs[left] = xs[right] = 2
        points.add(tuple(xs))
    return sorted(points)


def signature(arity, observations):
    required = probe_inputs(arity)
    if not all(xs in observations and type(observations[xs]) is int for xs in required):
        raise ValueError('Missing exact probe observations')
    degrees = []
    for axis in range(arity):
        values = []
        for value in range(5):
            xs = [1] * arity
            xs[axis] = value
            values.append(observations[tuple(xs)])
        degree = 0
        for order in range(1, 5):
            values = [b - a for a, b in zip(values, values[1:])]
            if any(values):
                degree = order
        degrees.append(degree)
    mixed = 0
    for left, right in combinations(range(arity), 2):
        both, a, b = [1] * arity, [1] * arity, [1] * arity
        both[left] = both[right] = a[left] = b[right] = 2
        mixed += int(observations[tuple(both)] - observations[tuple(a)]
                     - observations[tuple(b)] + observations[(1,) * arity] != 0)
    # Sorting exposes input-permutation invariance to the selector only.
    return (arity, *sorted(degrees + [-1] * (3 - arity)), mixed,
            int(observations[(0,) * arity] != 0))


def called_components(body):
    names = set()
    if body[0] == 'call':
        names.add(body[1])
        for child in body[2:]:
            names.update(called_components(child))
    elif body[0] not in ('arg', 'const'):
        raise ValueError('Experience must be a call-only composition')
    return tuple(sorted(names))


class ExperienceRouter:
    def __init__(self, tree):
        self.tree = tree

    @classmethod
    def fit(cls, examples):
        rows = [(tuple(features), tuple(sorted(set(names)))) for features, names in examples]
        if not rows or len(rows) > 256 or any(len(f) != 6 or not n for f, n in rows):
            raise ValueError('Use 1..256 six-feature routing examples with component labels')

        def build(group, available):
            labels = {names for _, names in group}
            union = sorted({name for _, names in group for name in names})
            if len(labels) == 1 or not available:
                return {'components': union}
            choices = []
            for axis in available:
                buckets = {}
                for row in group:
                    buckets.setdefault(row[0][axis], []).append(row)
                if len(buckets) > 1:
                    # Minimize conflicting-label pairs, with deterministic ties.
                    conflict = sum(sum(a[1] != b[1] for a in bucket for b in bucket)
                                   for bucket in buckets.values())
                    choices.append((conflict, axis, buckets))
            if not choices:
                return {'components': union}
            _, axis, buckets = min(choices, key=lambda x: (x[0], x[1]))
            return {'feature': axis, 'fallback': union,
                    'branches': {str(value): build(bucket, available - {axis})
                                 for value, bucket in sorted(buckets.items())}}

        return cls(build(rows, set(range(6))))

    def select(self, features):
        if len(features) != 6:
            raise ValueError('Expected six probe features')
        node = self.tree
        while 'feature' in node:
            child = node['branches'].get(str(features[node['feature']]))
            if child is None:
                return tuple(node['fallback'])
            node = child
        return tuple(node['components'])

    def encoded(self):
        return (json.dumps({'schema': 'kavi.experience-router.v1', 'tree': self.tree},
                           sort_keys=True, separators=(',', ':')) + '\n').encode()
