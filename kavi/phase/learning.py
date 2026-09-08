"""Bounded structural proposals and phase readout acquisition.

The grammar is supplied. Evidence can select impulses and couplings and bind
observed final states to output ports. No language interpretation is installed.
"""

from dataclasses import replace

from .runtime import PhaseActivity
from .selection import select_correction


def proposals(model, alphabet):
    """Reuse first, then change one impulse, then add one directed coupling.

    This finite local neighbourhood cannot discover every useful circuit. Multiple
    accepted correction rounds can compose changes; simultaneous edits and learned
    proposal procedures require separate implementations.
    """
    yield model
    n = len(model.moduli)
    for event in sorted(set(alphabet)):
        rest = tuple(row for row in model.impulses if row[0] != event)
        for target in range(n):
            for kick in (-1, 0, 1):
                yield replace(model, impulses=rest+((event, target, kick),))
    for source, modulus in enumerate(model.moduli):
        for phase in range(modulus):
            for target in range(n):
                for kick in (-1, 1):
                    edge = source, phase, target, kick
                    if edge not in model.couplings:
                        yield replace(model, couplings=model.couplings+(edge,))


def bind_readouts(model, examples, work):
    """Reject contradictory final states instead of retaining a lesson lookup."""
    labels = {}
    for events, port in examples:
        if type(port) is not int:
            raise ValueError('Teaching outcomes must be integer output ports')
        run = PhaseActivity(model, work)
        for event in events:
            run.accept(event)
            if run.failed:
                return None
        state = run.phases
        if state in labels and labels[state] != port:
            return None
        labels[state] = port
    # Earlier unmentioned readouts remain; explicit corrections can change them.
    readouts = dict(model.outputs)
    readouts.update(labels)
    return replace(model, outputs=tuple(sorted(readouts.items())))


def teach(model, lessons, protected, work, *, max_candidates=256):
    """One supervised update, returning an immutable successor and work results.

    The caller keeps the original until this call succeeds. Sealed test questions
    must never enter lessons or protected. Evidence is transient training workspace.
    """
    lessons = tuple((tuple(events), port) for events, port in lessons)
    protected = tuple((tuple(events), port) for events, port in protected)
    if not lessons or type(max_candidates) is not int or max_candidates < 1:
        raise ValueError('Teaching evidence and a positive candidate budget are required')
    evidence = protected+lessons
    alphabet = {event for events, _ in evidence for event in events}
    work.add('phase_evidence_events', sum(len(events) for events, _ in evidence))
    count, exhausted = 0, False
    def candidates():
        nonlocal count, exhausted
        for proposal in proposals(model, alphabet):
            if count == max_candidates:
                exhausted = True
                break
            count += 1
            work.add('phase_structural_proposals')
            candidate = bind_readouts(proposal, evidence, work)
            if candidate is not None:
                yield candidate
    successor, result = select_correction(model, candidates(), lessons, protected,
                                          work, max_candidates=max_candidates)
    result.update(structural_proposals=count, neighbourhood_truncated=exhausted)
    return successor, result
