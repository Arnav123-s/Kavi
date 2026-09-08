"""Finite coupled phase circuits; explicit dynamics and supervised replacement.

This substrate is discrete, not a simulation of physical or quantum pendulums.
It retains current phases, not an input history. Candidate construction and the
input alphabet are supplied; selecting a candidate is not semantic discovery.
"""

from dataclasses import dataclass, asdict


def contains(pattern, phases):
    """A readout conjunction uses exact phases or inclusive phase intervals."""
    return all((p == value if type(p) is int else p[0] <= value <= p[1])
               for p, value in zip(pattern, phases))

@dataclass(frozen=True)
class PhaseConfiguration:
    moduli: tuple
    # (event, target, increment). Several impulses can share an event or target.
    impulses: tuple = ()
    # (source, triggering phase, target, increment); all read the same snapshot.
    couplings: tuple = ()
    # (phase pattern, output port); each coordinate is exact or an interval.
    outputs: tuple = ()
    ticks: int = 1

    def __post_init__(self):
        if any(type(value) is not tuple for value in (self.moduli, self.impulses, self.couplings, self.outputs)):
            raise ValueError('Configuration collections must be immutable tuples')
        if any(type(row) is not tuple for rows in (self.impulses, self.couplings, self.outputs) for row in rows):
            raise ValueError('Configuration rows must be immutable tuples')
        n = len(self.moduli)
        if not 1 <= n <= 64 or any(type(m) is not int or not 2 <= m <= 256 for m in self.moduli):
            raise ValueError('Invalid phase dimensions')
        if type(self.ticks) is not int or not 1 <= self.ticks <= 256:
            raise ValueError('Invalid event propagation budget')
        def node(i):
            return type(i) is int and 0 <= i < n
        for event, target, delta in self.impulses:
            if not isinstance(event, str) or not event or not node(target) or type(delta) is not int:
                raise ValueError('Invalid event impulse')
        for source, phase, target, delta in self.couplings:
            if not node(source) or not node(target) or type(phase) is not int or not 0 <= phase < self.moduli[source] or type(delta) is not int:
                raise ValueError('Invalid phase coupling')
        seen = set()
        for state, port in self.outputs:
            def valid(p, m):
                if type(p) is int:
                    return 0 <= p < m
                return (type(p) is tuple and len(p) == 2 and all(type(v) is int for v in p)
                        and 0 <= p[0] <= p[1] < m)
            if type(state) is not tuple or len(state) != n or any(not valid(p, m) for p, m in zip(state, self.moduli)) or type(port) is not int:
                raise ValueError('Invalid phase readout')
            if state in seen:
                raise ValueError('Duplicate phase readout')
            seen.add(state)

    def record(self):
        return asdict(self)

    @classmethod
    def from_record(cls, record):
        if set(record) != {'moduli', 'impulses', 'couplings', 'outputs', 'ticks'}:
            raise ValueError('Invalid phase schema')
        return cls(tuple(record['moduli']), tuple(map(tuple, record['impulses'])),
                   tuple(map(tuple, record['couplings'])),
                   tuple((tuple(tuple(p) if isinstance(p, list) else p for p in state), port)
                         for state, port in record['outputs']), record['ticks'])

    def predict(self, events, work):
        from .runtime import PhaseActivity
        run = PhaseActivity(self, work)
        for event in events:
            run.accept(event)
            if run.failed:
                return None
        return run.finish()
