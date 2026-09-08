"""Learn an input-role habitat separately from fixed device limits.

Roles are inferred by equality of observed substitution contexts. They have no
installed semantic names. The finite language is represented by role domains
and admitted role patterns, not by a retained list of source lessons.
"""

from dataclasses import dataclass, asdict
from itertools import product

from ..composable_configurations import encoded
from .layers import CircuitGeneration, reconstruct


@dataclass(frozen=True)
class Habitat:
    roles: tuple = ()
    patterns: tuple = ()

    def __post_init__(self):
        if type(self.roles) is not tuple or type(self.patterns) is not tuple:
            raise ValueError('Habitat collections must be immutable')
        alphabet = []
        for role in self.roles:
            if type(role) is not tuple or not role or any(type(e) is not str or not e for e in role):
                raise ValueError('Invalid role domain')
            alphabet.extend(role)
        if len(alphabet) != len(set(alphabet)):
            raise ValueError('Role domains must be disjoint')
        for pattern in self.patterns:
            if (type(pattern) is not tuple or not pattern or len(pattern) > 64
                    or any(type(i) is not int or not 0 <= i < len(self.roles) for i in pattern)):
                raise ValueError('Invalid role pattern')
        if len(self.patterns) != len(set(self.patterns)):
            raise ValueError('Duplicate pattern')

    def record(self):
        return asdict(self)

    def accepts(self, events, work):
        sequence = tuple(events)
        lookup = {}
        for i, role in enumerate(self.roles):
            for symbol in role:
                work.add('habitat_role_symbols')
                lookup[symbol] = i
        work.add('habitat_input_events', len(sequence))
        if any(event not in lookup for event in sequence):
            return False
        pattern = tuple(lookup[event] for event in sequence)
        for known in self.patterns:
            work.add('habitat_pattern_checks')
            if pattern == known:
                return True
        return False

    def language(self, work, *, limit=4096):
        """Expand the deployed boundary for bounded exact retention checking.

        This is transient replay derived from a configuration, not a source
        corpus retained in the deployed object. No truth labels are stored here.
        """
        if type(limit) is not int or limit < 1:
            raise ValueError('Invalid expansion ceiling')
        count = 0
        for pattern in self.patterns:
            for sequence in product(*(self.roles[i] for i in pattern)):
                if count == limit:
                    raise InterruptedError('Habitat expansion budget exhausted')
                work.add('habitat_expanded_events', len(sequence))
                count += 1
                yield sequence


def infer_habitat(sequences, work):
    """Rebuild all roles and patterns from confirmed finite structural evidence.

    Symbols share a role only when they have identical sets of one-hole contexts
    (prefix, suffix). The input language is finite and exact. This rule discovers
    factorization; it does not invent unseen semantic categories or examples.
    """
    words = set()
    for sequence in sequences:
        word = tuple(sequence)
        if not word or len(word) > 64 or any(type(e) is not str or not e for e in word):
            raise ValueError('Invalid structural evidence')
        work.add('habitat_observed_events', len(word))
        words.add(word)
        if len(words) > 4096:
            raise InterruptedError('Habitat evidence budget exhausted')
    contexts = {}
    for word in sorted(words):
        for index, symbol in enumerate(word):
            work.add('habitat_context_coordinates', len(word)-1)
            contexts.setdefault(symbol, set()).add((word[:index], word[index+1:]))
    classes = {}
    for symbol, context in contexts.items():
        key = tuple(sorted(context))
        work.add('habitat_context_signatures', len(key))
        classes.setdefault(key, []).append(symbol)
    roles = tuple(sorted(tuple(sorted(group)) for group in classes.values()))
    lookup = {symbol:i for i,role in enumerate(roles) for symbol in role}
    patterns = tuple(sorted({tuple(lookup[e] for e in word) for word in words}))
    return Habitat(roles, patterns)


@dataclass(frozen=True)
class WorldGeneration:
    habitat: Habitat
    inner: CircuitGeneration

    def record(self):
        return {'habitat':self.habitat.record(), 'inner':self.inner.record()}

    def predict(self, events, work):
        sequence = tuple(events)
        if not self.habitat.accepts(sequence, work):
            return None
        return self.inner.circuit.predict(sequence, work)


def teach_world(current, lessons, work, *, candidates=256, seed=7):
    """Atomically replace learned boundary and whole circuit after validation.

    Replay old inputs from the old habitat and obtain their targets from the old
    circuit. Explicit new contradictory targets are corrections, not retention
    obligations. Rejection or interruption leaves the current world untouched.
    The inner template remains a supplied device/search envelope.
    """
    lessons = tuple((tuple(events), port) for events,port in lessons)
    if not lessons or any(type(port) is not int for _,port in lessons):
        raise ValueError('Labelled teaching evidence required')
    targets = {}
    for sequence,port in lessons:
        if sequence in targets and targets[sequence] != port:
            raise ValueError('Contradictory simultaneous teaching')
        targets[sequence] = port
    old_language = tuple(current.habitat.language(work))
    protected, corrected = [], 0
    for sequence in old_language:
        previous = current.inner.circuit.predict(sequence, work)
        if previous is None:
            raise ValueError('Deployed habitat admits an unresolved input')
        if sequence in targets and targets[sequence] != previous:
            corrected += 1
        else:
            protected.append((sequence, previous))
    # Infer first so malformed structural evidence cannot start circuit search.
    boundary = infer_habitat((*old_language, *targets), work)
    inner, selection = reconstruct(current.inner, lessons, protected, work,
                                   candidates=candidates, seed=seed, readout='exact')
    successor = WorldGeneration(boundary, inner)
    valid = all(successor.predict(seq, work) == port for seq,port in lessons+tuple(protected))
    # Check the full old boundary, not merely the protected output subset.
    preserved = all(boundary.accepts(seq, work) for seq in old_language)
    work.add('habitat_candidate_bytes', len(encoded(successor.record())))
    accepted = valid and preserved and successor != current
    result = {'accepted':accepted, 'inner_selection':selection,
              'old_boundary_cases':len(old_language), 'protected_cases':len(protected),
              'explicit_corrections':corrected, 'boundary_preserved':preserved,
              'habitat_changed':accepted and boundary != current.habitat,
              'roles':len(boundary.roles), 'patterns':len(boundary.patterns)}
    return (successor if accepted else current), result
