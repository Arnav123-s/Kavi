"""Authored teaching banks for a bounded, multi-track foundation assessment."""

from dataclasses import dataclass
from itertools import product
import random


@dataclass(frozen=True)
class Lesson:
    name: str
    arity: int
    title: str


LESSONS = (
    Lesson('cube', 1, 'Build a cube from earlier arithmetic'),
    Lesson('sum_squares', 2, 'Combine two squared quantities'),
    Lesson('shifted_square', 2, 'Square a combined quantity'),
    Lesson('scaled_square', 2, 'Scale a squared quantity'),
    Lesson('affine', 3, 'Combine a product and an offset'),
    Lesson('quadratic_offset', 3, 'Reuse a scaled square with an offset'),
    Lesson('cubic_sum', 2, 'Reuse a cube in another computation'),
    Lesson('combined_fourth', 2, 'Reuse a fourth power after addition'),
)


def target(name, xs):
    a = xs[0]
    if name == 'cube': return a**3
    b = xs[1]
    if name == 'sum_squares': return a*a+b*b
    if name == 'shifted_square': return (a+b)**2
    if name == 'scaled_square': return a*b*b
    if name == 'affine': return a*b+xs[2]
    if name == 'quadratic_offset': return a*b*b+xs[2]
    if name == 'cubic_sum': return a**3+b
    if name == 'combined_fourth': return (a+b)**4
    raise ValueError('Unknown authored lesson')


def banks(lesson, seed):
    """Four initial examples, disjoint correction and final partitions."""
    rng = random.Random(seed + sum((i+1)*ord(c) for i,c in enumerate(lesson.name)))
    low = list(product(range(6), repeat=lesson.arity))
    rng.shuffle(low)
    train = low[:4]
    correction = low[4:20]
    high = list(product(range(6, 13), repeat=lesson.arity))
    rng.shuffle(high)
    final = high[:24]
    return train, correction, final


def language_packet():
    """Annotation teaches routing and relation slots, not physical or literary truth."""
    teaching, final = [], []
    numeric = [
        ('cube', 'cube of {0}', (2,), (3,), (11,)),
        ('sum_squares', 'sum of squares of {0} and {1}', (2,3), (4,5), (7,11)),
        ('scaled_square', 'twice kinetic energy for mass {0} and speed {1}', (2,3), (4,5), (7,11)),
        ('affine', 'position after speed {0} time {1} starting at {2}', (2,3,4), (5,6,7), (8,9,10)),
        ('multiply', 'force for mass {0} and acceleration {1}', (2,3), (4,5), (7,11)),
    ]
    for label, pattern, a, b, held in numeric:
        for xs in (a,b):
            teaching.append({'text':pattern.format(*xs), 'source':'authored:foundation-20260907',
                'target':{'kind':'calculation','label':label,'inputs':list(xs)}})
        final.append({'text':pattern.format(*held), 'target':{'kind':'calculation','label':label,'inputs':list(held)},
                      'expected': held[0]*held[1] if label=='multiply' else target(label,held)})
    relations = [
        ('conditional', 'if {premise} then {conclusion}',
         [{'premise':'rain falls','conclusion':'soil gets wet'}, {'premise':'water freezes','conclusion':'ice forms'}],
         {'premise':'a premise is false','conclusion':'the argument requires review'}),
        ('reason', '{claim} because {reason}',
         [{'claim':'the room is bright','reason':'a lamp is on'}, {'claim':'the ground is wet','reason':'rain fell'}],
         {'claim':'the interpretation is doubtful','reason':'the passage allows another reading'}),
        ('attribution', '{speaker} claims that {claim}',
         [{'speaker':'the narrator','claim':'the journey ended'}, {'speaker':'the critic','claim':'the image repeats'}],
         {'speaker':'the witness','claim':'the account leaves out an event'}),
        ('interpretive_claim', 'the image of {image} suggests {interpretation}',
         [{'image':'a closed door','interpretation':'isolation'}, {'image':'an open road','interpretation':'possibility'}],
         {'image':'a broken clock','interpretation':'interrupted time'}),
    ]
    for label, pattern, examples, held in relations:
        for slots in examples:
            teaching.append({'text':pattern.format(**slots),'source':'authored:foundation-20260907',
                             'target':{'kind':'relation','label':label,'slots':slots}})
        final.append({'text':pattern.format(**held),'target':{'kind':'relation','label':label,'slots':held}})
    return teaching, final


FRONTIER = [
    {'track':'Mathematics', 'task':'Exact rational and signed arithmetic', 'state':'unsupported',
     'reason':'The current procedure executor accepts natural numbers; fractions and unrestricted negatives need representation changes.'},
    {'track':'Physics', 'task':'General quantum state evolution', 'state':'unsupported',
     'reason':'Complex vectors, operators, units and numerical error control are not supported by this executor.'},
    {'track':'Language and philosophy', 'task':'Interpret a new passage and defend an argument', 'state':'unassessed',
     'reason':'Sentence-slot recognition does not implement passage understanding, truth assessment or argument construction.'},
]
