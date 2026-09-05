"""Live structural learning, graph inspection and direct circuit queries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import time

from .circuit_core import Circuit
from .circuit_runtime import CircuitRun, CircuitRunConfig
from .terminal import configure_utf8_output


TERMINAL_STATES = {"completed", "stopped", "failed", "budget_exhausted"}


def show_event(event: dict) -> None:
    prefix = f"[{event['elapsed_seconds']:7.2f}s | seed {event.get('seed') or '-'} | {event['phase']}]"
    kind = event["kind"]
    if kind == "candidate":
        print(f"{prefix} proposal {event['proposal']}: {event['gates']} gates; {event['remaining']} candidates remain")
        for line in event["pathway"]:
            print(f"    {line}")
    elif kind == "counterexample":
        print(f"{prefix} WRONG: {event['left']} + {event['right']} -> {event['actual']}; expected {event['expected']} [{event['source']}]")
    elif kind == "accepted":
        print(f"{prefix} ACCEPTED: {event['gates']} gates, {event['bytes']} model bytes; {event['verified_cases']} selection cases")
    elif kind == "evaluation_progress":
        print(f"{prefix} {event['completed']}/{event['total']} checked; {event['correct']} correct; {event['regressions']} regressions")
    elif kind == "evaluation_complete":
        print(f"{prefix} RESULT: {event['correct']}/{event['cases']} correct; {event['gains']} gains; {event['regressions']} regressions")
    else:
        fields = {key: value for key, value in event.items()
                  if key not in {"sequence", "elapsed_seconds", "seed", "phase", "kind"}}
        print(f"{prefix} {kind}: {json.dumps(fields, ensure_ascii=False, separators=(',', ':'))}")
    sys.stdout.flush()


def control(run_dir: Path, action: str) -> None:
    status = json.loads((run_dir / "status.json").read_text(encoding="utf-8"))
    if status["state"] in TERMINAL_STATES:
        print(f"Run is already {status['state']}.")
        return
    if action == "resume":
        (run_dir / "PAUSE").unlink(missing_ok=True)
    else:
        (run_dir / ("PAUSE" if action == "pause" else "STOP")).touch()
    print(f"{action} requested")


def ask(model_path: Path, left: int, right: int, trace: bool = False) -> None:
    circuit = Circuit.load(model_path)
    result = circuit.execute(left, right, trace=trace)
    print(f"{left} + {right} = {result.value}")
    print(f"{len(circuit.gates)} gates; {result.frames} frames; {result.gate_evaluations} gate evaluations; {len(circuit.encoded())} model bytes")
    if trace:
        print("frame  left right state | gate values | emit next")
        for row in result.trace:
            print(f"{row['frame']:5}  {row['left']:4} {row['right']:5} {row['state_in']:5} | "
                  f"{' '.join(map(str, row['gates']))} | {row['emit']}    {row['state_out']}")
        if result.trace_truncated:
            print("Trace display is limited to the first 64 frames; the complete computation was executed.")


def console(run_dir: Path) -> None:
    print("\nKavi circuit console. Enter A + B, /trace A B, /circuit, /status, /pause, /resume, /stop or /quit.")
    print("Automatic teaching has a finite budget. Queries execute the saved graph without teaching records.")
    while True:
        try:
            command = input("kavi> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        try:
            if command in {"/quit", "/exit"}:
                return
            if command == "/status":
                print((run_dir / "status.json").read_text(encoding="utf-8"))
            elif command == "/circuit":
                print("\n".join(Circuit.load(run_dir / "model.json").describe()))
            elif command in {"/pause", "/resume", "/stop"}:
                control(run_dir, command[1:])
            elif command.startswith("/trace "):
                values = command.split()
                if len(values) != 3:
                    raise ValueError("Use /trace LEFT RIGHT.")
                ask(run_dir / "model.json", int(values[1]), int(values[2]), True)
            elif match := re.fullmatch(r"\s*(\d+)\s*\+\s*(\d+)\s*", command):
                ask(run_dir / "model.json", int(match.group(1)), int(match.group(2)))
            elif command:
                print("Use A + B, /trace A B, /circuit, /status, /pause, /resume, /stop or /quit.")
        except (OSError, ValueError) as error:
            print(f"Cannot complete command: {error}")


def watch(run_dir: Path, follow: bool) -> None:
    with (run_dir / "events.jsonl").open(encoding="utf-8") as stream:
        while True:
            position = stream.tell()
            line = stream.readline()
            if line and line.endswith("\n"):
                show_event(json.loads(line))
                continue
            stream.seek(position)
            if not follow:
                return
            try:
                status = json.loads((run_dir / "status.json").read_text(encoding="utf-8"))
                if status["state"] in TERMINAL_STATES:
                    # The writer may publish status just before the final event.
                    time.sleep(0.05)
                    for remaining in stream:
                        if remaining.endswith("\n"):
                            show_event(json.loads(remaining))
                    return
            except FileNotFoundError:
                pass
            time.sleep(0.2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kavi-circuit", description="Learn and repair reusable discrete circuits with live, bounded experiments.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run the declared curriculum, repair and final evaluation")
    run.add_argument("--run-dir", type=Path, required=True, help="new directory; existing runs are never overwritten")
    run.add_argument("--config", type=Path, help="reviewed JSON configuration; defaults are finite")
    run.add_argument("--interactive", action="store_true", help="open the query console after the finite run")
    for name in ("watch", "status", "console", "control"):
        command = sub.add_parser(name)
        command.add_argument("--run-dir", type=Path, required=True)
        if name == "watch":
            command.add_argument("--follow", action="store_true")
        elif name == "control":
            command.add_argument("action", choices=("pause", "resume", "stop"))
    query = sub.add_parser("ask", help="execute a saved circuit without any training files")
    query.add_argument("--model", type=Path, required=True)
    query.add_argument("left", type=int)
    query.add_argument("right", type=int)
    query.add_argument("--trace", action="store_true")
    inspect = sub.add_parser("inspect", help="show the actual saved gates and connections")
    inspect.add_argument("--model", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            config = CircuitRunConfig.load(args.config) if args.config else CircuitRunConfig()
            report = CircuitRun(config, args.run_dir, show_event).run()
            if args.interactive and (args.run_dir / "model.json").exists():
                console(args.run_dir)
            return 0 if report["state"] == "completed" else 1
        if args.command == "watch":
            watch(args.run_dir, args.follow)
        elif args.command == "status":
            print((args.run_dir / "status.json").read_text(encoding="utf-8"))
        elif args.command == "console":
            console(args.run_dir)
        elif args.command == "control":
            control(args.run_dir, args.action)
        elif args.command == "ask":
            ask(args.model, args.left, args.right, args.trace)
        elif args.command == "inspect":
            circuit = Circuit.load(args.model)
            print("\n".join(circuit.describe()))
            print(f"sha256={circuit.digest}; bytes={len(circuit.encoded())}")
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
