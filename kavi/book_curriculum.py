"""Original-source admission, ordered arithmetic units and independent exams.

Question generation and exact rational grading are teacher functions. They do
not run inside learner inference and are not claimed as learned skills.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import re

from .source_manifest import SourceManifest


@dataclass(frozen=True)
class Question:
    prompt: str
    answer: str
    explanation: str

    @property
    def key(self) -> str:
        return hashlib.sha256(self.prompt.encode()).hexdigest()

    @property
    def prefix(self) -> str:
        return f"Question: {self.prompt}\nAnswer: "

    def correct(self, output: str) -> bool:
        value = output.strip().removesuffix(".")
        if not re.fullmatch(r"-?\d+(?:/\d+|\.\d+)?", value):
            return False
        try:
            return Fraction(value) == Fraction(self.answer)
        except (ValueError, ZeroDivisionError):
            return False


UNITS = (
    ("numeration", "Numerals, number words and place value", "I"),
    ("addition-subtraction", "Addition and subtraction", "II"),
    ("multiplication", "Equal groups and multiplication", "III"),
    ("division", "Division and its connection to multiplication", "IV"),
    ("fractions", "Fractions and equal parts", "V"),
    ("decimals", "Decimal fractions", "VI"),
    ("square-roots", "Square roots", "VII"),
    ("proportion", "Ratios and proportion", "VIII"),
    ("combinations", "Permutations and combinations", "IX"),
)


def number_words(value: int) -> str:
    small = ("zero one two three four five six seven eight nine ten eleven twelve "
             "thirteen fourteen fifteen sixteen seventeen eighteen nineteen").split()
    tens = "zero ten twenty thirty forty fifty sixty seventy eighty ninety".split()
    if not 0 <= value < 1000:
        raise ValueError("This teacher covers number words below one thousand.")
    if value < 20:
        return small[value]
    if value < 100:
        return tens[value // 10] + ("-" + small[value % 10] if value % 10 else "")
    return small[value // 100] + " hundred" + (
        " and " + number_words(value % 100) if value % 100 else "")


def questions(unit: str, seed: int, count: int, *, harder: bool = False,
              exclude: set[str] | None = None) -> list[Question]:
    if unit not in {u[0] for u in UNITS} or not 1 <= count <= 256:
        raise ValueError("Unknown unit or invalid exam size.")
    rng, seen, result = random.Random(seed), set(exclude or ()), []
    ceiling = 499 if harder else 99
    for _ in range(count * 200):
        a, b = rng.randint(1, ceiling), rng.randint(1, ceiling)
        if unit == "numeration":
            n = rng.randint(0, 999 if harder else 99)
            prompt = f"Write {number_words(n)} using decimal digits."
            answer = str(n)
            explanation = f"Use place value: {n // 100} hundreds, {(n // 10) % 10} tens and {n % 10} units."
            if rng.randrange(2):
                prompt = f"How many units are {a} tens and {b % 10} units?"
                answer = str(a * 10 + b % 10)
                explanation = "One ten means ten units; combine the tens with the remaining units."
        elif unit == "addition-subtraction":
            if rng.randrange(2):
                prompt, answer = f"What is {a} plus {b}?", str(a + b)
                explanation = f"Combine both quantities: {a} + {b} = {answer}."
            else:
                a, b = max(a, b), min(a, b)
                prompt, answer = f"Subtract {b} from {a}.", str(a - b)
                explanation = f"Remove {b} units from {a}; {answer} units remain."
        elif unit == "multiplication":
            prompt, answer = f"There are {a} groups of {b} units. How many units altogether?", str(a * b)
            explanation = f"Repeated equal groups give {a} times {b} = {answer}."
        elif unit == "division":
            prompt, answer = f"Divide {a * b} into groups of {b}. How many groups?", str(a)
            explanation = f"There are {a} groups because {a} times {b} equals {a * b}."
        elif unit == "fractions":
            prompt, answer = f"Divide {a} into {b + 1} equal parts. Give the exact size of one part.", str(Fraction(a, b + 1))
            explanation = f"Equal division gives {a}/{b + 1}; reduce numerator and denominator together."
        elif unit == "decimals":
            divisor = rng.choice((10, 100, 1000))
            prompt, answer = f"Express {a} divided by {divisor} exactly.", str(Fraction(a, divisor))
            explanation = "Each decimal place represents a division by another factor of ten."
        elif unit == "square-roots":
            prompt, answer = f"Find the nonnegative square root of {a * a}.", str(a)
            explanation = f"The answer multiplied by itself is {a * a}."
        elif unit == "proportion":
            prompt, answer = f"If x/{b} = {a}/{b + 1}, find x exactly.", str(Fraction(a * b, b + 1))
            explanation = "Multiply both sides by the denominator on the left."
        else:
            n = rng.randint(3, 2000 if harder else 1000)
            prompt, answer = f"How many unordered pairs can be chosen from {n} distinct objects?", str(n * (n - 1) // 2)
            explanation = "Count ordered pairs, then divide by two because order does not matter."
        q = Question(prompt, answer, explanation)
        if q.key not in seen:
            seen.add(q.key)
            result.append(q)
            if len(result) == count:
                return result
    raise ValueError("Fresh question space exhausted; do not recycle it as unseen.")


def load_book(repo: Path, manifest_path: Path) -> tuple[dict, dict[str, list[str]]]:
    record = json.loads(manifest_path.read_text(encoding="utf-8"))
    source = SourceManifest.load(repo / "curriculum/source-manifest.json").by_id(record["source_id"])
    if not source.is_teaching_admissible or record["translation"] is not False:
        raise ValueError("Source is not an admitted original-language work.")
    local = (repo / record["local_path"]).resolve()
    if not local.is_relative_to((repo / "private").resolve()):
        raise ValueError("Source body must stay in the private workspace.")
    payload = local.read_bytes()
    if hashlib.sha256(payload).hexdigest() != record["sha256"]:
        raise ValueError("Book fingerprint differs from the reviewed edition.")
    text = payload.decode("utf-8-sig").replace("\r\n", "\n")
    start = re.search(r"(?m)^SECTION I\.$", text)
    if not start:
        raise ValueError("Reviewed Book I start marker is missing.")
    end = text.index("\nBOOK II.", start.end())
    body = text[start.start():end]
    markers = list(re.finditer(r"(?m)^SECTION ([IVX]+)\.$", body))
    if [m[1] for m in markers] != [u[2] for u in UNITS]:
        raise ValueError("Original section ordering changed.")
    sections = {}
    for i, (unit, _, _) in enumerate(UNITS):
        finish = markers[i + 1].start() if i + 1 < len(markers) else len(body)
        raw = body[markers[i].end():finish].strip()
        paragraphs = [" ".join(p.splitlines()) for p in re.split(r"\n\s*\n", raw)
                      if len(p.strip()) >= 40]
        sections[unit] = paragraphs
    return record, sections


def split_paragraphs(paragraphs: list[str], seed: int) -> dict[str, list[str]]:
    unique = list(dict.fromkeys(paragraphs))
    if len(unique) < 10:
        raise ValueError("Not enough distinct source paragraphs for an honest split.")
    indices = list(range(len(unique)))
    random.Random(seed).shuffle(indices)
    held = set(indices[:max(2, len(indices) // 5)])
    remaining = [p for i, p in enumerate(unique) if i not in held]
    return {"train": remaining[::2], "remediation": remaining[1::2],
            "validation": [p for i, p in enumerate(unique) if i in held]}
