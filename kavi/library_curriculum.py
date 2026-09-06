"""External arithmetic lessons, source witnesses and isolated final banks."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import random
import re

from .procedure_search import ProgramExample


@dataclass(frozen=True)
class Lesson:
    name: str
    arity: int
    teaching_maxima: tuple[int, ...]
    teaching_count: int
    source_scope: str
    purpose: str
    contract: str = "naturals"


LESSONS = (
    Lesson("double", 1, (15,), 8, "repeated_quantities", "Acquire two equal quantities as a reusable operation."),
    Lesson("sum3", 3, (7, 7, 7), 40, "addition", "Combine three quantities using acquired addition."),
    Lesson("triple", 1, (15,), 8, "repeated_quantities", "Test whether an earlier procedure helps acquire three equal quantities."),
    Lesson("adjusted_difference", 3, (7, 7, 7), 40, "subtraction", "Reuse acquired subtraction and addition; the first input must be at least the second.", "ordered_prefix"),
    Lesson("multiply", 2, (15, 15), 48, "multiplication", "Acquire repeated equal quantities through a selected iteration program."),
    Lesson("square", 1, (15,), 8, "multiplication", "Reuse a learned product with two equal operands."),
    Lesson("power", 2, (6, 5), 24, "derived_exercises", "Test repeated composition beyond the selected source examples; zero to power zero is one here."),
    Lesson("triangular", 1, (15,), 8, "derived_exercises", "Acquire a sum over an increasing finite range."),
    Lesson("factorial", 1, (8,), 6, "permutations", "Acquire the product counting arrangements of distinct objects; zero factorial is one."),
    Lesson("sum_squares", 2, (7, 7), 24, "derived_exercises", "Combine separately acquired products and addition."),
)

SCALING_LESSON = Lesson("scale", 2, (0, 0), 24, "derived_exercises",
    "Acquire multiplication of a large quantity by a small count within the existing execution budget.")


def target(name: str, args: tuple[int, ...]) -> int:
    """Reference operations belong to the teacher and evaluator, never inference."""
    a = args[0]
    if name == "add": return a + args[1]
    if name == "subtract": return a - args[1]
    if name == "double": return a * 2
    if name == "sum3": return sum(args)
    if name == "triple": return a * 3
    if name == "adjusted_difference": return a - args[1] + args[2]
    if name in {"multiply", "scale"}: return a * args[1]
    if name == "square": return a * a
    if name == "power": return a ** args[1]
    if name == "triangular": return a * (a + 1) // 2
    if name == "factorial": return math.factorial(a)
    if name == "sum_squares": return a * a + args[1] * args[1]
    raise ValueError("Unknown teaching objective.")


def partition(lesson: Lesson, seed: int):
    cases = (list(product((0, 1, 16, 64, 256, 513, 1024, 2048), range(8)))
             if lesson.name == "scale" else
             list(product(*(range(value + 1) for value in lesson.teaching_maxima))))
    if lesson.contract == "ordered_prefix":
        cases = [args for args in cases if args[0] >= args[1]]
    rng = random.Random(seed ^ int.from_bytes(lesson.name.encode(), "little"))
    rng.shuffle(cases)
    # Distinguish zero/one conventions before selection; this rule is fixed for every seed.
    anchors = [tuple(0 for _ in range(lesson.arity)), tuple(1 for _ in range(lesson.arity))]
    if lesson.name == "factorial":
        anchors = [(0,), (1,), (2,), (3,), (4,), (5,)]
    if lesson.name == "scale":
        anchors += [(1024, 2)]
    for value in reversed(anchors):
        cases.remove(value)
        cases.insert(0, value)
    teaching, held_out = cases[:lesson.teaching_count], cases[lesson.teaching_count:]
    return ([ProgramExample(args, target(lesson.name, args)) for args in teaching],
            [ProgramExample(args, target(lesson.name, args)) for args in held_out])


def audit_cases(name: str):
    if name == "add":
        domain = product(range(256), repeat=2)
    elif name == "subtract":
        domain = ((a, b) for a in range(256) for b in range(a + 1))
    elif name == "sum3":
        domain = product(range(16), repeat=3)
    elif name == "adjusted_difference":
        domain = ((a, b, c) for a in range(16) for b in range(a + 1) for c in range(16))
    elif name in {"multiply", "scale", "sum_squares"}:
        domain = product(range(32), repeat=2)
    elif name == "power":
        domain = product(range(13), range(9))
    elif name == "factorial":
        domain = ((value,) for value in range(11))
    elif name == "square":
        domain = ((value,) for value in range(64))
    else:
        domain = ((value,) for value in range(256))
    return [ProgramExample(args, target(name, args)) for args in domain]


def transfer_cases(name: str, seed: int, extended: bool = False):
    rng = random.Random(seed ^ int.from_bytes(name.encode(), "big") ^ 0x13579B)
    values = []
    if name in {"add", "subtract", "double", "triple", "sum3", "adjusted_difference"}:
        arity = 3 if name in {"sum3", "adjusted_difference"} else (1 if name in {"double", "triple"} else 2)
        for bits in (16, 64, 256, 1024):
            for _ in range(8):
                args = tuple((1 << (bits - 1)) | rng.getrandbits(bits - 1) for _ in range(arity))
                if name == "subtract": args = tuple(sorted(args, reverse=True))
                if name == "adjusted_difference": args = (*sorted(args[:2], reverse=True), args[2])
                values.append(args)
    elif name in {"multiply", "scale"}:
        # Both orders are declared: a one-sided repeated-addition algorithm may exhaust fuel.
        for bits in (16, 64, 256):
            for _ in range(4):
                big = (1 << (bits - 1)) | rng.getrandbits(bits - 1)
                small = rng.randrange(17, 41)
                values.extend(((big, small), (small, big)))
    elif name == "power":
        values = list(product(range(17, 21), range(7, 11))) if extended else list(product(range(13, 17), range(6, 10)))
    elif name == "factorial": values = [(n,) for n in (range(15, 19) if extended else range(11, 15))]
    elif name == "triangular": values = [(n,) for n in range(256, 385, 8)]
    elif name == "square": values = [(n,) for n in range(64, 97)]
    elif name == "sum_squares": values = [(rng.randrange(32, 64), rng.randrange(32, 64)) for _ in range(32)]
    return [ProgramExample(args, target(name, args)) for args in dict.fromkeys(values)]


def source_witness(repo: Path) -> tuple[dict, dict[str, str]]:
    metadata = json.loads((repo / "curriculum/arithmetic-original.json").read_text(encoding="utf-8"))
    manifest = json.loads((repo / "curriculum/source-manifest.json").read_text(encoding="utf-8"))
    admitted = next(row for row in manifest["sources"] if row["source_id"] == metadata["source_id"])
    if admitted["status"] != "approved" or admitted["license_class"] != "public-domain-us":
        raise ValueError("The selected arithmetic source is not admitted.")
    path = (repo / metadata["local_path"]).resolve()
    if not path.is_relative_to((repo / "private/sources").resolve()):
        raise ValueError("Source path must remain in the private source directory.")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != metadata["sha256"]:
        raise ValueError("The arithmetic source differs from the reviewed witness.")
    body = raw.decode("utf-8")
    regions = {"addition": (28, 30), "repeated_quantities": (35, 38),
               "subtraction": (39, 41), "multiplication": (47, 49), "permutations": (206, 207)}
    extracts, scopes = {}, {}
    for name, (start, end) in regions.items():
        first = re.search(rf"^{start}\. ", body, re.M)
        final = re.search(rf"^{end + 1}\. ", body, re.M)
        if first is None or final is None or final.start() <= first.start():
            raise ValueError("Reviewed paragraph boundary is missing.")
        extract = body[first.start():final.start()].strip()
        extracts[name] = extract
        scopes[name] = {"paragraphs": [start, end], "sha256": hashlib.sha256(extract.encode()).hexdigest()}
    witness = {"source_id": metadata["source_id"], "title": metadata["title"],
               "author": metadata["author"], "catalog_url": metadata["catalog_url"],
               "witness_sha256": metadata["sha256"], "scopes": scopes,
               "teaching_boundary": "A supplied teacher interprets the selected arithmetic ideas and generates formal exercises. The learner receives numerical examples, not prose.",
               "derived_exercises": "Scaling, when enabled, power, triangular sums and sum of squares are separately authored composition probes; they are not presented as quoted lessons from the selected paragraphs."}
    return witness, extracts
