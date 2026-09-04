"""Compare teaching on disposable checkpoint copies; leave live training alone."""

import argparse
from collections import Counter
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from kavi.pathway_live import _safe_write_json
from kavi.teaching_comparison import (ComparisonConfig, LessonSchedule, build_plan,
                                     checkpoint, evaluate, retention_losses, serialize_plan)
from kavi.mixed_quizzes import task_name
from kavi.wave_core import WaveLearner


class ExperimentStopped(Exception):
    pass


def peak_process_bytes():
    """Whole-process Windows peak working set, including native tensor memory."""
    if sys.platform != "win32":
        return None
    import ctypes
    from ctypes import wintypes

    class Counters(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in ("PeakWorkingSetSize", "WorkingSetSize",
             "QuotaPeakPagedPoolUsage", "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
             "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]

    kernel, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD]
    counters = Counters()
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), ctypes.sizeof(counters)):
        return None
    return counters.PeakWorkingSetSize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=384)
    parser.add_argument("--seeds", type=int, nargs="+", default=[43011, 43012, 43013])
    parser.add_argument("--max-seconds", type=int, default=600)
    args = parser.parse_args()
    config = ComparisonConfig(steps=args.steps, seeds=tuple(args.seeds), max_seconds=args.max_seconds)
    repo, root = Path(__file__).resolve().parents[1], args.output.resolve()
    if not root.is_relative_to(repo / "runs") or root == repo / "runs":
        parser.error("Use a new experiment directory below the ignored runs directory.")
    if root.exists():
        parser.error("Do not overwrite or resume an existing comparison.")
    model_path, pointer, progress = checkpoint(args.source_run)
    plan = build_plan(progress)
    root.mkdir(parents=True, exist_ok=False)
    frozen = root / "input.pt"
    shutil.copyfile(model_path, frozen)
    if hashlib.sha256(frozen.read_bytes()).hexdigest() != pointer["sha256"]:
        raise ValueError("Frozen experimental input does not match the source checkpoint.")
    _safe_write_json(root / "input-teacher.json", progress)
    started, cpu_started = time.monotonic(), time.process_time()
    deadline = started + config.max_seconds
    manifest = {"schema": 1, "config": asdict(config), "checkpoint": pointer,
                "source_run": str(args.source_run.resolve()), "live_mutations": False,
                "arm_order": [[seed, arm] for i, seed in enumerate(config.seeds)
                              for arm in (("random_mixed", "contrast") if i % 2 == 0 else ("contrast", "random_mixed"))],
                "primary": "Final position_three exact first/last accuracy, separately and combined.",
                "secondary": "Length/script transfer, copying/joining, and loss of baseline-correct retention items.",
                "limits": "One initial checkpoint; teaching-seed repetitions are not independent pretrained models. A narrow pilot, not a broad capability claim.",
                "control": "Random independent Latin three-symbol examples in the current quiz style; identical task frequencies and rehearsal, not the whole live teacher replayed. Both arms use Latin for operation teaching; multilingual command transfer is held out.",
                "promotion": "No live promotion. Report improved mean primary score only together with retention and all seed results.",
                "plan": serialize_plan(plan)}
    _safe_write_json(root / "manifest.json", manifest)
    report = {"schema": 1, "state": "running", "arms": [], "manifest": "manifest.json"}

    def emit(kind, **values):
        row = {"time_seconds": time.monotonic() - started, "kind": kind, **values}
        with (root / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=True) + "\n")
        if "display" in values:
            print(values["display"], flush=True)

    def save_report():
        report["wall_seconds"] = time.monotonic() - started
        report["process_cpu_seconds"] = time.process_time() - cpu_started
        report["peak_process_working_set_bytes"] = peak_process_bytes()
        report["persistent_files_bytes_before_report_write"] = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
        _safe_write_json(root / "report.json", report)

    def check():
        if (root / "stop.request").exists():
            raise ExperimentStopped("Owner stop request; live learner was not touched.")
        if time.monotonic() >= deadline:
            raise ExperimentStopped("Experiment wall-clock limit reached; partial arms are not compared.")
        if shutil.disk_usage(root).free < 2 * 1024 ** 3:
            raise ExperimentStopped("Free disk below 2 GiB.")

    def load_copy():
        import torch
        core = WaveLearner.load(frozen)
        core.config = replace(core.config, threads=1)
        core.network.config = core.config
        torch.set_num_threads(1)
        return core

    emit("start", display=f"KAVI TEACHING COMPARISON | isolated copies | {config.steps} updates per arm\n"
         f"Same checkpoint, matched task budgets, fresh sealed tests. Output: {root}\n"
         "No live restart or replacement. Ctrl+C stops only this experiment.")
    try:
        core = load_copy()
        initial_fingerprint, initial_updates = core.fingerprint(), core.updates
        report["initial"] = {"fingerprint": initial_fingerprint, "updates": initial_updates,
                             "ledger": core.ledger()}
        report["baseline"] = evaluate(core, plan["final"], check=check)
        base_dev = evaluate(core, plan["development"], check=check)
        report["baseline_development"] = base_dev
        emit("baseline", display="BASELINE | " + " | ".join(
            f"{name}: {value['correct']}/{value['total']}" for name, value in report["baseline"].items()))
        save_report()
        del core
        for seed, arm in manifest["arm_order"]:
            check()
            core = load_copy()
            if core.fingerprint() != initial_fingerprint or core.updates != initial_updates:
                raise AssertionError("Arms did not start from the same learned state.")
            schedule, counts, unique = LessonSchedule(arm, seed, plan), Counter(), set()
            history, steps, training_seconds, input_bytes, answer_bytes = [], 0, 0.0, 0, 0
            first_target_pass = None
            schedule.observe_development(base_dev)
            emit("arm_start", arm=arm, seed=seed, display=f"\n{arm.upper()} | teaching seed {seed} | from update {initial_updates}")
            for step in range(config.steps):
                check()
                batch, lesson = schedule.batch(step)
                counts.update(task_name(q) for q in batch)
                unique.update(q.key for q in batch)
                input_bytes += sum(len(q.prefix.encode()) for q in batch)
                answer_bytes += sum(len((q.answer + "\n").encode()) for q in batch)
                begun = time.monotonic()
                metrics = core.learn_answers([(q.prefix, q.answer) for q in batch])
                training_seconds += time.monotonic() - begun
                steps += 1
                emit("training", arm=arm, seed=seed, step=steps, lesson=lesson, loss=metrics["loss"],
                     examples=[{"prompt": q.prompt, "answer": q.answer, "key": q.key} for q in batch])
                time.sleep(config.rest_ms / 1000)
                if steps % config.check_every == 0:
                    scores = evaluate(core, plan["development"], check=check)
                    if all(v["accuracy"] >= 0.9 for v in scores["3"]["per_task"].values()) and first_target_pass is None:
                        first_target_pass = {"updates": steps, "presentations": steps * 4,
                                             "training_seconds": training_seconds}
                    advanced = schedule.observe_development(scores)
                    history.append({"step": steps, "scores": scores, "stage": schedule.stage})
                    emit("development", arm=arm, seed=seed, step=steps,
                         display=f"{arm} {seed} | {steps}/{config.steps} updates | " + " | ".join(
                             f"length {k}: {v['correct']}/{v['total']}" for k, v in scores.items()) +
                             (" | contrast lesson advances to three symbols" if advanced else ""))
            final = evaluate(core, plan["final"], check=check)
            lost = retention_losses(report["baseline"], final)
            ledger = core.ledger()
            if core.updates != initial_updates + config.steps or ledger["parameters"] != report["initial"]["ledger"]["parameters"]:
                raise AssertionError("Training budget or parameter count changed.")
            output = root / f"{arm}-{seed}.pt"
            core.save(output)
            record = {"arm": arm, "seed": seed, "state": "complete", "updates": steps,
                      "presentations": steps * 4, "unique_examples": len(unique), "task_counts": dict(counts),
                      "prefix_bytes": input_bytes, "supervised_answer_bytes": answer_bytes,
                      "training_seconds": training_seconds, "final": final, "development": history,
                      "first_three_symbol_development_pass": first_target_pass,
                      "lost_baseline_correct_retention_keys": lost, "stage": schedule.stage,
                      "ledger": ledger, "checkpoint": output.name, "fingerprint": core.fingerprint()}
            report["arms"].append(record)
            emit("arm_end", arm=arm, seed=seed, display=f"FINAL {arm} {seed} | " + " | ".join(
                f"{name}: {value['correct']}/{value['total']}" for name, value in final.items()) +
                f" | earlier correct items lost: {len(lost)}")
            save_report()
            del core
        for seed in config.seeds:
            pair = [a for a in report["arms"] if a["seed"] == seed]
            if pair[0]["task_counts"] != pair[1]["task_counts"]:
                raise AssertionError("Task presentation budgets were not matched.")
        report["state"] = "complete"
        report["summary"] = {arm: {"mean_primary_accuracy": sum(a["final"]["position_three"]["accuracy"] for a in report["arms"] if a["arm"] == arm) / len(config.seeds),
                                  "retention_preserved_all_seeds": all(not a["lost_baseline_correct_retention_keys"] for a in report["arms"] if a["arm"] == arm)}
                             for arm in ("random_mixed", "contrast")}
        emit("complete", display="\nCOMPLETE. All results, including failures, saved. Nothing was installed into the live model.")
    except (ExperimentStopped, KeyboardInterrupt) as error:
        report["state"], report["stop_reason"] = "incomplete", str(error) or "Keyboard interrupt"
        emit("stopped", display=report["stop_reason"])
    except Exception as error:
        report["state"], report["error"] = "failed", repr(error)
        raise
    finally:
        report["frozen_input_unchanged"] = hashlib.sha256(frozen.read_bytes()).hexdigest() == pointer["sha256"]
        save_report()
    return 0 if report["state"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
