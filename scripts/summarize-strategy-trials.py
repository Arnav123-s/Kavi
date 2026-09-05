"""Print aggregate trial evidence without publishing private question text."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from statistics import mean


def primary(scores):
    groups = [v for k, v in scores.items() if k.startswith("primary_")]
    return sum(g["correct"] for g in groups) / sum(g["total"] for g in groups)


def position_errors(scores):
    result = {}
    for name in ("primary_3", "primary_4", "longer_transfer", "script_transfer"):
        group = scores.get(name)
        if not group:
            continue
        counts, paired = defaultdict(Counter), defaultdict(dict)
        for row in group["outputs"]:
            operation, sequence = row["question"].split(" ", 1)
            if operation not in ("First", "Last"):
                continue
            actual = row["actual"].strip()
            paired[sequence][operation] = actual
            counts[operation]["total"] += 1
            if row["correct"]:
                counts[operation]["correct"] += 1
            elif not actual:
                counts[operation]["empty"] += 1
            elif len(actual) == 1 and actual in sequence:
                # Generated assessment strings have distinct code points.
                counts[operation][f"wrong_input_position_{sequence.index(actual)+1}"] += 1
            else:
                counts[operation]["other_wrong_output"] += 1
        both = [p for p in paired.values() if set(p) == {"First", "Last"}]
        result[name] = {"operations": dict(counts), "paired_strings": len(both),
                        "identical_first_last_outputs": sum(p["First"] == p["Last"] for p in both)}
    return result


def aggregate(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["strategy"], record["variant"])].append(record)
    result = []
    for (strategy, variant), rows in sorted(grouped.items()):
        summary = {"strategy": strategy, "variant": variant, "repetitions": len(rows),
                   "primary_percent": round(mean(primary(r["scores"]) for r in rows) * 100, 2),
                   "primary_seed_percent": [round(primary(r["scores"]) * 100, 2) for r in rows],
                   "retention_losses_per_seed": [len(r["retention_losses"]) for r in rows],
                   "groups_percent": {g: round(mean(r["scores"][g]["accuracy"] for r in rows) * 100, 2)
                                      for g in rows[0]["scores"]}}
        tasks = defaultdict(lambda: [0, 0])
        for r in rows:
            for g, values in r["scores"].items():
                if g.startswith("primary_"):
                    for task, count in values["per_task"].items():
                        tasks[task][0] += count["correct"]
                        tasks[task][1] += count["total"]
        summary["primary_operation_percent"] = {k: round(c / n * 100, 2) for k, (c, n) in tasks.items()}
        if "training_seconds" in rows[0]:
            summary.update({
                "mean_training_seconds": round(mean(r["training_seconds"] for r in rows), 3),
                "mean_practice_probe_seconds": round(mean(r["practice_probe_seconds"] for r in rows), 3),
                "practice_probe_calls": [r["practice_probe_calls"] for r in rows],
                "unique_training_questions": [r["unique_training_questions"] for r in rows],
                "parameter_counts": [r["ledger"]["parameters"] for r in rows],
                "parallel_row_counts": [r["parallel_row_counts"] for r in rows]})
        result.append(summary)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    output = {"state": report["state"], "teachers": aggregate(report["teachers"]),
              "pathways": aggregate(report["pathways"]), "confirmation": aggregate(report["confirmation"]),
              "wall_seconds": report["wall_seconds"], "process_cpu_seconds": report["process_cpu_seconds"],
              "memory": report["memory"], "artifact_bytes": report["artifact_bytes_before_report_write"]}
    for name in ("baseline_teacher", "baseline_pathways", "baseline_confirmation"):
        if name in report:
            scores = report[name]
            output[name] = {"primary_percent": round(primary(scores)*100, 2),
                            "groups": {g: {k: s[k] for k in ("correct", "total", "accuracy")}
                                       for g, s in scores.items()}, "position_errors": position_errors(scores)}
    output["confirmation_position_errors"] = [
        {"strategy": r["strategy"], "variant": r["variant"], "seed": r["seed"],
         "errors": position_errors(r["scores"])} for r in report["confirmation"]]
    print(json.dumps(output, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
