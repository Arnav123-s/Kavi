"""Bounded repair-forward comparison: continue the latest, never roll it back."""

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch

from kavi.flow_preservation import learn_with_rehearsal
from kavi.forward_repair import (ForwardLearner, choose_jump, correct_keys,
                                 feedback_batch, preservation)
from kavi.pathway_live import _safe_write_json
from kavi.pathway_trials import TrialLearner
from kavi.repair_trials import RepairLearner
from kavi.strategy_trials import make_plan, serialize
from kavi.teaching_comparison import evaluate
from kavi.trial_resources import memory_reading, parallel_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--reserved-manifest", type=Path, required=True)
    parser.add_argument("--teacher-ledger", type=Path, required=True)
    parser.add_argument("--live-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    source, root, live = args.source.resolve(), args.output.resolve(), args.live_run.resolve()
    if root.exists() or root == repo/"runs" or not root.is_relative_to(repo/"runs"):
        parser.error("Use a new ignored output directory under runs.")
    if not live.is_relative_to(repo/"runs") or not (live/"pause").exists():
        parser.error("The existing live learner must remain paused.")
    previous = json.loads((source/"report.json").read_text(encoding="utf-8"))
    source_manifest = json.loads((source/"manifest.json").read_text(encoding="utf-8"))
    if previous["state"] != "complete":
        parser.error("Source comparison must be complete.")
    # Chronological last trained direction, not selected using final accuracy.
    latest_record = previous["candidates"][-1]
    if latest_record["variant"] not in ("adapter_joint", "flow_repair"):
        parser.error("This bounded protocol starts from the latest repair-format candidate.")
    latest_path = (source/latest_record["checkpoint"]).resolve()
    if not latest_path.is_relative_to(source):
        parser.error("Latest checkpoint escaped the source experiment.")
    reserved = json.loads(args.reserved_manifest.read_text(encoding="utf-8"))
    ledger = json.loads(args.teacher_ledger.read_text(encoding="utf-8"))
    plan = make_plan(ledger, reserved["plan"]["forbidden_sequences"], seed=993071)
    old_digest = hashlib.sha256((source/"input.pt").read_bytes()).hexdigest()
    if old_digest != source_manifest["source_sha256"]:
        raise ValueError("Original checkpoint hash changed.")
    latest_digest = hashlib.sha256(latest_path.read_bytes()).hexdigest()
    steps, seeds = 120, (64121, 64122, 64123)
    root.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(source/"input.pt", root/"old.pt")
    shutil.copyfile(latest_path, root/"latest.pt")
    paths = ("kavi/forward_repair.py", "kavi/flow_preservation.py", "kavi/repair_trials.py",
             "kavi/pathway_trials.py", "kavi/wave_core.py", "kavi/strategy_trials.py",
             "kavi/teaching_comparison.py", "kavi/trial_resources.py",
             "kavi/mixed_quizzes.py", "kavi/language_curriculum.py", "scripts/run-forward-repair.py")
    _safe_write_json(root/"manifest.json", {
        "schema": 1, "old_sha256": old_digest, "latest_sha256": latest_digest,
        "latest_record": {k: latest_record[k] for k in ("variant", "seed", "checkpoint", "fingerprint")},
        "plan": serialize(plan), "seeds": seeds, "steps": steps,
        "modes": ["reuse", "one_jump"], "learning_rate": 0.0003,
        "feedback": "teacher_selection is explicitly feedback/TRAINING, reassessed every 40 steps. Four correction rows and four old/latest success rows per update.",
        "selection": "pathway_selection is never trained. Rank modes by mean union losses, then new connection count, then total correct. No candidate is rolled back during repair.",
        "confirmation": "Evaluate ALL six final iterates only after sealing mode selection; never select an earlier repair checkpoint.",
        "shortest_scope": "Compare zero versus one additional evaluated link, not a global shortest correct computation.",
        "resource_policy": {"threads": 1, "max_seconds": 900, "rest_ms": 10,
                            "min_available_gib": 2, "max_working_set_gib": 1},
        "code_sha256": {p: hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in paths}})
    started, cpu_started, sampled_at = time.monotonic(), time.process_time(), 0.0
    reading = memory_reading()
    report = {"state": "running", "candidates": [], "confirmation": []}

    def save():
        report.update(wall_seconds=time.monotonic()-started,
                      process_cpu_seconds=time.process_time()-cpu_started,
                      memory=memory_reading(),
                      artifact_bytes=sum(p.stat().st_size for p in root.rglob("*") if p.is_file()))
        _safe_write_json(root/"report.json", report)

    def emit(kind, **data):
        with (root/"events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"kind": kind, "seconds": time.monotonic()-started, **data})+"\n")
        if "display" in data:
            print(data["display"], flush=True)

    def check():
        nonlocal reading, sampled_at
        if (root/"stop.request").exists() or not (live/"pause").exists():
            raise InterruptedError("Stop requested or live learner unpaused.")
        if time.monotonic()-started >= 900:
            raise InterruptedError("Forward-repair experiment reached its time budget.")
        if time.monotonic()-sampled_at >= 2:
            reading, sampled_at = memory_reading(), time.monotonic()
            if ((reading["available_bytes"] is not None and reading["available_bytes"] < 2*1024**3)
                    or (reading["working_set_bytes"] is not None and reading["working_set_bytes"] > 1024**3)
                    or shutil.disk_usage(root).free < 2*1024**3):
                raise InterruptedError("Forward-repair resource ceiling reached.")

    def load_latest():
        core = RepairLearner.load(root/"latest.pt")
        core.config = replace(core.config, threads=1)
        core.network.config = core.config
        torch.set_num_threads(1)
        if core.fingerprint() != latest_record["fingerprint"]:
            raise ValueError("Latest candidate fingerprint changed.")
        return core

    def assess(core, partition):
        return evaluate(core, plan["partitions"][partition], check=check)

    try:
        check()
        old = TrialLearner.load(root/"old.pt")
        old.config = replace(old.config, threads=1)
        old.network.config = old.config
        torch.set_num_threads(1)
        latest = load_latest()
        report["old_feedback"], report["latest_feedback"] = assess(old, "teacher_selection"), assess(latest, "teacher_selection")
        report["old_selection"], report["latest_selection"] = assess(old, "pathway_selection"), assess(latest, "pathway_selection")
        report["initial_ledger"] = latest.ledger()
        old_keys, latest_keys = correct_keys(report["old_feedback"]), correct_keys(report["latest_feedback"])
        questions = [q for group in plan["partitions"]["teacher_selection"].values() for q in group]
        initial = preservation(report["old_feedback"], report["latest_feedback"], report["latest_feedback"])
        emit("start", display=f"KAVI REPAIR FORWARD: latest {latest_record['variant']}/{latest_record['seed']}, full configuration. Feedback old losses {initial['old_lost']}; protect old and latest successes. Live remains PAUSED.")
        for index, seed in enumerate(seeds):
            modes = ("reuse", "one_jump") if index % 2 == 0 else ("one_jump", "reuse")
            for mode in modes:
                check()
                base = load_latest()
                rng = random.Random(seed)
                focus, reference = feedback_batch(rng, questions, old_keys, latest_keys, latest_keys)
                jump, event, probe_seconds = None, None, 0.0
                if mode == "one_jump":
                    begin = time.monotonic()
                    jump, event = choose_jump(base, [(q.prefix, q.answer) for q in focus],
                                               [(q.prefix, q.answer) for q in reference])
                    probe_seconds = time.monotonic()-begin
                core = ForwardLearner.from_latest(base, [] if jump is None else [jump])
                core.config = replace(core.config, learning_rate=0.0003, threads=1)
                core.network.config = core.config
                for group in core.optimizer.param_groups:
                    group["lr"] = core.config.learning_rate
                initial_updates, initial_fingerprint = core.updates, core.fingerprint()
                record = {"mode": mode, "seed": seed, "jump": jump, "jump_selection": event,
                          "probe_seconds": probe_seconds, "history": [], "training_seconds": 0.0,
                          "inference_start": "full latest configuration; zero-effect additions only"}
                current_keys = set(latest_keys)
                emit("candidate", display=f"TRAIN {mode}/{seed}: 120 forward updates, jump {jump}; no rollback")
                for step in range(steps):
                    check()
                    core.parallel_rows = parallel_rows(reading)
                    focus, reference = feedback_batch(rng, questions, old_keys, latest_keys, current_keys)
                    before = time.monotonic()
                    loss = learn_with_rehearsal(core, [(q.prefix, q.answer) for q in focus],
                                               [(q.prefix, q.answer) for q in reference], project=False)
                    record["training_seconds"] += time.monotonic()-before
                    emit("learning", mode=mode, seed=seed, step=step+1, **loss)
                    time.sleep(0.01)
                    if (step+1) % 40 == 0:
                        scores = assess(core, "teacher_selection")
                        current_keys = correct_keys(scores)
                        counts = preservation(report["old_feedback"], report["latest_feedback"], scores)
                        record["history"].append({"step": step+1, **counts})
                        emit("feedback", mode=mode, seed=seed, step=step+1, **counts,
                             display=f"FEEDBACK {mode}/{seed} step {step+1}: old lost {counts['old_lost']}, latest lost {counts['latest_lost']}, total correct {counts['current_correct']}/419. Continue from THIS configuration.")
                if core.updates != initial_updates+steps:
                    raise AssertionError("Forward-update budget mismatch.")
                record.update(state="complete", ledger=core.ledger(),
                              initial_fingerprint=initial_fingerprint, fingerprint=core.fingerprint(),
                              updates=steps, presentations=steps*8,
                              scores=assess(core, "pathway_selection"))
                record["preservation"] = preservation(report["old_selection"], report["latest_selection"], record["scores"])
                path = root/f"{mode}-{seed}.pt"
                core.save(path)
                record["checkpoint"] = path.name
                report["candidates"].append(record)
                emit("selection_result", mode=mode, seed=seed, **record["preservation"])
                del core, base
                save()
        rankings = []
        for mode in ("reuse", "one_jump"):
            rows = [r for r in report["candidates"] if r["mode"] == mode]
            rankings.append({"mode": mode, "mean_union_lost": sum(r["preservation"]["union_lost"] for r in rows)/3,
                             "mean_correct": sum(r["preservation"]["current_correct"] for r in rows)/3,
                             "extra_connections": int(mode == "one_jump")})
        rankings.sort(key=lambda r: (r["mean_union_lost"], r["extra_connections"], -r["mean_correct"]))
        report["selection"] = rankings
        _safe_write_json(root/"selection.json", {"ranking": rankings, "final_iterates_only": True})
        emit("choice", display=f"SEALED MODE CHOICE: {rankings[0]['mode']}. Now opening untouched confirmation; both methods remain reported.")
        report["old_confirmation"], report["latest_confirmation"] = assess(old, "confirmation"), assess(latest, "confirmation")
        for record in report["candidates"]:
            core = ForwardLearner.load(root/record["checkpoint"])
            if core.fingerprint() != record["fingerprint"]:
                raise AssertionError("Forward candidate failed checkpoint round trip.")
            scores = assess(core, "confirmation")
            counts = preservation(report["old_confirmation"], report["latest_confirmation"], scores)
            report["confirmation"].append({"mode": record["mode"], "seed": record["seed"],
                                           "scores": scores, "preservation": counts})
            emit("final", mode=record["mode"], seed=record["seed"], **counts,
                 display=f"FINAL {record['mode']}/{record['seed']}: old lost {counts['old_lost']}, latest lost {counts['latest_lost']}, union lost {counts['union_lost']}, correct {counts['current_correct']}/419")
            del core
        report["state"] = "complete"
        emit("complete", display="COMPLETE: no old checkpoint restored, no candidate promoted to live, no final answers used for more training.")
    except (KeyboardInterrupt, InterruptedError) as error:
        report["state"], report["reason"] = "incomplete", str(error) or "Interrupted"
    except Exception as error:
        report["state"], report["error"] = "failed", repr(error)
        raise
    finally:
        report["live_pause_exists"] = (live/"pause").exists()
        report["old_unchanged"] = hashlib.sha256((root/"old.pt").read_bytes()).hexdigest() == old_digest
        report["latest_unchanged"] = hashlib.sha256((root/"latest.pt").read_bytes()).hexdigest() == latest_digest
        save()
    return 0 if report["state"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
