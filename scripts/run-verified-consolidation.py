"""Search smaller learned changes with an exact finite preservation gate."""

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch

from kavi.consolidation_trials import interpolate_candidate, lost_correct_answers, primary_correct
from kavi.pathway_live import _safe_write_json
from kavi.pathway_trials import TrialLearner
from kavi.repair_trials import RepairLearner
from kavi.strategy_trials import make_plan, serialize
from kavi.teaching_comparison import evaluate
from kavi.trial_resources import memory_reading


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--teacher-ledger", type=Path, required=True)
    parser.add_argument("--live-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    source, root, live = args.source.resolve(), args.output.resolve(), args.live_run.resolve()
    if root.exists() or root == repo / "runs" or not root.is_relative_to(repo / "runs"):
        parser.error("Use a new ignored output directory under runs.")
    if not live.is_relative_to(repo / "runs") or not (live / "pause").exists():
        parser.error("Live teaching must stay paused.")
    prior = json.loads((source / "report.json").read_text(encoding="utf-8"))
    prior_manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    if prior["state"] != "complete":
        parser.error("Finish the proposal experiment first.")
    progress = json.loads(args.teacher_ledger.read_text(encoding="utf-8"))
    plan = make_plan(progress, prior_manifest["plan"]["forbidden_sequences"], seed=981503)
    proposals = sorted(prior["candidates"], key=lambda r: (r["variant"], r["seed"]))
    scales = [2.0 ** -i for i in range(7)]
    digest = hashlib.sha256((source / "input.pt").read_bytes()).hexdigest()
    if digest != prior_manifest["source_sha256"]:
        raise ValueError("Frozen input hash mismatch.")
    root.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(source / "input.pt", root / "input.pt")
    paths = ("kavi/consolidation_trials.py", "kavi/repair_trials.py", "kavi/wave_core.py",
             "kavi/pathway_trials.py", "kavi/strategy_trials.py", "kavi/teaching_comparison.py",
             "kavi/mixed_quizzes.py", "kavi/language_curriculum.py", "kavi/trial_resources.py",
             "scripts/run-verified-consolidation.py")
    _safe_write_json(root / "manifest.json", {
        "schema": 1, "source_sha256": digest,
        "teacher_ledger_sha256": hashlib.sha256(args.teacher_ledger.read_bytes()).hexdigest(),
        "plan": serialize(plan), "scales": scales,
        "proposals": [{k: r[k] for k in ("variant", "seed", "checkpoint", "fingerprint")} for r in proposals],
        "selection": "Zero lost baseline-correct answers across ALL guard groups, plus at least one additional primary answer. Rank primary gain, fewer parameters, then smaller fraction and stable candidate name.",
        "confirmation": "Open only after selecting one candidate; report all-group break counts without further tuning.",
        "unused_partition": "pathway_selection",
        "optimizer": "Reset for inference-test candidates; no optimizer steps in this search and no live resume.",
        "resource_policy": {"threads": 1, "max_seconds": 600, "question_pacing_ms": 2,
                            "min_available_gib": 2, "min_disk_gib": 2, "max_working_set_gib": 1},
        "code_sha256": {p: hashlib.sha256((repo / p).read_bytes()).hexdigest() for p in paths}})
    started, cpu_started, sampled_at = time.monotonic(), time.process_time(), 0.0
    report = {"state": "running", "candidates": [], "chosen": None}

    def save():
        report.update(wall_seconds=time.monotonic()-started, process_cpu_seconds=time.process_time()-cpu_started,
                      memory=memory_reading(), artifact_bytes=sum(p.stat().st_size for p in root.rglob("*") if p.is_file()))
        _safe_write_json(root / "report.json", report)

    def check():
        nonlocal sampled_at
        time.sleep(0.002)
        if (root / "stop.request").exists() or not (live / "pause").exists():
            raise InterruptedError("Experiment stop requested or live pause removed.")
        if time.monotonic()-started >= 600:
            raise InterruptedError("Bounded configuration-search time exhausted.")
        if time.monotonic()-sampled_at >= 2:
            reading, sampled_at = memory_reading(), time.monotonic()
            if ((reading["available_bytes"] is not None and reading["available_bytes"] < 2 * 1024**3)
                    or (reading["working_set_bytes"] is not None and reading["working_set_bytes"] > 1024**3)
                    or shutil.disk_usage(root).free < 2 * 1024**3):
                raise InterruptedError("Configuration-search resource ceiling reached.")

    def load(path, mode="ordinary"):
        core = TrialLearner.load(path) if mode == "ordinary" else RepairLearner.load(path)
        core.config = replace(core.config, threads=1)
        core.network.config = core.config
        torch.set_num_threads(1)
        return core

    try:
        parent = load(root / "input.pt")
        baseline = evaluate(parent, plan["partitions"]["teacher_selection"], check=check)
        report["baseline_guard"] = baseline
        correct_keys = {q["key"] for group in baseline.values() for q in group["outputs"] if q["correct"]}
        groups = ("primary_4", "primary_3", "script_transfer", "longer_transfer", "retention_pairs", "retention_characters")
        protected = [q for name in groups for q in plan["partitions"]["teacher_selection"].get(name, []) if q.key in correct_keys]
        report["protected_answer_count"] = len(protected)
        print(f"KAVI VERIFIED CONFIGURATION SEARCH: {len(proposals)*len(scales)} proposals; {len(protected)} protected answers across all groups.", flush=True)
        best_key = None
        for proposal_record in proposals:
            mode, seed = proposal_record["variant"], proposal_record["seed"]
            proposal = load(source / proposal_record["checkpoint"], mode)
            if proposal.fingerprint() != proposal_record["fingerprint"]:
                raise ValueError("Proposal fingerprint changed.")
            for fraction in scales:
                check()
                core = interpolate_candidate(parent, proposal, fraction)
                cache, broken = {}, None
                for q in protected:
                    check()
                    actual = core.generate(q.prefix, max_bytes=24)
                    cache[q.prefix] = actual
                    if not q.correct(actual):
                        broken = q.key
                        break
                record = {"variant": mode, "seed": seed, "fraction": fraction,
                          "protected_checked": len(cache), "first_broken_key": broken,
                          "eligible": False, "parameters": core.ledger()["parameters"]}
                if broken is None:
                    # Evaluation-only cache of this fixed candidate's OWN outputs.
                    # Expected answers are never passed through the model interface.
                    class CachedProbe:
                        updates = core.updates
                        def fingerprint(self): return core.fingerprint()
                        def generate(self, prompt, max_bytes):
                            if prompt not in cache:
                                cache[prompt] = core.generate(prompt, max_bytes=max_bytes)
                            return cache[prompt]
                    scores = evaluate(CachedProbe(), plan["partitions"]["teacher_selection"], check=check)
                    losses = lost_correct_answers(baseline, scores)
                    gain = primary_correct(scores)-primary_correct(baseline)
                    record.update(scores=scores, primary_gain=gain, all_group_losses=losses,
                                  eligible=not losses and gain >= 1)
                    if record["eligible"]:
                        key = (-gain, record["parameters"], fraction, mode, seed)
                        if best_key is None or key < best_key:
                            best_key = key
                            core.save(root / "selected.pt")
                            report["chosen"] = {k: record[k] for k in ("variant", "seed", "fraction", "parameters", "primary_gain")}
                            report["chosen"]["fingerprint"] = core.fingerprint()
                        print(f"ELIGIBLE {mode}/{seed} fraction {fraction:g}: +{gain} primary, zero protected answers lost", flush=True)
                report["candidates"].append(record)
                del core
                save()
            del proposal
            print(f"Completed direction {mode}/{seed}; {len(report['candidates'])} configurations checked", flush=True)
        _safe_write_json(root / "selection.json", {"chosen": report["chosen"], "configurations": len(report["candidates"])})
        if report["chosen"]:
            report["baseline_confirmation"] = evaluate(parent, plan["partitions"]["confirmation"], check=check)
            core = load(root / "selected.pt", report["chosen"]["variant"])
            if core.fingerprint() != report["chosen"]["fingerprint"]:
                raise AssertionError("Selected candidate failed checkpoint round trip.")
            final = evaluate(core, plan["partitions"]["confirmation"], check=check)
            report["confirmation"] = {"scores": final,
                                      "primary_gain": primary_correct(final)-primary_correct(report["baseline_confirmation"]),
                                      "all_group_losses": lost_correct_answers(report["baseline_confirmation"], final)}
            print(f"FINAL: primary gain {report['confirmation']['primary_gain']}, newly broken previously correct answers across ALL groups {len(report['confirmation']['all_group_losses'])}", flush=True)
            del core
        else:
            print("No candidate passed both guard conditions. No unchanged candidate relabeled as an improvement.", flush=True)
        report["state"] = "complete"
        print("COMPLETE. No live model replaced; bounded test preservation is not a universal proof.", flush=True)
    except (KeyboardInterrupt, InterruptedError) as error:
        report["state"], report["reason"] = "incomplete", str(error) or "Interrupted"
    except Exception as error:
        report["state"], report["error"] = "failed", repr(error)
        raise
    finally:
        report["live_pause_exists"] = (live / "pause").exists()
        report["input_unchanged"] = hashlib.sha256((root / "input.pt").read_bytes()).hexdigest() == digest
        save()
    return 0 if report["state"] == "complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
