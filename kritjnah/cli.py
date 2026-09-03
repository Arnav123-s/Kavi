"""The low-overhead, streaming command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .runtime import LiveRuntime, RuntimeConfig
from .types import Operation


def _path_or_none(value: str | None) -> Path | None:
    return Path(value).expanduser().resolve() if value else None


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI without optional libraries or model runtimes."""

    parser = argparse.ArgumentParser(
        prog="kritjnah",
        description=(
            "Run the bounded, inspectable stage-0 hard-pathway experiment. "
            "All output is an observable route/update trace, not hidden reasoning."
        ),
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    live = subcommands.add_parser("live", help="train for a fixed number of exact examples")
    live.add_argument("--steps", type=int, default=24, help="finite events; default: 24")
    live.add_argument("--seed", type=int, default=7, help="reproducible curriculum seed")
    live.add_argument(
        "--max-active-routes",
        type=int,
        default=2,
        help="hard fan-out limit; two facets require at least two routes",
    )
    live.add_argument(
        "--workers",
        type=int,
        choices=(1, 2),
        default=1,
        help="independent evaluator workers only; inference remains serial",
    )
    live.add_argument(
        "--conflict-every",
        type=int,
        default=7,
        help="inject a phase-conflict test every N events; zero disables it",
    )
    live.add_argument(
        "--interval-ms",
        type=int,
        default=80,
        help="delay between visible events; zero runs without delay",
    )
    live.add_argument(
        "--pause-file",
        help="pause while this file exists; runtime never creates or removes it",
    )
    live.add_argument(
        "--stop-file",
        help="stop safely when this file exists; runtime never creates or removes it",
    )
    live.add_argument(
        "--ask",
        nargs=3,
        metavar=("LEFT", "RIGHT", "OPERATION"),
        help="after finite training, answer one add/subtract query",
    )

    inspect = subcommands.add_parser("paths", help="print the stage-0 path contracts")
    inspect.add_argument("--quiet", action="store_true", help="omit the explanatory heading")
    return parser


def _operation(value: str) -> Operation:
    try:
        return Operation(value.lower())
    except ValueError as error:
        choices = ", ".join(operation.value for operation in Operation)
        raise argparse.ArgumentTypeError(f"operation must be one of: {choices}") from error


def _print_paths(runtime: LiveRuntime, quiet: bool = False) -> None:
    if not quiet:
        print("Kritjnah stage-0 path contracts")
    for pipe in runtime.fabric.inspect_paths():
        scope = ",".join(
            operation.value for operation in sorted(pipe.scope, key=lambda item: item.value)
        )
        print(
            f"  {pipe.pipe_id}: {pipe.source} -> {pipe.target}; "
            f"{pipe.input_type.value} -> {pipe.output_type.value}; "
            f"scope={scope}; capacity={pipe.capacity}"
        )
    print(
        "  arithmetic-readout: typed join -> result; "
        "three learned scalar parameters; candidate-only updates"
    )


def main(argv: list[str] | None = None) -> int:
    """Run the selected bounded command."""

    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "paths":
        _print_paths(LiveRuntime(RuntimeConfig()), quiet=args.quiet)
        return 0

    config = RuntimeConfig(
        steps=args.steps,
        seed=args.seed,
        max_active_routes=args.max_active_routes,
        evaluator_workers=args.workers,
        conflict_every=args.conflict_every,
        interval_ms=args.interval_ms,
        pause_file=_path_or_none(args.pause_file),
        stop_file=_path_or_none(args.stop_file),
    )
    runtime = LiveRuntime(config)
    summary = runtime.run()
    print(
        "\nsummary: "
        f"{summary.completed_steps} finite steps; "
        f"{summary.promoted_candidates} promoted candidates; "
        f"{summary.correct_answers} initially correct answers; "
        f"{summary.abstentions} abstentions; "
        f"stopped={summary.stopped}"
    )
    if args.ask:
        left_text, right_text, operation_text = args.ask
        try:
            operation = _operation(operation_text)
            inference = runtime.ask(int(left_text), int(right_text), operation)
        except (ValueError, argparse.ArgumentTypeError) as error:
            parser.error(str(error))
        answer = "abstain" if inference.answer is None else str(inference.answer)
        print(
            f"query: {left_text} {operation.symbol} {right_text} = {answer}; "
            f"confidence={inference.confidence:.2f}; "
            f"uncertainty={inference.uncertainty:.2f}"
        )
    return 0
