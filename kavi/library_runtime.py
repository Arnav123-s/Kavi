"""Finite source-guided acquisition, library ablations and sealed evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import random
import time

from .circuit_core import Circuit
from .circuit_runtime import BudgetExceeded, RunStopped, save_model, write_json
from .circuit_search import CircuitSearch, Example, build_catalog
from .file_io import atomic_replace
from .library_curriculum import LESSONS, audit_cases, partition, source_witness, target, transfer_cases
from .procedure_core import Limits, Procedure, ProcedureLibrary, describe
from .procedure_search import ProgramExample, ProgramSearch, SearchExhausted
from .trial_resources import memory_reading


@dataclass(frozen=True)
class LibraryRunConfig:
    seeds: tuple[int, ...] = (7, 19, 31)
    foundation_model: str = "experiments/circuit-20260905-model.json"
    subtraction_teaching_cases: int = 48
    max_program_nodes: int = 3
    max_program_candidates: int = 20000
    max_candidate_cases: int = 1_000_000
    max_program_seconds: float = 10
    max_seconds: float = 900
    max_memory_mb: int = 512
    max_disk_mb: int = 128

    def validate(self):
        if (not self.seeds or len(self.seeds) > 5 or len(set(self.seeds)) != len(self.seeds)
                or any(type(seed) is not int or not 0 <= seed < 2**32 for seed in self.seeds)):
            raise ValueError("Use one through five distinct unsigned integer seeds.")
        if type(self.subtraction_teaching_cases) is not int or not 8 <= self.subtraction_teaching_cases < 136:
            raise ValueError("Subtraction teaching must leave an independent partition.")
        for value, lower, upper in ((self.max_program_nodes, 1, 4),
                                    (self.max_program_candidates, 1, 100000),
                                    (self.max_candidate_cases, 1, 5000000),
                                    (self.max_memory_mb, 64, 2048), (self.max_disk_mb, 1, 512)):
            if type(value) is not int or not lower <= value <= upper:
                raise ValueError("Invalid integer resource budget.")
        if not 0 < self.max_program_seconds <= 120 or not 0 < self.max_seconds <= 3600:
            raise ValueError("Invalid finite time budget.")

    @classmethod
    def load(cls, path: Path):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if "seeds" in raw: raw["seeds"] = tuple(raw["seeds"])
        config = cls(**raw)
        config.validate()
        return config


def save_library(path: Path, library: ProcedureLibrary):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(library.encoded())
    atomic_replace(temporary, path)


def subtraction_partition(seed: int, count: int):
    pairs = [(a, b) for a in range(16) for b in range(a + 1)]
    random.Random(seed).shuffle(pairs)
    for pair in reversed([(0, 0), (1, 0), (1, 1), (2, 1), (8, 1), (15, 7)]):
        pairs.remove(pair)
        pairs.insert(0, pair)
    return ([Example(a, b, a - b) for a, b in pairs[:count]],
            [ProgramExample((a, b), a - b) for a, b in pairs[count:]])


class LibraryRun:
    def __init__(self, config: LibraryRunConfig, run_dir: Path, display=lambda _: None):
        config.validate()
        self.config, self.run_dir, self.display = config, run_dir.resolve(), display
        self.repo = Path(__file__).resolve().parents[1]
        self.phase, self.seed, self.state = "initializing", None, "running"
        self.summary = "Preparing the declared experiment."
        self.sequence = 0
        self.started = self.cpu_started = 0
        self.last_resource = self.last_control = 0
        self.event_file = self.case_file = None
        self.active_search = None
        self.report = {"schema": "kavi.library-trial.v1", "state": "running", "seeds": []}

    def emit(self, kind, data):
        self.sequence += 1
        event = {"sequence": self.sequence, "elapsed_seconds": round(time.monotonic() - self.started, 3),
                 "seed": self.seed, "phase": self.phase, "kind": kind, **data}
        if self.event_file is not None:
            self.event_file.write(json.dumps(event, separators=(",", ":")) + "\n")
            self.event_file.flush()
        write_json(self.run_dir / "status.json", {"state": self.state, "seed": self.seed,
                   "phase": self.phase, "summary": self.summary, "last_event": kind,
                   "elapsed_seconds": event["elapsed_seconds"]})
        self.display(event)

    def check(self):
        now = time.monotonic()
        if now - self.started >= self.config.max_seconds:
            raise BudgetExceeded("Total automatic-run wall budget exhausted.")
        if now - self.last_control < 0.1:
            return
        self.last_control = now
        if (self.run_dir / "STOP").exists():
            raise RunStopped("Stop requested.")
        if (self.run_dir / "PAUSE").exists():
            self.state = "paused"
            self.emit("paused", {"message": "Wall budget continues while paused."})
            while (self.run_dir / "PAUSE").exists():
                if (self.run_dir / "STOP").exists(): raise RunStopped("Stop requested while paused.")
                if time.monotonic() - self.started >= self.config.max_seconds:
                    raise BudgetExceeded("Wall budget exhausted while paused.")
                time.sleep(0.1)
            self.state = "running"
            self.emit("resumed", {})
        if now - self.last_resource >= 0.5:
            self.last_resource = now
            memory = memory_reading()
            if (memory.get("working_set_bytes") or 0) > self.config.max_memory_mb * 1024**2:
                raise BudgetExceeded("Sampled process memory threshold exceeded.")
            size = sum(p.stat().st_size for p in self.run_dir.rglob("*") if p.is_file())
            if size > self.config.max_disk_mb * 1024**2:
                raise BudgetExceeded("Sampled run-directory threshold exceeded.")

    def evaluate(self, library, name, cases, partition_name, variant="shared"):
        self.phase = f"evaluate:{name}:{variant}:{partition_name}"
        counts = {"cases": 0, "correct": 0, "errors": 0, "calls": 0, "gates": 0, "iterations": 0}
        started = time.monotonic()
        for index, example in enumerate(cases):
            if index % 64 == 0:
                self.check()
            error, prediction, observed = None, None, None
            try:
                observed = library.execute(name, example.inputs, check=self.check)
                prediction = observed.value
            except ValueError as failure:
                error = str(failure)
                observed = getattr(failure, "execution", None)
                counts["errors"] += 1
            counts["cases"] += 1
            counts["correct"] += prediction == example.target
            if observed is not None:
                counts["calls"] += observed.calls
                counts["gates"] += observed.gates
                counts["iterations"] += observed.iterations
            row = [self.seed, name, variant, partition_name, example.inputs, example.target, prediction, error]
            self.case_file.write(json.dumps(row, separators=(",", ":")) + "\n")
            if index and index % 8192 == 0:
                self.emit("evaluation_progress", {"procedure": name, "partition": partition_name, **counts})
        self.case_file.flush()
        counts["seconds"] = time.monotonic() - started
        self.emit("evaluation_complete", {"procedure": name, "variant": variant,
                                           "partition": partition_name, **counts})
        return counts

    def learn_program(self, library, lesson, examples, variant, trial_dir):
        self.phase = f"acquire:{lesson.name}:{variant}"
        self.summary = f"Learning {lesson.name}; {variant} vocabulary. All search attempts count toward the declared budget."
        self.emit("lesson", {"name": lesson.name, "variant": variant, "purpose": lesson.purpose,
                             "source_scope": lesson.source_scope, "teaching_cases": len(examples)})
        search = ProgramSearch(library, self.config.max_program_nodes, self.config.max_program_candidates,
                               self.config.max_candidate_cases, self.config.max_program_seconds,
                               check=self.check, notify=self.emit)
        self.active_search = search
        try:
            body = search.learn(lesson.arity, examples)
            learned = Procedure(lesson.name, lesson.arity, lesson.contract, body=body)
            library.add(learned)
            result = {"state": "acquired", "program": describe(body), "body": body,
                      "stats": asdict(search.stats), "storage": library.storage()}
        except SearchExhausted as error:
            result = {"state": "not_acquired", "reason": str(error), "stats": asdict(search.stats)}
            self.emit("not_acquired", {"name": lesson.name, "variant": variant, **result})
        self.active_search = None
        write_json(trial_dir / f"{lesson.name}-{variant}-search.json", result)
        return result

    def trial(self, catalog, foundation, seed):
        self.seed = seed
        trial_dir = self.run_dir / f"seed-{seed}"
        trial_dir.mkdir()
        library = ProcedureLibrary([Procedure("add", 2, "naturals", circuit=foundation)])
        initial_size = len(library.encoded())
        self.phase = "acquire:subtract"
        self.summary = "Acquiring a borrow transition from formal exercises based on De Morgan's subtraction lesson."
        teaching, subtraction_final = subtraction_partition(seed, self.config.subtraction_teaching_cases)
        self.emit("lesson", {"name": "subtract", "source_scope": "subtraction", "teaching_cases": len(teaching)})
        search = CircuitSearch(catalog, check=self.check, notify=self.emit)
        self.active_search = search
        subtraction = search.learn(teaching, parent=foundation)
        self.active_search = None
        library.add(Procedure("subtract", 2, "ordered_pair", circuit=subtraction))
        save_model(trial_dir / "subtract.json", subtraction)
        subtraction_stats = asdict(search.stats)
        base = ProcedureLibrary.from_dict(library.to_dict())
        save_library(self.run_dir / "library.json", library)
        growth = [{"after": "imported_add", "shared_library_bytes": initial_size, "procedures": 1},
                  {"after": "subtract", **library.storage()}]
        learned_records, controls, final_banks = {}, {}, {"subtract": subtraction_final}
        guards = {"add": [ProgramExample((n, n + 1), 2*n + 1) for n in range(16)],
                  "subtract": [ProgramExample((e.left, e.right), e.target) for e in teaching]}
        guard_transitions = []
        teacher_record = {"subtract": [asdict(e) for e in teaching]}
        for lesson in LESSONS:
            self.check()
            examples, held_out = partition(lesson, seed)
            teacher_record[lesson.name] = [asdict(e) for e in examples]
            final_banks[lesson.name] = held_out
            before = {name: p.to_dict() for name, p in library.procedures.items()}
            result = self.learn_program(library, lesson, examples, "shared", trial_dir)
            learned_records[lesson.name] = result
            if result["state"] == "acquired":
                checked, regressions = 0, 0
                for name, bank in guards.items():
                    if library.procedures[name].to_dict() != before[name]:
                        raise RuntimeError("An earlier definition changed during append-only extension.")
                    for example in bank:
                        checked += 1
                        regressions += library.execute(name, example.inputs, check=self.check).value != example.target
                if regressions:
                    raise RuntimeError("An earlier protected procedure regressed.")
                guard_transitions.append({"after": lesson.name, "cases": checked, "regressions": regressions})
                guards[lesson.name] = examples
                growth.append({"after": lesson.name, **library.storage()})
                save_library(self.run_dir / "library.json", library)
                save_library(trial_dir / f"after-{lesson.name}.json", library)
                self.emit("library_growth", {"procedure": lesson.name, **library.storage(),
                                             "protected_cases": checked, "regressions": regressions})
            control = ProcedureLibrary.from_dict(base.to_dict())
            controls[lesson.name] = (control, self.learn_program(control, lesson, examples, "base_only", trial_dir))
            if controls[lesson.name][1]["state"] == "acquired":
                save_library(trial_dir / f"{lesson.name}-base-library.json", control)
        write_json(trial_dir / "teaching.json", teacher_record)
        save_library(trial_dir / "library.json", library)
        self.phase = "seal"
        lock = {"sha256": library.digest, "state": "all task selection complete before final evaluation"}
        write_json(trial_dir / "selection-lock.json", lock)
        self.emit("selection_sealed", lock)
        evaluations = {}
        for name in ["add", "subtract", *(lesson.name for lesson in LESSONS)]:
            self.summary = f"Final independent evaluation of {name}; the selected library is sealed."
            groups = {"audit": audit_cases(name), "transfer": transfer_cases(name, seed)}
            if name in final_banks: groups = {"held_out": final_banks[name], **groups}
            evaluations[name] = {label: self.evaluate(library, name, bank, label) for label, bank in groups.items()}
            if name in controls:
                control, record = controls[name]
                if record["state"] == "acquired":
                    record["evaluations"] = {label: self.evaluate(control, name, bank, label, "base_only")
                                             for label, bank in groups.items()}
        # These identity checks occur only after all task selection has ended.
        invariant = []
        for a, b, borrow in ((a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)):
            emit, following = subtraction.step(a, b, borrow)
            invariant.append({"left": a, "right": b, "borrow": borrow, "emit": emit,
                              "next_borrow": following, "holds": emit - 2*following == a - b - borrow})
        write_json(trial_dir / "subtraction-invariant.json", {"sha256": subtraction.digest, "rows": invariant})
        if library.digest != lock["sha256"]:
            raise RuntimeError("The selected library changed during final evaluation.")
        result = {"seed": seed, "initial_library_bytes": initial_size, "storage": library.storage(),
                  "sha256": library.digest, "subtraction": {"gates": len(subtraction.gates),
                  "bytes": len(subtraction.encoded()), "search": subtraction_stats,
                  "invariant_valid_rows": sum(row["holds"] for row in invariant)},
                  "acquisition": learned_records, "base_only": {name: record for name, (_, record) in controls.items()},
                  "evaluations": evaluations, "growth": growth, "protected_transitions": guard_transitions,
                  "retention_mechanism": "append-only immutable definitions; shared-definition repair is not tested"}
        write_json(trial_dir / "result.json", result)
        self.phase = "seed_complete"
        self.summary = f"Seed {seed}: {len(library.procedures)} procedures retained in {len(library.encoded())} canonical bytes."
        self.emit("seed_complete", {"procedures": len(library.procedures), **library.storage(),
                                    "acquired_new_programs": sum(r["state"] == "acquired" for r in learned_records.values())})
        return result

    def run(self):
        # Validate external prerequisites before creating a run or starting its clock.
        witness, extracts = source_witness(self.repo)
        foundation = Circuit.load(self.repo / self.config.foundation_model)
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.started, self.cpu_started = time.monotonic(), time.process_time()
        fingerprints = {f"kavi/{p.name}": hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (self.repo / "kavi").glob("*.py")}
        write_json(self.run_dir / "config.json", asdict(self.config))
        write_json(self.run_dir / "source-witness.json", witness)
        extracts_dir = self.run_dir / "source-extracts"
        extracts_dir.mkdir()
        for name, content in extracts.items(): (extracts_dir / f"{name}.txt").write_text(content, encoding="utf-8")
        write_json(self.run_dir / "environment.json", {"python": platform.python_version(),
                   "platform": platform.platform(), "device": "CPU", "workers": 1,
                   "started_utc": datetime.now(timezone.utc).isoformat(), "source_sha256": fingerprints,
                   "foundation_sha256": foundation.digest})
        self.event_file = (self.run_dir / "events.jsonl").open("w", encoding="utf-8")
        self.case_file = (self.run_dir / "cases.jsonl").open("w", encoding="utf-8")
        write_json(self.run_dir / "case-schema.json", {"columns": ["seed", "procedure", "variant", "partition",
                                                                  "inputs", "target", "prediction", "error"]})
        self.report.update(config=asdict(self.config), source=witness, foundation_sha256=foundation.digest,
                           search_execution_limits=asdict(ProgramSearch(ProcedureLibrary()).limits),
                           inference_execution_limits=asdict(Limits()),
                           search_cache_entry_limit=100000)
        try:
            self.summary = "Source-guided formal exercises; language interpretation is supplied by the teacher."
            self.emit("run_started", {"config": asdict(self.config), "source": witness["title"],
                                      "boundary": witness["teaching_boundary"]})
            catalog = build_catalog(self.check, self.emit)
            for seed in self.config.seeds:
                self.report["seeds"].append(self.trial(catalog, foundation, seed))
                write_json(self.run_dir / "report.json", self.report)
            self.state = "completed"
            self.summary = "All declared experiments finished. Check final accuracy and exhausted tasks; no graduate-level capability is claimed."
        except RunStopped as error:
            self.state, self.summary = "stopped", str(error)
        except BudgetExceeded as error:
            self.state, self.summary = "budget_exhausted", str(error)
        except KeyboardInterrupt:
            self.state, self.summary = "stopped", "Keyboard interrupt."
        except Exception as error:
            self.state, self.summary = "failed", f"{type(error).__name__}: {error}"
        finally:
            if self.active_search is not None:
                self.report["interrupted_search"] = {"phase": self.phase, "stats": asdict(self.active_search.stats)}
            self.case_file.close()
            self.report.update(state=self.state, summary=self.summary, wall_seconds=time.monotonic() - self.started,
                               cpu_seconds=time.process_time() - self.cpu_started, memory=memory_reading(),
                               disk_bytes_before_report=sum(p.stat().st_size for p in self.run_dir.rglob("*") if p.is_file()))
            write_json(self.run_dir / "report.json", self.report)
            self.phase = "finished"
            self.emit("run_finished", {"state": self.state, "summary": self.summary,
                                       "wall_seconds": self.report["wall_seconds"]})
            self.event_file.close()
        return self.report
