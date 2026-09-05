"""Finite structural-learning trials, live records and independent evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import time
from typing import Callable, Iterable

from .circuit_core import Circuit, MAX_INPUT_BITS
from .circuit_search import CircuitSearch, Example, build_catalog
from .file_io import atomic_replace
from .trial_resources import memory_reading


@dataclass(frozen=True)
class CircuitRunConfig:
    seeds: tuple[int, ...] = (7, 19, 31)
    teaching_bits: int = 4
    repair_examples: int = 48
    audit_bits: int = 8
    transfer_bits: tuple[int, ...] = (16, 32, 64, 256, 1024)
    transfer_random_cases: int = 32
    max_nodes: int = 12
    max_candidates: int = 65536
    max_candidate_evaluations: int = 1_000_000
    max_seconds: float = 180.0
    max_memory_mb: int = 512
    max_disk_mb: int = 96

    def validate(self) -> None:
        if not self.seeds or len(self.seeds) > 10 or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("Use between one and ten distinct seeds.")
        if any(type(seed) is not int or not 0 <= seed <= 2**32 - 1 for seed in self.seeds):
            raise ValueError("Seeds must be unsigned 32-bit integers.")
        if not 2 <= self.teaching_bits <= 5:
            raise ValueError("Teaching width must be between 2 and 5 bits.")
        carry_cases = 4**self.teaching_bits - 3**self.teaching_bits
        if not 1 <= self.repair_examples < carry_cases:
            raise ValueError("Repair examples must leave an independent carry partition.")
        if not self.teaching_bits <= self.audit_bits <= 9:
            raise ValueError("Audit width must cover teaching width and be at most 9 bits.")
        if (not self.transfer_bits or len(set(self.transfer_bits)) != len(self.transfer_bits)
                or any(type(bits) is not int or not self.audit_bits < bits <= MAX_INPUT_BITS
                       for bits in self.transfer_bits)):
            raise ValueError("Transfer widths must be distinct and exceed the audit width.")
        if not 1 <= self.transfer_random_cases <= 128:
            raise ValueError("Use between one and 128 random transfer cases per width.")
        if not 1 <= self.max_nodes <= 32 or not 1 <= self.max_candidates <= 65536:
            raise ValueError("Invalid circuit search size.")
        if not 1 <= self.max_candidate_evaluations <= 10_000_000:
            raise ValueError("Invalid candidate evaluation budget.")
        if not 0 < self.max_seconds <= 3600 or not 64 <= self.max_memory_mb <= 2048:
            raise ValueError("Invalid time or memory budget.")
        if not 1 <= self.max_disk_mb <= 512:
            raise ValueError("Invalid disk budget.")

    @classmethod
    def load(cls, path: Path) -> CircuitRunConfig:
        value = json.loads(path.read_text(encoding="utf-8"))
        for name in ("seeds", "transfer_bits"):
            if name in value:
                value[name] = tuple(value[name])
        result = cls(**value)
        result.validate()
        return result


class RunStopped(RuntimeError):
    pass


class BudgetExceeded(RuntimeError):
    pass


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    atomic_replace(temporary, path)


def save_model(path: Path, circuit: Circuit) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(circuit.encoded())
    atomic_replace(temporary, path)


def teaching_partition(bits: int, repairs: int, seed: int) -> tuple[list[Example], list[Example], list[Example]]:
    """The teacher owns integer addition; the candidate executor cannot call it."""
    rng = random.Random(seed)
    foundation, carry = [], []
    for left in range(1 << bits):
        for right in range(1 << bits):
            example = Example(left, right, left + right)
            (carry if left & right else foundation).append(example)
    rng.shuffle(foundation)
    rng.shuffle(carry)
    # A first carry counterexample is fixed before any model is inspected.
    first = next(example for example in carry if (example.left, example.right) == (1, 1))
    carry.remove(first)
    carry.insert(0, first)
    return foundation, carry[:repairs], carry[repairs:]


def transfer_cases(config: CircuitRunConfig, seed: int) -> list[Example]:
    rng = random.Random(seed ^ 0x9E3779B9)
    pairs = []
    for bits in config.transfer_bits:
        high, full = 1 << (bits - 1), (1 << bits) - 1
        # Fixed edge cases exercise zero, the highest bit and long carries.
        local = [(full, 1), (1, full), (full, full), (high, high), (0, full), (full, 0)]
        local += [(high | rng.getrandbits(bits - 1), high | rng.getrandbits(bits - 1))
                  for _ in range(config.transfer_random_cases)]
        pairs.extend(dict.fromkeys(local))
    return [Example(left, right, left + right) for left, right in pairs]


def local_invariant(circuit: Circuit) -> dict:
    """Exhaustively check a local identity; do not use it to select candidates.

    The identity plus zero initial state and the stated streaming semantics
    supports an induction argument for natural-number addition. This is an
    executable local check, not a proof-assistant verification of Python.
    """
    rows = []
    for left in (0, 1):
        for right in (0, 1):
            for state in (0, 1):
                emitted, following = circuit.step(left, right, state)
                rows.append({"left": left, "right": right, "state": state,
                             "emit": emitted, "next_state": following,
                             "holds": emitted + 2 * following == left + right + state})
    return {"model_sha256": circuit.digest, "identity": "emit + 2*next_state = left + right + state",
            "checked_rows": 8, "valid_rows": sum(row["holds"] for row in rows), "rows": rows,
            "scope": "exhaustive local identity; global argument assumes the documented executor",
            "used_for_selection": False}


def source_fingerprints() -> dict:
    root = Path(__file__).resolve().parents[1]
    files = [Path(__file__).with_name(name) for name in
             ("circuit_core.py", "circuit_search.py", "circuit_runtime.py", "circuit_cli.py")]
    return {str(path.relative_to(root)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in files if path.exists()}


class CircuitRun:
    def __init__(self, config: CircuitRunConfig, run_dir: Path,
                 display: Callable[[dict], None] = lambda _: None):
        config.validate()
        self.config, self.run_dir, self.display = config, run_dir.resolve(), display
        self.started = time.monotonic()
        self.started_cpu = time.process_time()
        self.sequence = 0
        self.phase, self.seed = "initializing", None
        self.last_resource_check = 0.0
        self.last_progress = 0.0
        self.last_state = "running"
        self.events = None
        self.case_file = None
        self.case_bytes = 0
        self.latest_model = None
        self.active_search = None
        self.report: dict = {"schema": "kavi.circuit-trial.v1", "state": "running", "seeds": []}

    def status(self, **extra) -> dict:
        return {"state": self.last_state, "phase": self.phase, "seed": self.seed,
                "elapsed_seconds": round(time.monotonic() - self.started, 3),
                "events": self.sequence, "latest_model": self.latest_model, **extra}

    def emit(self, kind: str, data: dict) -> None:
        self.sequence += 1
        event = {"sequence": self.sequence, "elapsed_seconds": round(time.monotonic() - self.started, 3),
                 "seed": self.seed, "phase": self.phase, "kind": kind, **data}
        if self.events:
            self.events.write(json.dumps(event, separators=(",", ":")) + "\n")
            self.events.flush()
        write_json(self.run_dir / "status.json", self.status(last_event=kind))
        self.display(event)

    def check(self) -> None:
        if (self.run_dir / "STOP").exists():
            raise RunStopped("Stop requested.")
        now = time.monotonic()
        if now - self.started >= self.config.max_seconds:
            raise BudgetExceeded("Wall-time budget exhausted.")
        if (self.run_dir / "PAUSE").exists():
            if self.last_state != "paused":
                self.last_state = "paused"
                self.emit("paused", {"message": "Remove PAUSE or use the resume control. Wall-time limit remains active."})
            while (self.run_dir / "PAUSE").exists():
                if (self.run_dir / "STOP").exists():
                    raise RunStopped("Stop requested while paused.")
                if time.monotonic() - self.started >= self.config.max_seconds:
                    raise BudgetExceeded("Wall-time budget exhausted while paused.")
                time.sleep(0.1)
            self.last_state = "running"
            self.emit("resumed", {})
        if now - self.last_resource_check >= 0.5:
            self.last_resource_check = now
            memory = memory_reading()
            if (memory.get("working_set_bytes") or 0) > self.config.max_memory_mb * 1024**2:
                raise BudgetExceeded("Process working-set budget exhausted.")
            disk = sum(path.stat().st_size for path in self.run_dir.rglob("*") if path.is_file())
            if disk > self.config.max_disk_mb * 1024**2:
                raise BudgetExceeded("Run-directory disk budget exhausted.")

    def evaluate(self, name: str, cases: Iterable[Example], total: int, circuit: Circuit,
                 previous: Circuit, lookup: dict[tuple[int, int], int]) -> dict:
        self.phase = name
        stats = {"cases": 0, "correct": 0, "previous_correct": 0, "gains": 0,
                 "regressions": 0, "lookup_answered": 0, "lookup_correct": 0,
                 "gate_evaluations": 0, "frames": 0}
        started = time.monotonic()
        for index, case in enumerate(cases):
            if index % 128 == 0:
                self.check()
                if time.monotonic() - self.last_progress >= 1.0:
                    self.last_progress = time.monotonic()
                    self.emit("evaluation_progress", {"completed": index, "total": total,
                                                      "correct": stats["correct"], "regressions": stats["regressions"]})
            observed = circuit.execute(case.left, case.right)
            old = previous.execute(case.left, case.right).value
            cached = lookup.get((case.left, case.right))
            correct, old_correct = observed.value == case.target, old == case.target
            stats["cases"] += 1
            stats["correct"] += correct
            stats["previous_correct"] += old_correct
            stats["gains"] += correct and not old_correct
            stats["regressions"] += old_correct and not correct
            stats["lookup_answered"] += cached is not None
            stats["lookup_correct"] += cached == case.target
            stats["gate_evaluations"] += observed.gate_evaluations
            stats["frames"] += observed.frames
            row = [self.seed, name, case.left, case.right, case.target, observed.value, old, cached]
            line = json.dumps(row, separators=(",", ":")) + "\n"
            self.case_file.write(line)
            self.case_bytes += len(line.encode("utf-8"))
        self.case_file.flush()
        stats["seconds"] = round(time.monotonic() - started, 6)
        self.emit("evaluation_complete", {"partition": name, **stats})
        return stats

    def trial(self, catalog: dict, seed: int) -> dict:
        self.seed = seed
        foundation, repairs, held_out = teaching_partition(self.config.teaching_bits, self.config.repair_examples, seed)
        trial_dir = self.run_dir / f"seed-{seed}"
        trial_dir.mkdir()
        teaching = {"foundation": [asdict(case) for case in foundation],
                    "repair": [asdict(case) for case in repairs]}
        write_json(trial_dir / "teaching.json", teaching)
        partitions = {"foundation": len(foundation), "repair": len(repairs), "held_out": len(held_out),
                      "held_out_sha256": hashlib.sha256(json.dumps([asdict(case) for case in held_out],
                                                                 sort_keys=True).encode()).hexdigest()}
        self.phase = "foundation"
        self.emit("phase_started", {"partitions": partitions, "message": "Learn a shared procedure from cases without carries."})
        foundation_search = CircuitSearch(catalog, self.config.max_nodes, self.config.max_candidates,
                                          self.config.max_candidate_evaluations, self.check, self.emit)
        self.active_search = foundation_search
        started = time.monotonic()
        previous = foundation_search.learn(foundation, state_enabled=False)
        foundation_seconds = time.monotonic() - started
        save_model(trial_dir / "foundation.json", previous)
        save_model(self.run_dir / "model.json", previous)
        self.latest_model = "model.json"
        protected = [Example(case.left, case.right, previous.execute(case.left, case.right).value) for case in foundation]
        self.phase = "structural_repair"
        self.emit("phase_started", {"message": "Repair the operation using carry counterexamples; preserve the foundation domain.",
                                    "counterexample": {"left": 1, "right": 1, "actual": previous.execute(1, 1).value, "expected": 2}})
        repair_search = CircuitSearch(catalog, self.config.max_nodes, self.config.max_candidates,
                                      self.config.max_candidate_evaluations, self.check, self.emit)
        self.active_search = repair_search
        started = time.monotonic()
        learned = repair_search.learn(repairs, protected=protected, parent=previous)
        repair_seconds = time.monotonic() - started
        self.active_search = None
        save_model(trial_dir / "learned.json", learned)
        save_model(self.run_dir / "model.json", learned)
        # Seal the graph before creating transfer examples or inspecting final answers.
        write_json(trial_dir / "selection-lock.json", {"sha256": learned.digest, "partitions": partitions,
                                                       "selection_complete": True})
        self.emit("selection_locked", {"sha256": learned.digest, "message": "Final evaluation cannot modify this model."})
        learned = Circuit.load(trial_dir / "learned.json")
        lookup = {(case.left, case.right): case.target for case in [*foundation, *repairs]}
        lookup_bytes = len(json.dumps([[a, b, value] for (a, b), value in sorted(lookup.items())],
                                     separators=(",", ":")).encode("utf-8"))
        evaluations = {}
        evaluations["protected"] = self.evaluate("protected", foundation, len(foundation), learned, previous, lookup)
        evaluations["held_out"] = self.evaluate("held_out", held_out, len(held_out), learned, previous, lookup)
        bound = 1 << self.config.audit_bits
        exhaustive = (Example(a, b, a + b) for a in range(bound) for b in range(bound))
        evaluations["exhaustive"] = self.evaluate("exhaustive", exhaustive, bound**2, learned, previous, lookup)
        transfer = transfer_cases(self.config, seed)
        evaluations["transfer"] = self.evaluate("transfer", transfer, len(transfer), learned, previous, lookup)
        invariant = local_invariant(learned)
        write_json(trial_dir / "local-invariant.json", invariant)
        self.emit("invariant", {"valid_rows": invariant["valid_rows"], "rows": 8, "used_for_selection": False})
        if Circuit.load(trial_dir / "learned.json").digest != learned.digest:
            raise RuntimeError("Sealed model changed during final evaluation.")
        result = {"seed": seed, "partitions": partitions,
                  "foundation": {"sha256": previous.digest, "gates": len(previous.gates), "bytes": len(previous.encoded()),
                                 "seconds": foundation_seconds, "search": asdict(foundation_search.stats)},
                  "learned": {"sha256": learned.digest, "gates": len(learned.gates), "bytes": len(learned.encoded()),
                              "seconds": repair_seconds, "search": asdict(repair_search.stats), "pathway": learned.describe()},
                  "lookup_payload_bytes": lookup_bytes, "evaluations": evaluations,
                  "invariant_valid_rows": invariant["valid_rows"]}
        write_json(trial_dir / "result.json", result)
        self.phase = "seed_complete"
        self.emit("seed_complete", {"gates": len(learned.gates), "bytes": len(learned.encoded()),
                                    "held_out": f"{evaluations['held_out']['correct']}/{evaluations['held_out']['cases']}",
                                    "exhaustive": f"{evaluations['exhaustive']['correct']}/{evaluations['exhaustive']['cases']}",
                                    "transfer": f"{evaluations['transfer']['correct']}/{evaluations['transfer']['cases']}",
                                    "regressions": evaluations["exhaustive"]["regressions"]})
        return result

    def run(self) -> dict:
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.started, self.started_cpu = time.monotonic(), time.process_time()
        write_json(self.run_dir / "config.json", asdict(self.config))
        write_json(self.run_dir / "environment.json", {"python": platform.python_version(), "platform": platform.platform(),
                                                       "pid": os.getpid(), "workers": 1, "device": "CPU",
                                                       "started_utc": datetime.now(timezone.utc).isoformat(),
                                                       "source_sha256": source_fingerprints()})
        self.events = (self.run_dir / "events.jsonl").open("w", encoding="utf-8")
        self.case_file = (self.run_dir / "cases.jsonl").open("w", encoding="utf-8")
        write_json(self.run_dir / "case-schema.json", {"columns": ["seed", "partition", "left", "right", "target",
                                                                  "prediction", "foundation_prediction", "lookup_prediction"]})
        self.report.update(config=asdict(self.config))
        try:
            self.emit("run_started", {"config": asdict(self.config), "message": "Finite structural learning; exact external teacher; no numerical edge weights."})
            self.check()
            self.phase = "catalog"
            catalog_started = time.monotonic()
            catalog = build_catalog(self.check, self.emit)
            write_json(self.run_dir / "search-catalog.json", {str(mask): expr for mask, expr in catalog.items()})
            self.report["catalog_seconds"] = time.monotonic() - catalog_started
            self.report["catalog_functions"] = len(catalog)
            for seed in self.config.seeds:
                self.check()
                self.report["seeds"].append(self.trial(catalog, seed))
                write_json(self.run_dir / "report.json", self.report)
            self.check()
            self.last_state = "completed"
        except RunStopped as error:
            self.last_state = "stopped"
            self.report["reason"] = str(error)
        except BudgetExceeded as error:
            self.last_state = "budget_exhausted"
            self.report["reason"] = str(error)
        except KeyboardInterrupt:
            self.last_state = "stopped"
            self.report["reason"] = "Keyboard interrupt."
        except Exception as error:
            self.last_state = "failed"
            self.report["reason"] = f"{type(error).__name__}: {error}"
        finally:
            if self.active_search is not None:
                self.report["interrupted_search"] = {"seed": self.seed, "phase": self.phase,
                                                     "stats": asdict(self.active_search.stats)}
            self.phase = "finished"
            self.report.update(state=self.last_state, wall_seconds=time.monotonic() - self.started,
                               cpu_seconds=time.process_time() - self.started_cpu, memory=memory_reading(),
                               case_bytes=self.case_bytes)
            self.case_file.close()
            self.report["disk_bytes_before_final_report"] = sum(path.stat().st_size for path in self.run_dir.rglob("*") if path.is_file())
            write_json(self.run_dir / "report.json", self.report)
            self.emit("run_finished", {"state": self.last_state, "completed_seeds": len(self.report["seeds"]),
                                       "wall_seconds": self.report["wall_seconds"], "reason": self.report.get("reason")})
            self.events.close()
        return self.report
