"""Read-only inference comparison; never updates or restarts the live learner."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kavi.language_curriculum import LETTERS, letters_case
from kavi.pathway_live import _safe_write_json
from kavi.wave_core import WaveLearner


def checkpoint(root):
    pointer = json.loads((root / "current.json").read_text(encoding="utf-8"))
    folder = (root / pointer["snapshot"]).resolve()
    if not folder.is_relative_to(root.resolve() / "snapshots"):
        raise ValueError("Checkpoint path escaped its snapshot directory.")
    path = folder / "learner.pt"
    if hashlib.sha256(path.read_bytes()).hexdigest() != pointer["sha256"]:
        raise ValueError("Checkpoint fingerprint mismatch.")
    progress = json.loads((folder / "teacher.json").read_text(encoding="utf-8"))
    return path, pointer, progress


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--older", type=Path, required=True)
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cases", type=int, default=64)
    args = parser.parse_args()
    if not 16 <= args.cases <= 128:
        parser.error("Use 16..128 questions per length.")
    repo = Path(__file__).resolve().parents[1]
    if not args.output.resolve().is_relative_to(repo / "runs"):
        parser.error("Assessment output must stay in ignored runs/.")
    old, new = checkpoint(args.older), checkpoint(args.current)
    excluded = set(old[2]["seen_questions"]) | set(new[2]["seen_questions"])
    rng = random.Random(202609041429)
    bank = {"familiar-single-letters": [letters_case(c) for c in LETTERS]}
    for length in (3, 4):
        rows = []
        while len(rows) < args.cases:
            q = letters_case("".join(rng.choice(LETTERS) for _ in range(length)))
            if q.key not in excluded:
                rows.append(q)
                excluded.add(q.key)
        bank[f"unseen-{length}-letters"] = rows
    report = {"schema": 1, "method": "Identical question-only inference; no optimizer updates.",
              "unseen_relative_to": "Union of both durable checkpoints' recorded exposure hashes.",
              "question_keys": {name: [q.key for q in rows] for name, rows in bank.items()},
              "results": []}
    for label, (path, pointer, _) in (("older", old), ("current", new)):
        core = WaveLearner.load(path)
        before, updates = core.fingerprint(), core.updates
        result = {"checkpoint": label, "sha256": pointer["sha256"], "updates": updates, "tests": {}}
        for name, rows in bank.items():
            answers = [core.generate(q.prefix, max_bytes=16) for q in rows]
            right = sum(q.correct(a) for q, a in zip(rows, answers))
            result["tests"][name] = {"correct": right, "total": len(rows), "accuracy": right / len(rows),
                                       "outputs": [{"question": q.prompt, "answer": a, "expected": q.answer}
                                                   for q, a in zip(rows, answers)]}
            print(f"{label}, {updates} updates | {name}: {right}/{len(rows)}", flush=True)
        if core.fingerprint() != before or core.updates != updates:
            raise AssertionError("Read-only assessment changed the model.")
        report["results"].append(result)
        del core
    _safe_write_json(args.output, report)
    print(f"Saved: {args.output}", flush=True)


if __name__ == "__main__":
    main()
