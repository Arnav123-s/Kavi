"""Live program acquisition, library inspection and direct procedure queries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .circuit_cli import control
from .library_runtime import LibraryRun, LibraryRunConfig
from .procedure_core import Limits, ProcedureLibrary, describe
from .terminal import configure_utf8_output


def show_event(event):
    prefix = f"[{event['elapsed_seconds']:7.2f}s | seed {event.get('seed') or '-'} | {event['phase']}]"
    kind = event["kind"]
    if kind == "candidate":
        print(f"{prefix} Candidate: {event['gates']} gates; {event['remaining']} remain")
        for line in event["pathway"]: print("    " + line)
    elif kind == "counterexample":
        print(f"{prefix} WRONG {event['left']} - {event['right']} -> {event['actual']}; expected {event['expected']}")
    elif kind == "program_search_progress":
        print(f"{prefix} Searching: {event['candidates']} candidates; {event['retained_vectors']} distinct teaching behaviors")
    elif kind == "program_accepted":
        print(f"{prefix} ACQUIRED {event['program']} | {event['candidates']} candidates")
    elif kind == "evaluation_complete":
        print(f"{prefix} RESULT {event['correct']}/{event['cases']} correct; {event['errors']} execution errors")
    elif kind == "library_growth":
        print(f"{prefix} LIBRARY {event['procedures']} procedures | {event['shared_library_bytes']} bytes | "
              f"separate packages {event['independent_closure_bytes']} bytes | {event['regressions']} protected regressions")
    elif kind == "not_acquired":
        print(f"{prefix} NOT ACQUIRED: {event['reason']}")
    else:
        fields = {key: value for key, value in event.items()
                  if key not in {"sequence", "elapsed_seconds", "seed", "phase", "kind"}}
        print(f"{prefix} {kind}: {json.dumps(fields, ensure_ascii=False, separators=(',', ':'))}")
    sys.stdout.flush()


def ask(path, name, args, trace=False, trace_limit=128):
    library = ProcedureLibrary.load(path)
    result = library.execute(name, tuple(args), trace=trace, limits=Limits(max_trace_entries=trace_limit))
    print(f"{name}{tuple(args)} = {result.value}")
    print(f"calls={result.calls}; frames={result.frames}; gate evaluations={result.gates}; iterations={result.iterations}")
    if trace:
        for row in result.trace: print(json.dumps(row))
        print(f"trace records={len(result.trace)}/{result.trace_events}; truncated={result.trace_truncated}")


def console(path):
    print("Enter a procedure name followed by integers, /library, /trace NAME INPUTS or /quit.")
    while True:
        try:
            line = input("kavi> ").strip()
            if line == "/quit": return
            if line == "/library":
                for item in ProcedureLibrary.load(path).procedures.values():
                    print(f"{item.name}/{item.arity}: " + (describe(item.body) if item.body is not None else f"{len(item.circuit.gates)} gates"))
            elif line:
                parts = line.split()
                trace = parts[0] == "/trace"
                if trace: parts = parts[1:]
                ask(path, parts[0], tuple(map(int, parts[1:])), trace)
        except (EOFError, KeyboardInterrupt):
            print()
            return
        except (ValueError, OSError, IndexError) as error:
            print(f"Cannot execute query: {error}")


def main(argv=None):
    configure_utf8_output()
    parser = argparse.ArgumentParser(prog="kavi-library", description="Acquire and reuse bounded executable procedures.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--interactive", action="store_true")
    for name in ("inspect", "console", "ask"):
        p = sub.add_parser(name)
        p.add_argument("--library", type=Path, required=True)
        if name == "ask":
            p.add_argument("name")
            p.add_argument("inputs", type=int, nargs="+")
            p.add_argument("--trace", action="store_true")
            p.add_argument("--trace-limit", type=int, default=128)
    status = sub.add_parser("status")
    status.add_argument("--run-dir", type=Path, required=True)
    ctrl = sub.add_parser("control")
    ctrl.add_argument("--run-dir", type=Path, required=True)
    ctrl.add_argument("action", choices=("pause", "resume", "stop"))
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            report = LibraryRun(LibraryRunConfig.load(args.config), args.run_dir, show_event).run()
            if args.interactive and (args.run_dir / "library.json").exists(): console(args.run_dir / "library.json")
            return 0 if report["state"] == "completed" else 1
        if args.command == "ask": ask(args.library, args.name, args.inputs, args.trace, args.trace_limit)
        elif args.command == "console": console(args.library)
        elif args.command == "inspect":
            library = ProcedureLibrary.load(args.library)
            for item in library.procedures.values():
                print(f"{item.name}/{item.arity} [{item.contract}]: " +
                      (describe(item.body) if item.body is not None else f"{len(item.circuit.gates)} gates"))
            print(json.dumps({"sha256": library.digest, **library.storage()}))
        elif args.command == "status": print((args.run_dir / "status.json").read_text(encoding="utf-8"))
        elif args.command == "control": control(args.run_dir, args.action)
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
