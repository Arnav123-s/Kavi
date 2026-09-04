"""CLI for Kavi's unified circuit model and separate live feeds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pathway_circuit import CircuitState, PathwayCircuitCore
from .pathway_live import CHANNELS, PathwayCurriculumRuntime, PathwayLiveConfig, watch_channel
from .terminal import configure_utf8_output


def _optional_path(value: str | None) -> Path | None:
    return Path(value).expanduser().resolve() if value else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m kavi.pathway_cli",
        description=(
            "Run Kavi's finite unified path-centric curriculum or follow one "
            "read-only live event channel."
        ),
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    run = subcommands.add_parser("run", help="teach all currently implemented stages")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument(
        "--lesson",
        type=Path,
        default=Path("private/lessons/basic-algebra-6e-expressions-relations-1-1.json"),
    )
    run.add_argument(
        "--source-manifest",
        type=Path,
        default=Path("curriculum/source-manifest.json"),
    )
    run.add_argument("--max-parallel-paths", type=int, default=4)
    run.add_argument("--interval-ms", type=int, default=250)
    run.add_argument("--start-delay-seconds", type=int, default=6)
    run.add_argument("--seed", type=int, default=31)
    run.add_argument("--pause-file")
    run.add_argument("--stop-file")

    watch = subcommands.add_parser("watch", help="follow one live feed until the run ends")
    watch.add_argument("--run-dir", type=Path, required=True)
    watch.add_argument("--channel", choices=CHANNELS, required=True)
    watch.add_argument("--poll-ms", type=int, default=100)

    inspect = subcommands.add_parser(
        "inspect-state",
        help="inspect compact active model state without loading an archived parent",
    )
    inspect.add_argument("--state-file", type=Path, required=True)

    signal = subcommands.add_parser("signal", help="pause, resume, stop, or inspect one live run")
    signal.add_argument("--run-dir", type=Path, required=True)
    signal.add_argument("action", choices=("pause", "resume", "stop", "status"))
    return parser


def _inspect_state(path: Path) -> None:
    raw = json.loads(path.read_text(encoding="utf-8"))
    state = CircuitState.from_mapping(raw)
    core = PathwayCircuitCore(state)
    ledger = core.resource_ledger()
    print("Kavi active path-centric state")
    print(
        f"  routes={ledger['routes']}; jump adapters={ledger['jump_adapters']}; "
        f"numeric payload≈{ledger['estimated_numeric_payload_bytes']} bytes"
    )
    print("  categorical routes:")
    for route in state.routes:
        print(
            f"    {route.route_id}: task={route.task_id}; output={route.output_label}; "
            f"support={route.support}; revision={route.revision}; "
            f"resistance={route.resistance:.3f}"
        )
    print("  transform routes:")
    for route in state.transforms:
        print(
            f"    {route.route_id}: operation={route.operation}; support={route.support}; "
            f"revision={route.revision}; resistance={route.resistance:.3f}"
        )
    print("  verified foundations: " + ", ".join(state.verified_foundations))
    print("  archived parents are not loaded or consulted by this command.")


def _signal(run_dir: Path, action: str) -> None:
    root = run_dir.expanduser().resolve()
    pause_path = root / "pause"
    stop_path = root / "stop"
    if action == "pause":
        pause_path.touch(exist_ok=True)
        print(f"pause requested: {pause_path}")
    elif action == "resume":
        if pause_path.exists():
            pause_path.unlink()
        print(f"resume requested: {pause_path} is absent")
    elif action == "stop":
        stop_path.touch(exist_ok=True)
        print(f"safe stop requested: {stop_path}")
    else:
        status_path = root / "status.json"
        print(
            status_path.read_text(encoding="utf-8")
            if status_path.exists()
            else "run has not started"
        )


def main(argv: list[str] | None = None) -> int:
    configure_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "watch":
        return watch_channel(args.run_dir, args.channel, poll_ms=args.poll_ms)
    if args.command == "inspect-state":
        _inspect_state(args.state_file)
        return 0
    if args.command == "signal":
        _signal(args.run_dir, args.action)
        return 0

    config = PathwayLiveConfig(
        run_dir=args.run_dir,
        lesson_path=args.lesson,
        source_manifest_path=args.source_manifest,
        max_parallel_paths=args.max_parallel_paths,
        interval_ms=args.interval_ms,
        start_delay_seconds=args.start_delay_seconds,
        seed=args.seed,
        pause_file=_optional_path(args.pause_file),
        stop_file=_optional_path(args.stop_file),
    )
    runtime = PathwayCurriculumRuntime(config)
    summary = runtime.run()
    print("\nsummary:")
    print("  completed: " + ", ".join(summary.completed_stage_ids))
    print(f"  active routes={summary.routes}; jump adapters={summary.jump_adapters}")
    print(f"  stopped={summary.stopped}")
    print(f"  next gate: {summary.next_gate}")
    return 1 if summary.stopped else 0


if __name__ == "__main__":
    raise SystemExit(main())
