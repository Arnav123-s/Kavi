"""Command-line interface for Kavi's finite model curriculum automation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .terminal import configure_utf8_output

from .school import ModelSchool, SchoolConfig


def _path_or_none(value: str | None) -> Path | None:
    return Path(value).expanduser().resolve() if value else None


def build_parser() -> argparse.ArgumentParser:
    """Create a small CLI with explicit limits and visible source gates."""

    parser = argparse.ArgumentParser(
        prog="python -m kavi.school_cli",
        description=(
            "Run Kavi's finite, evaluator-gated model curriculum. "
            "It never downloads or ingests source texts automatically."
        ),
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=Path("curriculum/model-curriculum.json"),
        help="declared curriculum plan",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        default=Path("curriculum/source-manifest.json"),
        help="reviewed public source metadata",
    )
    parser.add_argument(
        "--lesson-root",
        type=Path,
        default=Path("private/lessons"),
        help="local-only reviewed lesson files; never fetched automatically",
    )
    parser.add_argument("--list", action="store_true", help="show stages without running")
    parser.add_argument("--max-stages", type=int, default=2)
    parser.add_argument("--lessons-per-stage", type=int, default=24)
    parser.add_argument("--symbol-batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--interval-ms", type=int, default=80)
    parser.add_argument("--pause-file")
    parser.add_argument("--stop-file")
    parser.add_argument(
        "--state-file",
        help="optional local checkpoint; Kavi never creates one unless you provide this path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """List or execute a bounded curriculum pass."""

    configure_utf8_output()

    parser = build_parser()
    args = parser.parse_args(argv)
    school = ModelSchool(
        SchoolConfig(
            plan_path=args.plan,
            source_manifest_path=args.source_manifest,
            private_lesson_root=args.lesson_root,
            max_stages=args.max_stages,
            lessons_per_stage=args.lessons_per_stage,
            symbol_batch_size=args.symbol_batch_size,
            seed=args.seed,
            interval_ms=args.interval_ms,
            pause_file=_path_or_none(args.pause_file),
            stop_file=_path_or_none(args.stop_file),
            state_file=_path_or_none(args.state_file),
        )
    )
    if args.list:
        print(f"Kavi model curriculum: {school.plan.title}")
        for stage in school.list_stages():
            prerequisites = ", ".join(stage.prerequisites) or "none"
            sources = ", ".join(stage.source_ids) or "generated only"
            print(
                f"  {stage.stage_id}: {stage.status}; "
                f"prerequisites={prerequisites}; sources={sources}"
            )
        return 0
    summary = school.run()
    print("\nsummary:")
    print(f"  completed stages: {', '.join(summary.completed_stage_ids) or 'none'}")
    print(f"  stopped={summary.stopped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
