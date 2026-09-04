"""Novel, exact-graded symbol-operation quizzes, distinct from retention checks.

These are teacher-defined exercises. No answers or string-operation routines
are inserted into the model. A task label alone is never counted as knowledge.
"""

from __future__ import annotations

import random

from .language_curriculum import LETTERS, LanguageExample, letters_case, spelling_case


OPERATIONS = ("copy", "join", "first", "last")


def exercise(operation, symbols):
    if operation == "copy":
        return letters_case(symbols)
    if operation == "join":
        return spelling_case((symbols,))
    if operation not in ("first", "last") or not symbols:
        raise ValueError("Unknown operation or empty symbol sequence.")
    return LanguageExample("symbol-position", operation.capitalize() + " " + symbols,
                           symbols[0] if operation == "first" else symbols[-1],
                           "Use the first/last symbol in the written logical sequence. This is a defined symbol task, not a claim about word meaning.")


def mixed_questions(seed, *, count=32, difficulty=3, extra_characters=(), exclude=(), avoid_sequences=()):
    if not 4 <= count <= 256 or not 3 <= difficulty <= 6:
        raise ValueError("Quiz budget: 4..256 cases, difficulty 3..6 symbols.")
    if any(len(c) != 1 for c in extra_characters):
        raise ValueError("This foundation quiz uses single code points, not grapheme segmentation.")
    rng, seen, rows = random.Random(seed), set(exclude), []
    reserved_sequences = set(avoid_sequences)
    for _ in range(count * 300):
        operation = OPERATIONS[len(rows) % len(OPERATIONS)]
        length = rng.randint(3, difficulty)
        # Extra-script symbols are only drawn from the current taught subset.
        alphabet = LETTERS + "".join(extra_characters)
        symbols = "".join(rng.choice(alphabet) for _ in range(length))
        if extra_characters and len(rows) % 4 == 0:
            where = rng.randrange(length)
            symbols = symbols[:where] + rng.choice(extra_characters) + symbols[where+1:]
        if symbols in reserved_sequences:
            continue
        q = exercise(operation, symbols)
        if q.key in seen:
            continue
        seen.add(q.key)
        rows.append(q)
        if len(rows) == count:
            rng.shuffle(rows)
            return rows
    raise ValueError("No unused mixed questions remain in this bounded family.")


def task_name(question):
    return question.prompt.split(" ", 1)[0].lower()
