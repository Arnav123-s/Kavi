"""Finite supervised replacement with explicit retention obligations."""

from ..composable_configurations import encoded

def select_correction(current, candidates, lessons, protected, work, *, max_candidates=256):
    """Select a supplied replacement against correction and retention obligations.

    The teacher owns examples and their provenance. No examples enter the returned
    configuration. This proves only finite-bank retention. Unknown outputs count
    as errors. Contradictory requirements leave the current configuration intact.
    """
    if type(max_candidates) is not int or max_candidates < 1:
        raise ValueError('Invalid candidate budget')
    lessons, protected = tuple(lessons), tuple(protected)
    if not lessons:
        raise ValueError('Correction evidence is required')
    def score(model):
        errors = 0
        for events, port in protected:
            if model.predict(events, work) != port:
                return None
        for events, port in lessons:
            errors += model.predict(events, work) != port
        size = len(encoded(model.record()))
        work.add('phase_serialized_bytes', size)
        return errors, size
    best, best_score = current, score(current)
    examined = 0
    for candidate in candidates:
        if examined >= max_candidates:
            raise InterruptedError('Phase candidate budget exhausted')
        examined += 1
        work.add('phase_candidates')
        value = score(candidate)
        if value is not None and (best_score is None or value < best_score):
            best, best_score = candidate, value
    return best, {'candidates': examined, 'accepted': best != current,
                  'errors': None if best_score is None else best_score[0],
                  'finite_retention_passed': best_score is not None}
