"""Visible command-line entry point for Kavi's bounded adaptive syllabus."""

from __future__ import annotations

import argparse
from pathlib import Path

from .adaptive_syllabus import AdaptiveRuntimeConfig, AdaptiveSyllabus, AdaptiveSyllabusRuntime
from .terminal import configure_utf8_output


def _path_or_none(value: str | None) -> Path | None:
    return Path(value).expanduser().resolve() if value else None


def build_parser() -> argparse.ArgumentParser:
    """Create the local-only visible adaptive-study CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m kavi.adaptive_cli",
        description=(
            "Run a finite Kavi adaptive syllabus from reviewed local lessons. "
            "It never downloads books or starts a background worker."
        ),
    )
    parser.add_argument(
        "--syllabus",
        type=Path,
        default=Path("private/syllabi/adaptive-textbook-syllabus.json"),
        help="private reviewed syllabus with lesson identifiers only",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=Path("curriculum/source-manifest.json"),
        help="public reviewed-source metadata",
    )
    parser.add_argument(
        "--lesson-root",
        type=Path,
        default=Path("private/lessons"),
        help="private reviewed lesson manifests; never fetched automatically",
    )
    parser.add_argument("--state-file", help="optional local compact-state checkpoint")
    parser.add_argument("--max-units", type=int, default=1)
    parser.add_argument("--seed", type=int, help="reproducible randomized question order")
    parser.add_argument("--interval-ms", type=int, default=250)
    parser.add_argument("--pause-file")
    parser.add_argument("--stop-file")
    parser.add_argument(
        "--wait-for-enter",
        action="store_true",
        help="open the visible CLI and wait for Enter before the finite pass begins",
    )
    parser.add_argument("--list", action="store_true", help="show declared units without teaching")
    return parser


def main(argv: list[str] | None = None) -> int:
    """List or visibly run a finite local adaptive syllabus pass."""

    configure_utf8_output()
    args = build_parser().parse_args(argv)
    if args.list:
        syllabus = AdaptiveSyllabus.load(args.syllabus)
        print(f"Kavi adaptive textbook syllabus: {syllabus.title}")
        print(
            "  gate: "
            f"protected>={syllabus.minimum_protected_accuracy:.2f}; "
            f"held-out>={syllabus.minimum_held_out_accuracy:.2f}"
        )
        for unit in syllabus.units:
            repairs = ", ".join(unit.repair_lesson_ids) or "none declared"
            prerequisites = ", ".join(unit.prerequisites) or "none"
            print(
                f"  {unit.unit_id}: lesson={unit.lesson_id}; "
                f"repairs={repairs}; prerequisites={prerequisites}"
            )
        return 0
    if args.wait_for_enter:
        print("Kavi is ready. Press Enter in this terminal to begin the finite visible pass.")
        try:
            input()
        except EOFError:
            print("No interactive terminal input is available; starting immediately.")
    runtime = AdaptiveSyllabusRuntime(
        AdaptiveRuntimeConfig(
            syllabus_path=args.syllabus,
            source_manifest_path=args.source_manifest,
            lesson_root=args.lesson_root,
            state_file=_path_or_none(args.state_file),
            max_units=args.max_units,
            seed=args.seed,
            interval_ms=args.interval_ms,
            pause_file=_path_or_none(args.pause_file),
            stop_file=_path_or_none(args.stop_file),
        )
    )
    summary = runtime.run()
    print("\nsummary:")
    print(f"  mastered units: {', '.join(summary.completed_unit_ids) or 'none'}")
    print(f"  stopped={summary.stopped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
