"""Bounded configuration reuse experiment with a visible, stoppable worker."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kavi.circuit_runtime import write_json
from kavi.procedure_core import Limits, Procedure, ProcedureLibrary, describe
from kavi.procedure_search import ProgramExample, ProgramSearch, SearchExhausted
from kavi.trial_resources import memory_reading


def run(config_path, run_dir):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    train, test = config["teaching_inputs"], config["test_inputs"]
    if (not train or not test or set(train) & set(test)
            or any(type(x) is not int or not 0 <= x <= 32 for x in train + test)):
        raise ValueError("Use disjoint, nonempty natural-number partitions up to 32.")
    run_dir = run_dir.resolve()
    if not run_dir.is_relative_to(ROOT / "runs") or run_dir.exists():
        raise ValueError("Use a new directory beneath runs.")
    run_dir.mkdir(parents=True)
    started, cpu = time.monotonic(), time.process_time()
    source = ProcedureLibrary.load(ROOT / config["source"])
    base = source.closure("multiply")
    limits = Limits(max_calls=3000, max_gates=100000, max_iterations=32)
    result = {"scope": "Finite composition experiment; no invented primitives or universal learning claim",
              "config": config, "source_digest": source.digest, "base": base.to_dict(), "arms": {}}
    last_memory = 0.0

    def emit(message):
        print(message, flush=True)
        with (run_dir / "events.txt").open("a", encoding="utf-8") as out:
            out.write(message + "\n")

    def check():
        nonlocal last_memory
        if (run_dir / "STOP").exists():
            raise InterruptedError("Stopped by owner")
        if time.monotonic() - started > 120:
            raise InterruptedError("120-second total wall limit reached")
        while (run_dir / "PAUSE").exists():
            if (run_dir / "STOP").exists() or time.monotonic() - started > 120:
                raise InterruptedError("Stopped while paused or wall limit reached")
            time.sleep(.05)
        if time.monotonic() - last_memory > .25:
            last_memory = time.monotonic()
            if (memory_reading().get("working_set_bytes") or 0) > 512 * 1024**2:
                raise InterruptedError("512 MiB process working-set limit reached")

    def learn(library, name, exponent=None):
        emit(f"TEACH {name}: library has {len(library.procedures)} components")
        examples = [ProgramExample((x,), 2*x if exponent is None else x**exponent)
                    for x in config["teaching_inputs"]]
        search = ProgramSearch(library, max_nodes=2, max_candidates=3000,
                               max_candidate_cases=40000, max_seconds=5,
                               max_cache_entries=8000, limits=limits, check=check,
                               notify=lambda event, data: emit(event + " " + json.dumps(data)))
        expression = None
        reason = None
        try:
            expression = search.learn(1, examples)
        except SearchExhausted as error:
            reason = str(error)
            emit("SEARCH EXHAUSTED: " + reason)
        return {"name": name, "exponent": exponent, "body": expression,
                "description": describe(expression) if expression else None,
                "stats": asdict(search.stats), "reason": reason}

    def audit(library, expr, inputs, target):
        rows = []
        for args in inputs:
            check()
            try:
                measured = library.execute_expr(expr, args, limits=limits, check=check)
                rows.append({"inputs": args, "expected": target(*args),
                             "correct": measured.value == target(*args),
                             "execution": asdict(measured)})
            except ValueError as error:
                rows.append({"inputs": args, "correct": False, "error": str(error)})
        return {"passed": sum(r["correct"] for r in rows), "total": len(rows), "rows": rows}

    try:
        emit("START: fixed protocol; final test inputs are not supplied to search")
        for arm in ("fixed", "unrelated", "cumulative"):
            check()
            write_json(run_dir / "status.json", {"state": "running", "phase": arm})
            library = ProcedureLibrary.from_dict(base.to_dict())
            row = {"initial_bytes": len(library.encoded()), "lessons": []}
            result["arms"][arm] = row
            if arm == "unrelated":
                warmup = learn(library, "double")
                row["warmup"] = warmup
                if warmup["body"] is not None:
                    library.add(Procedure("double", 1, "naturals", body=warmup["body"]))
            for name, exponent in (("square", 2), ("fourth", 4), ("eighth", 8)):
                lesson = learn(library, name, exponent)
                row["lessons"].append(lesson)
                if arm == "cumulative" and lesson["body"] is not None:
                    library.add(Procedure(name, 1, "naturals", body=lesson["body"]))
            row["final_bytes"] = len(library.encoded())
            row["library"] = library.to_dict()
        # Final data is used only after all learning in every arm has finished.
        for arm, row in result["arms"].items():
            library = ProcedureLibrary.from_dict(row["library"])
            for lesson in row["lessons"]:
                if lesson["body"] is not None:
                    lesson["held_out"] = audit(library, lesson["body"],
                        [(x,) for x in config["test_inputs"]], lambda x: x**lesson["exponent"])
            if "warmup" in row and row["warmup"]["body"] is not None:
                row["warmup"]["held_out"] = audit(library, row["warmup"]["body"],
                    [(x,) for x in config["test_inputs"]], lambda x: 2*x)
            row["retention"] = {}
            for name, target in (("add", lambda a,b: a+b), ("multiply", lambda a,b: a*b)):
                row["retention"][name] = audit(library, ("call", name, ("arg",0), ("arg",1)),
                    [(a,b) for a in range(10) for b in range(10)], target)
            emit(f"EVALUATED {arm}: " + json.dumps({x["name"]: x.get("held_out", {}).get("passed", 0)
                                                   for x in row["lessons"]}))
        cumulative = ProcedureLibrary.from_dict(result["arms"]["cumulative"]["library"])
        if "fourth" in cumulative.procedures:
            square = ("call", "multiply", ("arg",0), ("arg",0))
            repeated = ("call", "multiply", square, square)
            learned = cumulative.procedures["fourth"].body
            result["restructuring_comparison"] = {
                "scope": "Engineer-supplied repeated-work baseline versus independently synthesized expression; no rewrite learner",
                "baseline": audit(cumulative, repeated, [(x,) for x in config["test_inputs"]], lambda x: x**4),
                "learned": audit(cumulative, learned, [(x,) for x in config["test_inputs"]], lambda x: x**4)}
        write_json(run_dir / "library.json", cumulative.to_dict())
        result["state"] = "completed"
    except Exception as error:
        result["state"] = "stopped" if isinstance(error, InterruptedError) else "failed"
        result["error"] = str(error)
        emit(result["state"].upper() + ": " + str(error))
    finally:
        result.update(seconds=time.monotonic()-started, cpu_seconds=time.process_time()-cpu,
                      memory=memory_reading())
        write_json(run_dir / "results.json", result)
        write_json(run_dir / "status.json", {"state": result["state"], "phase": "finished",
                   "summary": "Results saved. Compare held-out accuracy, search work and total library storage."})
        emit("FINISHED " + result["state"])
    return 0 if result["state"] == "completed" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "live"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "live":
        from scripts.pathway_growth_view import show
        show(args.run_dir, args.config, start=True)
        return 0
    return run(args.config, args.run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
