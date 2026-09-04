"""A small, explicit language prerequisite ladder, not a claim of fluency.

The teacher generates classroom exercises from reviewed concepts. Answers and
closed-world scene records remain outside model inference. Original passages
are admitted separately; generated exercises are never labeled author quotes.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import random
import string


@dataclass(frozen=True)
class LanguageExample:
    skill: str
    prompt: str
    answer: str
    explanation: str

    @property
    def prefix(self) -> str:
        return self.prompt + " => "

    @property
    def key(self) -> str:
        return hashlib.sha256((self.skill + "\0" + self.prefix).encode()).hexdigest()

    def correct(self, value: str) -> bool:
        # Preserve case, sequence order and full answers; no substring credit.
        return value.strip() == self.answer


@dataclass(frozen=True)
class LanguageStage:
    stage_id: str
    title: str
    prerequisites: tuple[str, ...]
    source_packets: tuple[str, ...]
    scope: str


STAGES = (
    LanguageStage("en-letter-sequences", "Recognize and reproduce written letters",
                  (), ("unicode-latin-letters", "grammar-name-words"),
                  "ASCII letter copying and new letter combinations; not English comprehension."),
    LanguageStage("en-word-forms", "Build written words from their letters",
                  ("en-letter-sequences",), ("grammar-name-words", "demorgan-number-words"),
                  "Join a limited written vocabulary; spelling is not meaning."),
    LanguageStage("en-quantity-meanings", "Connect number words with small quantities",
                  ("en-word-forms",), ("demorgan-number-words", "demorgan-counting"),
                  "Ground ten number words in explicit mark counts; not a general vocabulary."),
    LanguageStage("en-sentence-roles", "Understand who has which object in one sentence",
                  ("en-quantity-meanings",), ("grammar-sentence", "grammar-predicate"),
                  "Controlled ownership sentences with names and four object words."),
    LanguageStage("en-short-passages", "Read several sentences without mixing their facts",
                  ("en-sentence-roles",), ("grammar-predicate", "grammar-name-words"),
                  "Two or three explicit ownership facts; not unrestricted reading comprehension."),
)
STAGE_IDS = tuple(stage.stage_id for stage in STAGES)
LETTERS = string.ascii_letters
NUMBERS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
NAMES = ("Ada", "Bo", "Cai", "Dara", "Eli", "Fara", "Gita", "Hana", "Ivo", "Jin",
         "Kavi", "Lina", "Mira", "Noor", "Omar", "Pia", "Qin", "Ravi", "Sara", "Tao",
         "Uma", "Vera", "Wen", "Xia", "Yara", "Zuri")
OBJECTS = ("book", "pen", "ball", "box")
WORDS = NUMBERS + OBJECTS + ("has", "a", "who", "what", "does", "have")


def allowed(stage_id: str, passed: list[str]) -> bool:
    stage = next((s for s in STAGES if s.stage_id == stage_id), None)
    return stage is not None and all(p in passed for p in stage.prerequisites)


def letters_case(text: str) -> LanguageExample:
    return LanguageExample(STAGE_IDS[0], "Copy " + text, text,
                           "Keep every written letter, its case and its order unchanged.")


def spelling_case(words: tuple[str, ...]) -> LanguageExample:
    return LanguageExample(STAGE_IDS[1], "Join " + " / ".join(" ".join(w) for w in words),
                           " ".join(words), "Join the letters within each word; / separates words.")


def quantity_case(values: tuple[int, ...], reverse: bool = False) -> LanguageExample:
    marks = ["x" * n if n else "empty" for n in values]
    names = [NUMBERS[n] for n in values]
    shown, expected = (names, marks) if reverse else (marks, names)
    return LanguageExample(STAGE_IDS[2], ("Show " if reverse else "Name ") + " | ".join(shown),
                           " | ".join(expected),
                           "Each x stands for one object. empty means none. Match each group separately; do not add groups.")


def scene_case(facts: tuple[tuple[str, str], ...], target: int, ask_owner: bool,
               *, skill: str) -> LanguageExample:
    subject, obj = facts[target]
    statements = " ".join(f"{name} has a {item}." for name, item in facts)
    question = f"Who has a {obj}?" if ask_owner else f"What does {subject} have?"
    return LanguageExample(skill, statements + " " + question,
                           subject if ask_owner else obj,
                           f"Use the stated fact: {subject} has a {obj}. Other names belong to other facts.")


def inventory(stage_id: str) -> list[LanguageExample]:
    """Known-item calibration, explicitly NOT an unseen generalization exam."""
    if stage_id == STAGE_IDS[0]:
        return [letters_case(c) for c in LETTERS]
    if stage_id == STAGE_IDS[1]:
        return [spelling_case((w,)) for w in WORDS]
    if stage_id == STAGE_IDS[2]:
        return [quantity_case((n,), reverse) for n in range(10) for reverse in (False, True)]
    if stage_id == STAGE_IDS[3]:
        return [scene_case(((name, OBJECTS[i % 4]),), 0, owner, skill=stage_id)
                for i, name in enumerate(NAMES[:8]) for owner in (False, True)]
    if stage_id == STAGE_IDS[4]:
        return [scene_case(((name, "book"), (NAMES[i+1], "pen")), i % 2, owner, skill=stage_id)
                for i, name in enumerate(NAMES[:8]) for owner in (False, True)]
    raise ValueError("Unknown language foundation.")


def varied(stage_id: str, seed: int, count: int, *, harder: bool = False,
           exclude: set[str] | None = None) -> list[LanguageExample]:
    """New combinations of taught primitives, with exact question exclusion."""
    if stage_id not in STAGE_IDS or not 1 <= count <= 256:
        raise ValueError("Unknown stage or invalid exercise budget.")
    rng, seen, result = random.Random(seed), set(exclude or ()), []
    for _ in range(count * 300):
        if stage_id == STAGE_IDS[0]:
            text = "".join(rng.choice(LETTERS) for _ in range(3 if harder else 2))
            q = letters_case(text)
        elif stage_id == STAGE_IDS[1]:
            q = spelling_case(tuple(rng.choice(WORDS) for _ in range(3 if harder else 2)))
        elif stage_id == STAGE_IDS[2]:
            q = quantity_case(tuple(rng.randrange(10) for _ in range(3 if harder else 2)), bool(rng.randrange(2)))
        else:
            size = 1 if stage_id == STAGE_IDS[3] else 3 if harder else 2
            # Paired proper-name labels keep harder sentence tests distinct without
            # pretending a finite question pool supplies endless unique exams.
            labels = tuple(a + " " + b for a in NAMES for b in NAMES) if harder else NAMES
            names, objects = rng.sample(labels, size), rng.sample(OBJECTS, size)
            q = scene_case(tuple(zip(names, objects)), rng.randrange(size), bool(rng.randrange(2)), skill=stage_id)
        if q.key not in seen:
            seen.add(q.key)
            result.append(q)
            if len(result) == count:
                return result
    raise ValueError("Unseen exercise space exhausted; do not relabel repeated questions as fresh.")
