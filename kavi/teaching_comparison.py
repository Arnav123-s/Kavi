"""Bounded teacher-only comparison; never attaches to a live learner.

The random-mixed arm uses the current quiz style, not a replay of the entire
live teacher. Task counts and rehearsal are controlled to compare teaching
selection/order. All answer rules remain in the exercise generator and grader.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random

from .language_curriculum import LETTERS, LanguageExample, letters_case
from .mixed_quizzes import OPERATIONS, exercise, task_name


@dataclass(frozen=True)
class ComparisonConfig:
    steps: int = 384
    seeds: tuple[int, ...] = (43011, 43012, 43013)
    check_every: int = 64
    max_seconds: int = 600
    rest_ms: int = 5

    def __post_init__(self):
        if not 64 <= self.steps <= 768 or self.steps % 64:
            raise ValueError("Use 64..768 optimizer steps in multiples of 64.")
        if not 1 <= len(self.seeds) <= 3 or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("Use one to three distinct teaching seeds.")
        if self.check_every != 64 or not 30 <= self.max_seconds <= 1200:
            raise ValueError("Use 64-step checks and a 30..1200 second wall limit.")
        if not 0 <= self.rest_ms <= 100:
            raise ValueError("Pacing must be 0..100 milliseconds.")


def checkpoint(run_dir: Path):
    root = run_dir.resolve()
    pointer = json.loads((root / "current.json").read_text(encoding="utf-8"))
    folder = (root / pointer["snapshot"]).resolve()
    if not folder.is_relative_to(root / "snapshots"):
        raise ValueError("Checkpoint escaped its snapshot directory.")
    model = folder / "learner.pt"
    if hashlib.sha256(model.read_bytes()).hexdigest() != pointer["sha256"]:
        raise ValueError("Checkpoint fingerprint mismatch.")
    progress = json.loads((folder / "teacher.json").read_text(encoding="utf-8"))
    return model, pointer, progress


def written_sequence(q: LanguageExample) -> str:
    operation, value = q.prompt.split(" ", 1)
    return value.replace(" ", "") if operation == "Join" else value


def contrast_group(symbols: str) -> list[LanguageExample]:
    """Same content/different command, then same symbols/reversed order."""
    if len(symbols) < 2 or symbols[0] == symbols[-1]:
        raise ValueError("A contrast needs different first and last symbols.")
    reverse = symbols[::-1]
    return [exercise(op, seq) for op in ("first", "last") for seq in (symbols, reverse)] + [
        exercise(op, seq) for op in ("copy", "join") for seq in (symbols, reverse)]


def _sample_sequences(rng, count, length, *, used, seen=(), extras=(), fresh=True):
    """Bounded sampling: never spin forever on an exhausted short-string pool."""
    result, excluded = [], set(seen)
    for _ in range(max(1000, count * 500)):
        chars = rng.sample(LETTERS, length)
        if extras:
            chars[rng.randrange(length)] = rng.choice(extras)
        seq = "".join(chars)
        if seq in used or seq[::-1] in used:
            continue
        if fresh and any(exercise(op, s).key in excluded
                         for op in OPERATIONS for s in (seq, seq[::-1])):
            continue
        result.append(seq)
        used.update((seq, seq[::-1]))
        if len(result) == count:
            return result
    raise ValueError("The bounded comparison question pool was exhausted.")


def build_plan(progress: dict, seed: int = 942026):
    """Seal development/final partitions before seeing experimental outcomes."""
    seen = set(progress["seen_questions"])
    bridge = progress.get("multilingual_bridge", {})
    extras = sorted({c for lane in bridge.get("lanes", {}).values()
                     for c in lane.get("correct_characters", [])})
    used = {q["answer"] for bank in bridge.get("banks", {}).values() for q in bank}
    used |= {s[::-1] for s in tuple(used)}
    rng = random.Random(seed)
    development, final = {}, {}
    for length in (2, 3):
        strings = _sample_sequences(rng, 12, length, used=used, seen=seen, fresh=length > 2)
        development[str(length)] = [exercise(op, s) for s in strings for op in ("first", "last")]
    # Hold every underlying final string out of every automatic teaching task.
    for label, length, count, script in (("position_three", 3, 32, ()),
                                         ("position_four", 4, 32, ()),
                                         ("position_multiscript", 3, 16, extras)):
        if label == "position_multiscript" and not extras:
            continue
        strings = _sample_sequences(rng, count, length, used=used, seen=seen, extras=script)
        final[label] = [exercise(op, s) for s in strings for op in ("first", "last")]
    strings = _sample_sequences(rng, 16, 3, used=used, seen=seen)
    final["transfer_copy_join"] = [exercise(op, s) for s in strings for op in ("copy", "join")]
    # Two-letter combinations were exhausted by the live learner; no fresh label.
    strings = _sample_sequences(rng, 24, 2, used=used, fresh=False)
    final["retention_pairs"] = [letters_case(s) for s in strings]
    final["retention_characters"] = [letters_case(c) for c in LETTERS + "".join(extras)]
    rehearsal_strings = _sample_sequences(rng, 24, 2, used=set(used), fresh=False)
    rehearsal = [letters_case(c) for c in LETTERS + "".join(extras)] + [
        letters_case(s) for s in rehearsal_strings]
    return {"development": development, "final": final, "rehearsal": rehearsal,
            "forbidden_sequences": sorted(used), "extra_characters": extras,
            "notes": {"development_two": "Calibration; familiar strings allowed, never directly trained here.",
                      "final_novelty": "All four operation keys absent from frozen exposure ledger for each final non-retention string and its reverse.",
                      "transfer": "New combinations, not proof of English or native-language comprehension.",
                      "retention": "Only baseline-correct items count as protected; finite checks, not universal preservation."}}


class LessonSchedule:
    """Equal task frequencies, batch sizes and shared rehearsal in both arms."""

    def __init__(self, arm, seed, plan):
        if arm not in ("random_mixed", "contrast"):
            raise ValueError("Unknown teaching arm.")
        self.arm, self.plan = arm, plan
        self.rng, self.rehearsal_rng = random.Random(seed), random.Random(seed + 997)
        self.forbidden = set(plan["forbidden_sequences"])
        self.stage = 2
        self.pending = []

    def observe_development(self, scores):
        if self.arm == "contrast" and self.stage == 2:
            tasks = scores["2"]["per_task"]
            if all(tasks[k]["accuracy"] >= 0.9 for k in ("first", "last")):
                self.stage = 3
                # Preserve pending tasks so operator budgets stay identical.
                return True
        return False

    def batch(self, step):
        if step % 5 == 4:
            return self.rehearsal_rng.sample(self.plan["rehearsal"], 4), "shared_rehearsal"
        if not self.pending:
            if self.arm == "contrast":
                seq = _sample_sequences(self.rng, 1, self.stage,
                                        used=set(self.forbidden), fresh=False)[0]
                self.pending = contrast_group(seq)
            else:
                # Independent mixed examples, like the current quiz sampler.
                strings = _sample_sequences(self.rng, 8, 3, used=set(self.forbidden), fresh=False)
                tasks = ("first", "first", "last", "last", "copy", "copy", "join", "join")
                rows = [exercise(op, s) for op, s in zip(tasks, strings)]
                positions, copying = rows[:4], rows[4:]
                self.rng.shuffle(positions)
                self.rng.shuffle(copying)
                self.pending = positions + copying
        rows, self.pending = self.pending[:4], self.pending[4:]
        if any(written_sequence(q) in self.forbidden for q in rows):
            raise AssertionError("An assessment string entered teaching.")
        return rows, "contrast_" + str(self.stage) if self.arm == "contrast" else "random_mixed_three"


def evaluate(core, banks, *, check=lambda: None):
    """Question-only generation: no grading helpers run inside the model."""
    before, updates = core.fingerprint(), core.updates
    result = {}
    for name, rows in banks.items():
        outputs, correct, total = [], Counter(), Counter()
        for q in rows:
            check()
            actual = core.generate(q.prefix, max_bytes=24)
            good, task = q.correct(actual), task_name(q)
            correct[task] += good
            total[task] += 1
            outputs.append({"question": q.prompt, "key": q.key, "expected": q.answer,
                            "actual": actual, "correct": good})
        result[name] = {"correct": sum(correct.values()), "total": len(rows),
                        "accuracy": sum(correct.values()) / len(rows), "outputs": outputs,
                        "per_task": {task: {"correct": correct[task], "total": n,
                                            "accuracy": correct[task] / n} for task, n in total.items()}}
    if core.fingerprint() != before or core.updates != updates:
        raise AssertionError("Evaluation altered model parameters or update count.")
    return result


def retention_losses(baseline, final):
    protected = {row["key"] for name, group in baseline.items() if name.startswith("retention_")
                 for row in group["outputs"] if row["correct"]}
    now = {row["key"] for name, group in final.items() if name.startswith("retention_")
           for row in group["outputs"] if row["correct"]}
    return sorted(protected - now)


def serialize_plan(plan):
    return {**plan, "development": {k: [asdict(q) for q in v] for k, v in plan["development"].items()},
            "final": {k: [asdict(q) for q in v] for k, v in plan["final"].items()},
            "rehearsal": [asdict(q) for q in plan["rehearsal"]]}
