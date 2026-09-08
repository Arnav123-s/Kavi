"""Supplied clause masking and formula ports for a learned phrase circuit.

The teacher/caller marks the two atomic clause spans. This module neither learns
those boundaries nor provides lexical connective-to-formula mappings.
"""

import re

FORMS = (('and', 'P', 'Q'), ('or', 'P', 'Q'), ('implies', 'P', 'Q'),
         ('implies', 'Q', 'P'), ('iff', 'P', 'Q'))


def events(sentence, clauses):
    if type(sentence) is not str or len(sentence) > 8192 or len(clauses) != 2:
        raise ValueError('Expected a short sentence and two marked clauses')
    spans = []
    for clause in clauses:
        if not clause or sentence.count(clause) != 1:
            raise ValueError('Each marked clause must occur exactly once')
        start = sentence.index(clause)
        spans.append((start, start+len(clause)))
    spans.sort()
    if spans[0][1] > spans[1][0]:
        raise ValueError('Clause spans overlap')
    pieces, cursor = [], 0
    for start, end in spans:
        pieces.extend(re.findall(r"[\w’']+",sentence[cursor:start].lower()))
        pieces.append('@clause')
        cursor = end
    pieces.extend(re.findall(r"[\w’']+",sentence[cursor:].lower()))
    return tuple(pieces)


def interpret(circuit, sentence, clauses, work):
    sequence = events(sentence, clauses)
    work.add('english_input_characters', len(sentence))
    port = circuit.predict(sequence, work)
    if port is None:
        return None
    if type(port) is not int or not 0 <= port < len(FORMS):
        raise ValueError('Unknown formula port')
    return FORMS[port]
