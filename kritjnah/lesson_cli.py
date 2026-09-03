"""A CLI entry point for the explanation-learning experiment."""

from __future__ import annotations

import argparse
from pathlib import Path

from .lesson_runtime import ExplanationRuntime
from .runtime import RuntimeConfig
from .types import Operation


def _path_or_none(value: str | None) -> Path | None:
    return Path(value).expanduser().resolve() if value else None


def _operation(value: str) -> Operation:
    try:
        return Operation(value.lower())
    except ValueError as error:
        raise argparse.ArgumentTypeError("operation must be add or subtract") from error


def build_parser() -> argparse.ArgumentParser:
    """Create a deliberately small CLI with explicit finite controls."""

    parser = argparse.ArgumentParser(
        prog="python -m kritjnah.lesson_cli",
        description=(
            "Run finite explanation-guided learning. "
            "Explanations are verified structured arithmetic lessons."
        ),
    )
    parser.add_argument("--steps", type=int, default=24)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-active-routes", type=int, default=2)
    parser.add_argument("--workers", choices=(1, 2), type=int, default=1)
    parser.add_argument("--conflict-every", type=int, default=7)
    parser.add_argument("--interval-ms", type=int, default=80)
    parser.add_argument("--pause-file")
    parser.add_argument("--stop-file")
    parser.add_argument(
        "--ask",
        nargs=3,
        metavar=("LEFT", "RIGHT", "OPERATION"),
        help="after finite lessons, answer one add/subtract query",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run a finite explanation-learning session."""

    parser = build_parser()
    args = parser.parse_args(argv)
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
    runtime = ExplanationRuntime(config)
    summary = runtime.run()
    print(
        "\nsummary: "
        f"{summary.completed_steps} finite lessons; "
        f"{summary.promoted_candidates} promoted candidates; "
        f"{summary.correct_answers} initially correct answers; "
        f"{summary.abstentions} abstentions; stopped={summary.stopped}"
    )
    if args.ask:
        left, right, operation_name = args.ask
        try:
            operation = _operation(operation_name)
            inference = runtime.ask(int(left), int(right), operation)
        except (ValueError, argparse.ArgumentTypeError) as error:
            parser.error(str(error))
        answer = "abstain" if inference.answer is None else str(inference.answer)
        print(
            f"query: {left} {operation.symbol} {right} = {answer}; "
            f"confidence={inference.confidence:.2f}; "
            f"uncertainty={inference.uncertainty:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
