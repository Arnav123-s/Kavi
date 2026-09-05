"""Compare ordinary updates with eight small contextual repair connections."""

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
import random
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch

from kavi.pathway_live import _safe_write_json
from kavi.flow_preservation import learn_with_rehearsal
from kavi.pathway_trials import TrialLearner
from kavi.repair_trials import RepairLearner
from kavi.strategy_trials import TeachingRecipe, make_plan, primary_score, rank_results, serialize
from kavi.teaching_comparison import evaluate, retention_losses
from kavi.trial_resources import memory_reading, parallel_rows


MODES = ("ordinary", "adapter_joint", "flow_repair")


def changes(before, after):
    old = {row["key"]: row["correct"] for name, group in before.items()
           if name.startswith("primary_") for row in group["outputs"]}
    now = {row["key"]: row["correct"] for name, group in after.items()
           if name.startswith("primary_") for row in group["outputs"]}
    if old.keys() != now.keys():
        raise ValueError("Repair/break counts need identical questions.")
    return {"newly_correct": sum(now[k] and not v for k, v in old.items()),
            "newly_wrong": sum(v and not now[k] for k, v in old.items())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent-experiment", type=Path, required=True)
    parser.add_argument("--live-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    source, live, root = args.parent_experiment.resolve(), args.live_run.resolve(), args.output.resolve()
    if root.exists() or root == repo / "runs" or not root.is_relative_to(repo / "runs"):
        parser.error("Use a new private directory under runs.")
    if not live.is_relative_to(repo / "runs") or not (live / "pause").exists():
        parser.error("Live teaching must stay paused.")
    parent_report = json.loads((source / "report.json").read_text(encoding="utf-8"))
    if parent_report["state"] != "complete":
        parser.error("Wait for the earlier experiment to complete; do not run candidate experiments concurrently.")
    previous = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    teacher = parent_report["teacher_ranking"][0]["name"]
    progress = json.loads((source / "input-teacher.json").read_text(encoding="utf-8"))
    plan = make_plan(progress, previous["plan"]["forbidden_sequences"], seed=947731)
    digest = hashlib.sha256((source / "input.pt").read_bytes()).hexdigest()
    if digest != previous["source_sha256"]:
        raise ValueError("Parent checkpoint hash mismatch.")
    root.mkdir(parents=True, exist_ok=False)
    frozen = root / "input.pt"
    shutil.copyfile(source / "input.pt", frozen)
    steps, seeds = 180, (53121, 53122, 53123)
    paths = ("kavi/repair_trials.py", "kavi/flow_preservation.py", "kavi/pathway_trials.py", "kavi/wave_core.py",
             "kavi/strategy_trials.py", "kavi/teaching_comparison.py", "kavi/trial_resources.py",
             "kavi/mixed_quizzes.py", "kavi/language_curriculum.py", "scripts/run-repair-trials.py")
    _safe_write_json(root / "manifest.json", {
        "schema": 1, "source_sha256": digest, "teacher_from_prior_selection": teacher,
        "modes": MODES, "seeds": seeds, "steps": steps, "examples_per_update": 8,
        "objective": "Four focus and four common reference examples; all base parameters remain trainable. Flow repair additionally projects the Adam displacement against the reference loss gradient.",
        "slots": 8, "extra_parameters": 56, "plan": serialize(plan),
        "selection": "Retention first, then fewer lost old answers, then mean primary score; no deployment.",
        "confirmation": "Evaluate ALL three methods after sealing the selection, no subsequent training.",
        "unused_partition": "pathway_selection is reserved but unused in this repair experiment",
        "resource_policy": {"numerical_threads": 1, "candidate_processes": 1, "max_seconds": 1200,
                            "min_available_gib": 2, "max_working_set_gib": 1, "rest_ms": 10,
                            "temperature_measured": False},
        "code_sha256": {p: hashlib.sha256((repo / p).read_bytes()).hexdigest() for p in paths}})
    started, cpu_started, sampled_at = time.monotonic(), time.process_time(), 0.0
    reading = memory_reading()
    report = {"state": "running", "strategy": teacher, "candidates": [], "confirmation": []}

    def emit(kind, **data):
        with (root / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"kind": kind, "seconds": time.monotonic()-started, **data}) + "\n")
        if "display" in data:
            print(data["display"], flush=True)

    def save():
        report.update(wall_seconds=time.monotonic()-started, process_cpu_seconds=time.process_time()-cpu_started,
                      memory=memory_reading(), artifact_bytes=sum(p.stat().st_size for p in root.rglob("*") if p.is_file()))
        _safe_write_json(root / "report.json", report)

    def check():
        nonlocal sampled_at, reading
        if (root / "stop.request").exists() or not (live / "pause").exists():
            raise InterruptedError("Experiment stopped without modifying live training.")
        if time.monotonic()-started >= 1200:
            raise InterruptedError("Bounded repair experiment time exhausted.")
        if time.monotonic()-sampled_at >= 2:
            reading, sampled_at = memory_reading(), time.monotonic()
            if shutil.disk_usage(root).free < 2 * 1024**3:
                raise InterruptedError("Free disk below 2 GiB.")
            if reading["available_bytes"] is not None and reading["available_bytes"] < 2 * 1024**3:
                raise InterruptedError("Available RAM below 2 GiB.")
            if reading["working_set_bytes"] is not None and reading["working_set_bytes"] > 1024**3:
                raise InterruptedError("Experiment working set above 1 GiB.")

    def load(mode="ordinary", path=frozen):
        core = TrialLearner.load(path) if mode == "ordinary" else RepairLearner.load(path)
        core.config = replace(core.config, threads=1)
        core.network.config = core.config
        torch.set_num_threads(1)
        return core

    def assess(core, partition):
        return evaluate(core, plan["partitions"][partition], check=check)

    try:
        check()
        core = load()
        base_hash, initial_updates = core.fingerprint(), core.updates
        report["baseline_selection"] = assess(core, "teacher_selection")
        report["initial_ledger"] = core.ledger()
        del core
        emit("start", display=f"KAVI SMALL REPAIR TRIALS: eight extra connections, teacher {teacher}. Live remains PAUSED.")
        for i, seed in enumerate(seeds):
            for mode in MODES[i:] + MODES[:i]:
                core = load()
                if mode != "ordinary":
                    core = RepairLearner.from_parent(core, mode="adapter_joint")
                recipe, widths, training_seconds = TeachingRecipe(teacher, seed, plan, steps), Counter(), 0.0
                reference_rng, projected_updates = random.Random(seed+7003), 0
                probe_calls, probe_seconds = 0, 0.0
                emit("trial_start", display=f"TRAIN {mode}/{seed}: {steps} updates, frozen start")
                for step in range(steps):
                    check()
                    core.parallel_rows = parallel_rows(reading)
                    rows, metadata = recipe.batch(step, core, check)
                    reference = reference_rng.sample(plan["rehearsal"], 4)
                    probe_calls += metadata["probe_calls"]
                    probe_seconds += metadata["probe_seconds"]
                    widths[core.parallel_rows] += 1
                    began = time.monotonic()
                    event = learn_with_rehearsal(core, [(q.prefix, q.answer) for q in rows],
                                                [(q.prefix, q.answer) for q in reference],
                                                project=mode == "flow_repair")
                    projected_updates += event["projected"]
                    training_seconds += time.monotonic()-began
                    emit("learning", mode=mode, seed=seed, step=step+1, **event)
                    time.sleep(0.01)
                    if (step+1) % 60 == 0:
                        emit("progress", display=f"{mode}/{seed}: {step+1}/{steps}")
                if core.updates != initial_updates + steps:
                    raise AssertionError("Update budget changed.")
                scores = assess(core, "teacher_selection")
                result = {"state": "complete", "strategy": teacher, "variant": mode, "seed": seed,
                          "scores": scores, "retention_losses": retention_losses(report["baseline_selection"], scores),
                          "primary_changes": changes(report["baseline_selection"], scores),
                          "ledger": core.ledger(), "training_seconds": training_seconds,
                          "practice_probe_calls": probe_calls, "practice_probe_seconds": probe_seconds,
                          "parallel_row_counts": dict(widths), "presentations": steps*8,
                          "projected_updates": projected_updates,
                          "base_unchanged": (core.fingerprint() if mode == "ordinary" else core.base_fingerprint()) == base_hash}
                if result["ledger"]["parameters"] > report["initial_ledger"]["parameters"] + 56:
                    raise AssertionError("Small-repair capacity budget exceeded.")
                path = root / f"{mode}-{seed}.pt"
                core.save(path)
                result["checkpoint"], result["fingerprint"] = path.name, core.fingerprint()
                del core
                restored = load(mode, path)
                if restored.fingerprint() != result["fingerprint"]:
                    raise AssertionError("Repair checkpoint did not round trip.")
                del restored
                report["candidates"].append(result)
                emit("trial_done", display=f"DONE {mode}/{seed}: primary {primary_score(scores):.1%}, old answers lost {len(result['retention_losses'])}")
                save()
        report["selection_ranking"] = rank_results(report["candidates"], "variant")
        _safe_write_json(root / "selection.json", {"ranking": report["selection_ranking"], "finalists": MODES})
        core = load()
        report["baseline_confirmation"] = assess(core, "confirmation")
        del core
        for trained in report["candidates"]:
            core = load(trained["variant"], root / trained["checkpoint"])
            scores = assess(core, "confirmation")
            result = {"strategy": teacher, "variant": trained["variant"], "seed": trained["seed"],
                      "scores": scores, "retention_losses": retention_losses(report["baseline_confirmation"], scores),
                      "primary_changes": changes(report["baseline_confirmation"], scores)}
            report["confirmation"].append(result)
            del core
            emit("confirmation", display=f"FINAL {result['variant']}/{result['seed']}: primary {primary_score(scores):.1%}, repairs/breaks {result['primary_changes']}, retention losses {len(result['retention_losses'])}")
            save()
        report["state"] = "complete"
        emit("complete", display="COMPLETE. All candidates remain experimental. No live model replaced.")
    except (KeyboardInterrupt, InterruptedError) as error:
        report["state"], report["reason"] = "incomplete", str(error) or "Interrupted"
    except Exception as error:
        report["state"], report["error"] = "failed", repr(error)
        raise
    finally:
        report["live_pause_exists"] = (live / "pause").exists()
        report["input_unchanged"] = hashlib.sha256(frozen.read_bytes()).hexdigest() == digest
        save()
    return 0 if report["state"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
