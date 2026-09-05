"""Serial teacher/plasticity trials with separate selection and final tests."""

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch

from kavi.mixed_quizzes import task_name
from kavi.pathway_live import _safe_write_json
from kavi.pathway_trials import TrialLearner, VARIANTS
from kavi.strategy_trials import (DESCRIPTIONS, STRATEGIES, TeachingRecipe, make_plan,
                                 primary_score, rank_results, serialize)
from kavi.teaching_comparison import evaluate, retention_losses, written_sequence
from kavi.trial_resources import memory_reading, parallel_rows


class TrialStopped(Exception):
    pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frozen-experiment", type=Path, required=True)
    parser.add_argument("--live-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=360, choices=(180, 360, 720))
    parser.add_argument("--seeds", type=int, nargs="+", default=(53101, 53102, 53103))
    parser.add_argument("--max-seconds", type=int, default=1800)
    args = parser.parse_args()
    if not 1 <= len(args.seeds) <= 3 or len(set(args.seeds)) != len(args.seeds) or not 60 <= args.max_seconds <= 1800:
        parser.error("Use one to three distinct seeds and at most 1800 seconds.")
    repo = Path(__file__).resolve().parents[1]
    source, root, live = args.frozen_experiment.resolve(), args.output.resolve(), args.live_run.resolve()
    if not root.is_relative_to(repo / "runs") or root == repo / "runs" or root.exists():
        parser.error("Use a new output directory under the ignored runs folder.")
    if not live.is_relative_to(repo / "runs") or not (live / "pause").exists():
        parser.error("The separately controlled live run must remain paused.")
    previous = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    digest = previous["checkpoint"]["sha256"]
    if hashlib.sha256((source / "input.pt").read_bytes()).hexdigest() != digest:
        raise ValueError("Frozen source checkpoint hash mismatch.")
    progress = json.loads((source / "input-teacher.json").read_text(encoding="utf-8"))
    plan = make_plan(progress, previous["plan"]["forbidden_sequences"])
    root.mkdir(parents=True, exist_ok=False)
    frozen = root / "input.pt"
    shutil.copyfile(source / "input.pt", frozen)
    _safe_write_json(root / "input-teacher.json", progress)
    paths = ("kavi/strategy_trials.py", "kavi/pathway_trials.py", "kavi/trial_resources.py",
             "kavi/teaching_comparison.py", "kavi/wave_core.py", "kavi/mixed_quizzes.py",
             "kavi/language_curriculum.py", "scripts/run-strategy-trials.py")
    order = [(seed, strategy) for i, seed in enumerate(args.seeds)
             for strategy in STRATEGIES[i:] + STRATEGIES[:i]]
    manifest = {"schema": 1, "steps_per_trial": args.steps, "seeds": args.seeds,
                "source_sha256": digest, "source_updates": previous["checkpoint"]["ledger"]["updates"],
                "teaching_recipes": DESCRIPTIONS, "teacher_order": order, "variants": VARIANTS,
                "topology_change_at_update": args.steps // 2,
                "code_sha256": {p: hashlib.sha256((repo / p).read_bytes()).hexdigest() for p in paths},
                "selection": "Retention-preserving across all seeds first; then fewer lost answers, then higher primary score. If none preserve retention, selection is exploratory only.",
                "confirmation": "After both selections are sealed, test mixed baseline, two leading teachers with standard plasticity, and selected teacher with selected plasticity. Do not tune or resume training on final answers.",
                "resource_policy": {"simultaneous_candidates": 1, "numerical_threads": 1,
                                    "example_rows": "4/2/1 from memory headroom; accumulate to four-example optimizer updates",
                                    "max_seconds": args.max_seconds, "min_free_disk_gib": 2,
                                    "min_available_ram_gib": 2, "max_process_working_set_gib": 1,
                                    "rest_ms": 10, "cpu_temperature": "not measured; no hardware thresholds changed"},
                "plan": serialize(plan)}
    _safe_write_json(root / "manifest.json", manifest)
    started, cpu_started = time.monotonic(), time.process_time()
    report = {"schema": 1, "state": "running", "teachers": [], "pathways": [], "confirmation": []}
    reading, sampled_at = memory_reading(), 0.0

    def emit(kind, **data):
        record = {"kind": kind, "seconds": time.monotonic() - started, **data}
        with (root / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
        if "display" in data:
            print(data["display"], flush=True)

    def save():
        report["wall_seconds"] = time.monotonic() - started
        report["process_cpu_seconds"] = time.process_time() - cpu_started
        report["memory"] = memory_reading()
        report["artifact_bytes_before_report_write"] = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
        _safe_write_json(root / "report.json", report)

    def check():
        nonlocal reading, sampled_at
        if (root / "stop.request").exists() or not (live / "pause").exists():
            raise TrialStopped("Stop requested or owner resumed live training; experiment stopped without changing the live run.")
        if time.monotonic() - started >= args.max_seconds:
            raise TrialStopped("Bounded experiment time exhausted; incomplete trials are not ranked.")
        if time.monotonic() - sampled_at >= 2:
            reading, sampled_at = memory_reading(), time.monotonic()
            if shutil.disk_usage(root).free < 2 * 1024 ** 3:
                raise TrialStopped("Free disk below 2 GiB.")
            if reading["available_bytes"] is not None and reading["available_bytes"] < 2 * 1024 ** 3:
                raise TrialStopped("Available memory below 2 GiB.")
            if reading["working_set_bytes"] is not None and reading["working_set_bytes"] > 1024 ** 3:
                raise TrialStopped("Experiment working set exceeded 1 GiB.")

    def load(path=frozen):
        core = TrialLearner.load(path)
        core.config = replace(core.config, threads=1)
        core.network.config = core.config
        torch.set_num_threads(1)
        return core

    def measure(core, partition):
        return evaluate(core, plan["partitions"][partition], check=check)

    def train(strategy, variant, seed, baseline, partition):
        check()
        core = load()
        if core.fingerprint() != report["initial"]["fingerprint"]:
            raise AssertionError("A candidate did not start from the frozen model.")
        core.variant = variant
        recipe = TeachingRecipe(strategy, seed, plan, args.steps)
        counts, lengths, widths, unique, candidate_keys = Counter(), Counter(), Counter(), set(), set()
        curves, training_seconds, probes, probe_seconds, prefix_bytes, answer_bytes = [], 0.0, 0, 0.0, 0, 0
        label = f"{strategy}/{variant}/{seed}"
        emit("trial_start", display=f"\nTRAIN {label}: {args.steps} updates, same frozen start", candidate=label)
        for step in range(args.steps):
            check()
            core.parallel_rows = parallel_rows(reading)
            if step == args.steps // 2:
                core.apply_scheduled_change()
                if core.adaptations:
                    emit("pathway_change", candidate=label, step=step, changes=core.adaptations,
                         display=f"PATH CHANGE {label}: {core.adaptations[-1]}")
            batch, metadata = recipe.batch(step, core, check)
            counts.update(task_name(q) for q in batch)
            if metadata["kind"] != "shared_review":
                lengths.update(len(written_sequence(q)) for q in batch)
            widths[core.parallel_rows] += 1
            unique.update(q.key for q in batch)
            candidate_keys.update(metadata["candidate_keys"])
            probes += metadata["probe_calls"]
            probe_seconds += metadata["probe_seconds"]
            prefix_bytes += sum(len(q.prefix.encode()) for q in batch)
            answer_bytes += sum(len((q.answer + "\n").encode()) for q in batch)
            began = time.monotonic()
            metrics = core.learn_answers([(q.prefix, q.answer) for q in batch])
            training_seconds += time.monotonic() - began
            emit("learning", candidate=label, step=step+1, loss=metrics["loss"], rows=core.parallel_rows,
                 examples=[{"question": q.prompt, "answer": q.answer, "key": q.key} for q in batch])
            time.sleep(0.01)
            if (step+1) % 120 == 0:
                small = {name: rows[:8] for name, rows in plan["partitions"][partition].items() if name.startswith("primary_")}
                observation = evaluate(core, small, check=check)
                curves.append({"updates": step+1, "score": primary_score(observation)})
                emit("progress", display=f"{label}: {step+1}/{args.steps}, repeated selection probe {primary_score(observation):.1%}, links {core.config.nodes * core.config.fan_in}")
        scores = measure(core, partition)
        losses = retention_losses(baseline, scores)
        ledger = core.ledger()
        if core.updates != report["initial"]["updates"] + args.steps or ledger["parameters"] > report["initial"]["ledger"]["parameters"] + 256:
            raise AssertionError("Update or growth budget exceeded.")
        path = root / f"{strategy}-{variant}-{seed}.pt"
        core.save(path)
        restored = load(path)
        if restored.fingerprint() != core.fingerprint():
            raise AssertionError("Candidate did not survive checkpoint round trip.")
        result = {"state": "complete", "strategy": strategy, "variant": variant, "seed": seed,
                  "scores": scores, "retention_losses": losses, "checkpoint": path.name,
                  "fingerprint": core.fingerprint(), "steps": args.steps, "presentations": args.steps * 4,
                  "unique_training_questions": len(unique), "unique_probed_questions": len(candidate_keys),
                  "task_counts": dict(counts), "focus_length_counts": dict(lengths),
                  "parallel_row_counts": dict(widths), "training_seconds": training_seconds,
                  "practice_probe_calls": probes, "practice_probe_seconds": probe_seconds,
                  "prefix_bytes": prefix_bytes, "answer_bytes": answer_bytes,
                  "curves": curves, "ledger": ledger, "pathway_changes": core.adaptations}
        emit("trial_done", candidate=label, display=f"DONE {label}: primary {primary_score(scores):.1%}, lost old answers {len(losses)}, parameters {ledger['parameters']}")
        del restored, core
        return result

    emit("start", display=f"KAVI METHOD + PATHWAY TRIALS\nLive teaching stays PAUSED. Serial candidates, one CPU thread.\nPrivate output: {root}")
    try:
        core = load()
        report["initial"] = {"fingerprint": core.fingerprint(), "updates": core.updates, "ledger": core.ledger()}
        report["baseline_teacher"] = measure(core, "teacher_selection")
        del core
        for seed, strategy in order:
            report["teachers"].append(train(strategy, "standard", seed, report["baseline_teacher"], "teacher_selection"))
            save()
        # Match actual data/length budgets, not just a nominal number of steps.
        first = report["teachers"][0]
        if any(r["task_counts"] != first["task_counts"] or r["focus_length_counts"] != first["focus_length_counts"] for r in report["teachers"]):
            raise AssertionError("Teacher budgets differed.")
        teacher_rank = rank_results(report["teachers"], "strategy")
        teacher = teacher_rank[0]["name"]
        report["teacher_ranking"] = teacher_rank
        _safe_write_json(root / "teacher-selection.json", {"ranking": teacher_rank, "chosen_for_pathway_test": teacher})
        emit("teacher_selected", display=f"\nTEACHER SELECTION SEALED: {teacher}; retention preserved across seeds: {teacher_rank[0]['all_retention_preserved']}")
        core = load()
        report["baseline_pathways"] = measure(core, "pathway_selection")
        del core
        for i, seed in enumerate(args.seeds):
            for variant in VARIANTS[i:] + VARIANTS[:i]:
                if variant == "standard":
                    trained = next(r for r in report["teachers"] if r["strategy"] == teacher and r["seed"] == seed)
                    core = load(root / trained["checkpoint"])
                    scores = measure(core, "pathway_selection")
                    record = {**trained, "scores": scores, "retention_losses": retention_losses(report["baseline_pathways"], scores), "reused_teacher_candidate": True}
                    del core
                else:
                    record = train(teacher, variant, seed, report["baseline_pathways"], "pathway_selection")
                report["pathways"].append(record)
                save()
        pathway_rank = rank_results(report["pathways"], "variant")
        variant = pathway_rank[0]["name"]
        finalists = sorted({("mixed", "standard"), (teacher_rank[0]["name"], "standard"),
                            (teacher_rank[1]["name"], "standard"), (teacher, variant)})
        report["pathway_ranking"] = pathway_rank
        _safe_write_json(root / "pathway-selection.json", {"ranking": pathway_rank, "finalists": finalists,
                                                           "note": "Sealed before any confirmation answer is generated."})
        emit("pathway_selected", display=f"PATHWAY SELECTION SEALED: {variant}; now opening untouched final tests.")
        core = load()
        report["baseline_confirmation"] = measure(core, "confirmation")
        del core
        for strategy, mode in finalists:
            for seed in args.seeds:
                candidates = report["teachers"] if mode == "standard" else report["pathways"]
                trained = next(r for r in candidates if r["strategy"] == strategy and r["variant"] == mode and r["seed"] == seed)
                core = load(root / trained["checkpoint"])
                scores = measure(core, "confirmation")
                report["confirmation"].append({"strategy": strategy, "variant": mode, "seed": seed,
                                                "scores": scores, "retention_losses": retention_losses(report["baseline_confirmation"], scores)})
                emit("confirmation", display=f"FINAL {strategy}/{mode}/{seed}: primary {primary_score(scores):.1%}, retention losses {len(report['confirmation'][-1]['retention_losses'])}")
                del core
                save()
        report["state"] = "complete"
        emit("complete", display="COMPLETE. No curriculum advanced; no candidate deployed; live teaching remains paused.")
    except (TrialStopped, KeyboardInterrupt) as error:
        report["state"], report["reason"] = "incomplete", str(error) or "Keyboard interrupt"
        emit("stopped", display=report["reason"])
    except Exception as error:
        report["state"], report["error"] = "failed", repr(error)
        raise
    finally:
        report["frozen_input_unchanged"] = hashlib.sha256(frozen.read_bytes()).hexdigest() == digest
        report["live_pause_exists"] = (live / "pause").exists()
        save()
    return 0 if report["state"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
