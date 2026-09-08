"""Stable template and whole-circuit generational reconstruction.

The template constrains the circuit grammar. Every proposal is a complete fresh
circuit assembled using inherited and newly proposed relationships. A deployed
generation stores neither the parent object nor a chain of teaching records.
"""

from dataclasses import dataclass
import hashlib
import random

from ..composable_configurations import encoded
from .model import PhaseConfiguration
from .learning import bind_readouts
from .selection import select_correction


@dataclass(frozen=True)
class CircuitTemplate:
    moduli: tuple
    ticks: int = 1
    max_couplings: int = 32
    encoding: str = 'explicit-events-v1'

    def __post_init__(self):
        PhaseConfiguration(self.moduli, ticks=self.ticks)
        if type(self.max_couplings) is not int or not 0 <= self.max_couplings <= 4096:
            raise ValueError('Invalid coupling capacity')
        if self.encoding not in ('explicit-events-v1', 'unicode-codepoints-v1', 'grayscale-v1'):
            raise ValueError('Unsupported encoding contract')

    def accepts(self, circuit):
        return (circuit.moduli == self.moduli and circuit.ticks == self.ticks
                and len(circuit.couplings) <= self.max_couplings)


@dataclass(frozen=True)
class CircuitGeneration:
    template: CircuitTemplate
    circuit: PhaseConfiguration
    generation: int = 0

    def __post_init__(self):
        if not self.template.accepts(self.circuit):
            raise ValueError('Circuit violates its template')
        if type(self.generation) is not int or self.generation < 0:
            raise ValueError('Invalid generation')

    def record(self):
        from dataclasses import asdict
        return {'template': asdict(self.template), 'circuit': self.circuit.record(),
                'generation': self.generation}


def reconstruct(current, lessons, protected, work, *, candidates=64, seed=7, readout='exact'):
    """Build complete successors, combining inheritance with new relationships.

    The first candidate reuses all dynamics while relearning the readout. Later
    candidates redraw every event's impulse group and the whole coupling set.
    Inheritance probability and the candidate generator are supplied, not learned.
    Old unobserved behavior is not universally protected by a finite evidence bank.
    """
    if type(candidates) is not int or not 1 <= candidates <= 4096:
        raise ValueError('Invalid whole-circuit search budget')
    if readout not in ('exact', 'regions'):
        raise ValueError('Unknown readout grammar')
    from .regions import bind_regions
    binder = bind_readouts if readout == 'exact' else bind_regions
    lessons = tuple((tuple(events), port) for events, port in lessons)
    protected = tuple((tuple(events), port) for events, port in protected)
    if not lessons:
        raise ValueError('A teaching round requires evidence')
    old, template = current.circuit, current.template
    evidence = protected+lessons
    alphabet = sorted({e for seq, _ in evidence for e in seq} | {e for e, _, _ in old.impulses})
    if any(not isinstance(e, str) or not e for e in alphabet):
        raise ValueError('Events must be nonempty strings')
    work.add('phase_evidence_events', sum(len(seq) for seq, _ in evidence))
    rng = random.Random(seed)
    examined, compatible = 0, 0
    inherited = {event: tuple(row for row in old.impulses if row[0] == event) for event in alphabet}
    def assembled():
        nonlocal examined, compatible
        for index in range(candidates):
            examined += 1
            work.add('phase_whole_circuit_proposals')
            if index == 0:
                impulses, couplings = old.impulses, old.couplings
            else:
                impulses = []
                for event in alphabet:
                    work.add('phase_inheritance_choices')
                    if inherited[event] and rng.random() < .5:
                        impulses.extend(inherited[event])
                    else:
                        impulses.append((event, rng.randrange(len(template.moduli)), rng.choice((-1, 0, 1))))
                impulses = tuple(impulses)
                couplings = []
                for edge in old.couplings:
                    work.add('phase_inheritance_choices')
                    if rng.random() < .5:
                        couplings.append(edge)
                for _ in range(rng.randrange(template.max_couplings-len(couplings)+1)):
                    work.add('phase_new_coupling_proposals')
                    source = rng.randrange(len(template.moduli))
                    edge = (source, rng.randrange(template.moduli[source]),
                            rng.randrange(len(template.moduli)), rng.choice((-1, 1)))
                    if edge not in couplings:
                        couplings.append(edge)
                couplings = tuple(couplings)
            proposal = PhaseConfiguration(template.moduli, impulses, couplings, (), template.ticks)
            work.add('phase_assembled_rules', len(impulses)+len(couplings))
            # Reconstruct output organization from declared evidence. No old
            # readout silently overrides a new correction at a changed state.
            bound = binder(proposal, evidence, work)
            if bound is not None:
                compatible += 1
                yield bound
    model, selection = select_correction(old, assembled(), lessons, protected,
                                         work, max_candidates=candidates)
    improved = selection['accepted']
    successor = CircuitGeneration(template, model, current.generation+1) if improved else current
    selection.update(whole_candidates=examined, compatible_candidates=compatible,
                     seed=seed, readout=readout, template_unchanged=True,
                     previous_sha256=hashlib.sha256(encoded(current.record())).hexdigest(),
                     successor_sha256=hashlib.sha256(encoded(successor.record())).hexdigest())
    return successor, selection
