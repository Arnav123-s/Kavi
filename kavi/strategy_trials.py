"""Teacher recipes and sealed partitions for bounded, local comparison trials."""

from collections import Counter, defaultdict
from dataclasses import asdict
import random
import time

from .language_curriculum import LETTERS, letters_case
from .mixed_quizzes import OPERATIONS, exercise, task_name
from .teaching_comparison import _sample_sequences, written_sequence


STRATEGIES = ("mixed", "blocked", "reversal", "boundary", "spaced", "mistakes")
DESCRIPTIONS = {
    "mixed": "Independent examples mixed within small lesson groups.",
    "blocked": "Exactly the mixed teacher's examples, grouped by operation.",
    "reversal": "Different commands on a shared sequence and its reverse.",
    "boundary": "Append/prepend chains: first stays when appending, last stays when prepending.",
    "spaced": "Every fourth lesson revisits a lesson from three groups earlier.",
    "mistakes": "Select a wrong practice example from two candidates of the same operation and length.",
}


def make_plan(progress, previously_reserved, seed=943127):
    seen = set(progress["seen_questions"])
    used = set(previously_reserved)
    used |= {s[::-1] for s in tuple(used)}
    extra = sorted({c for lane in progress["multilingual_bridge"]["lanes"].values()
                    for c in lane["correct_characters"]})
    rng, partitions = random.Random(seed), {}
    for partition in ("teacher_selection", "pathway_selection", "confirmation"):
        bank = {}
        for length in (3, 4):
            strings = _sample_sequences(rng, 24, length, used=used, seen=seen)
            bank[f"primary_{length}"] = [exercise(op, s) for s in strings for op in OPERATIONS]
        strings = _sample_sequences(rng, 16, 5, used=used, seen=seen)
        bank["longer_transfer"] = [exercise(op, s) for s in strings for op in OPERATIONS]
        if extra:
            strings = _sample_sequences(rng, 16, 3, used=used, seen=seen, extras=extra)
            bank["script_transfer"] = [exercise(op, s) for s in strings for op in OPERATIONS]
        strings = _sample_sequences(rng, 24, 2, used=used, fresh=False)
        bank["retention_pairs"] = [letters_case(s) for s in strings]
        bank["retention_characters"] = [letters_case(c) for c in LETTERS + "".join(extra)]
        partitions[partition] = bank
    rehearsal = [letters_case(c) for c in LETTERS + "".join(extra)]
    for length in (2, 3):
        rehearsal += [letters_case(s) for s in _sample_sequences(rng, 24, length,
                                                                used=set(used), fresh=False)]
    return {"partitions": partitions, "rehearsal": rehearsal,
            "forbidden_sequences": sorted(used), "extra_characters": extra}


def serialize(plan):
    return {**plan, "partitions": {p: {k: [asdict(q) for q in rows] for k, rows in bank.items()}
                                    for p, bank in plan["partitions"].items()},
            "rehearsal": [asdict(q) for q in plan["rehearsal"]]}


def primary_score(scores):
    groups = [v for k, v in scores.items() if k.startswith("primary_")]
    return sum(v["correct"] for v in groups) / sum(v["total"] for v in groups)


def rank_results(records, field):
    """Retention first, then mean primary score; ties are deterministic."""
    grouped = defaultdict(list)
    for row in records:
        if row.get("state") != "complete":
            raise ValueError("Incomplete candidates cannot enter a ranking.")
        grouped[row[field]].append(row)
    result = []
    for name, rows in grouped.items():
        losses = [len(r["retention_losses"]) for r in rows]
        result.append({"name": name, "mean_primary": sum(primary_score(r["scores"]) for r in rows) / len(rows),
                       "mean_retention_losses": sum(losses) / len(losses),
                       "all_retention_preserved": not any(losses), "repetitions": len(rows)})
    result.sort(key=lambda r: (not r["all_retention_preserved"], r["mean_retention_losses"], -r["mean_primary"], r["name"]))
    return result


class TeachingRecipe:
    def __init__(self, strategy, seed, plan, steps=360):
        if strategy not in STRATEGIES or steps not in (180, 360, 720):
            raise ValueError("Unknown recipe or unsupported balanced budget.")
        self.strategy, self.plan = strategy, plan
        self.rng, self.review_rng = random.Random(seed), random.Random(seed + 1999)
        self.forbidden = set(plan["forbidden_sequences"])
        self.focus_steps = steps - steps // 5
        self.unit_count = self.focus_steps // 6
        self.position = 0
        common_rng = random.Random(seed + 311)
        common = [self._independent(common_rng) for _ in range(self.unit_count)]
        self.candidates = defaultdict(list)
        for unit in common:
            for q in unit:
                self.candidates[(task_name(q), len(written_sequence(q)))].append(q)
        if strategy in ("mixed", "mistakes"):
            units = common
        elif strategy == "blocked":
            flat = [q for unit in common for q in unit]
            self.rows = sorted(flat, key=lambda q: OPERATIONS.index(task_name(q)))
            return
        elif strategy == "spaced":
            units = [common[i-3] if i >= 3 and i % 4 == 3 else common[i]
                     for i in range(self.unit_count)]
        else:
            units = [self._paired(strategy) for _ in range(self.unit_count)]
        self.rows = [q for unit in units for q in unit]

    def _draw(self, rng, length):
        return _sample_sequences(rng, 1, length, used=set(self.forbidden), fresh=False)[0]

    def _independent(self, rng):
        rows = [exercise(op, self._draw(rng, length))
                for length in (2, 3, 4) for _ in range(2) for op in OPERATIONS]
        rng.shuffle(rows)
        return rows

    def _paired(self, strategy):
        if strategy == "boundary":
            for _ in range(2000):
                base = self._draw(self.rng, 4)
                strings = [base[:n] for n in (2, 3, 4)]
                if all(s not in self.forbidden and s[::-1] not in self.forbidden for s in strings):
                    break
            else:
                raise ValueError("Boundary practice pool exhausted.")
        else:
            strings = [self._draw(self.rng, length) for length in (2, 3, 4)]
        return [exercise(op, value) for s in strings for value in (s, s[::-1]) for op in OPERATIONS]

    def batch(self, step, core=None, check=lambda: None):
        metadata = {"probe_calls": 0, "probe_seconds": 0.0, "candidate_keys": []}
        if step % 5 == 4:
            return self.review_rng.sample(self.plan["rehearsal"], 4), {**metadata, "kind": "shared_review"}
        rows = self.rows[self.position:self.position + 4]
        self.position += 4
        if len(rows) != 4:
            raise ValueError("Teaching budget exhausted.")
        if self.strategy == "mistakes":
            if core is None:
                raise ValueError("Mistake-focused selection needs a read-only learner probe.")
            before, updates = core.fingerprint(), core.updates
            selected = []
            started = time.monotonic()
            for q in rows:
                pair = self.rng.sample(self.candidates[(task_name(q), len(written_sequence(q)))], 2)
                chosen = pair[0]
                for candidate in pair:
                    check()
                    answer = core.generate(candidate.prefix, max_bytes=24)
                    metadata["probe_calls"] += 1
                    metadata["candidate_keys"].append(candidate.key)
                    if not candidate.correct(answer):
                        chosen = candidate
                        break
                selected.append(chosen)
            rows = selected
            metadata["probe_seconds"] = time.monotonic() - started
            if core.fingerprint() != before or core.updates != updates:
                raise AssertionError("Practice selection updated the model.")
        if any(written_sequence(q) in self.forbidden for q in rows):
            raise AssertionError("A reserved assessment sequence entered practice.")
        return rows, {**metadata, "kind": self.strategy}


def exposure_counts(rows):
    return dict(Counter((task_name(q), len(written_sequence(q))) for q in rows))
