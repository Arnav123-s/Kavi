"""Finite connector repair and grounded sentence-learning trials."""

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import platform
import random
import time

from .circuit_runtime import BudgetExceeded, RunStopped, write_json
from .grounded_language import LanguageModel
from .library_cli import show_event
from .library_runtime import LibraryRun, save_library
from .procedure_core import Limits, ProcedureLibrary
from .procedure_optimizations import compile_product
from .trial_resources import memory_reading
from .source_manifest import SourceManifest
from .terminal import configure_utf8_output


@dataclass(frozen=True)
class Config:
    foundation: str
    lessons: str
    lesson_sha256: str
    seed: int = 83
    max_seconds: float = 180
    max_memory_mb: int = 256
    max_disk_mb: int = 32

    def validate(self):
        if not 1 <= self.max_seconds <= 900 or not 64 <= self.max_memory_mb <= 512 or not 1 <= self.max_disk_mb <= 128:
            raise ValueError("Invalid finite run budgets.")
        if type(self.seed) is not int or not 0 <= self.seed < 2**32:
            raise ValueError("Invalid seed.")
        if len(self.lesson_sha256) != 64:
            raise ValueError("Expected a sealed lesson-packet hash.")


class ConnectorLanguageRun(LibraryRun):
    def run(self):
        self.started, self.cpu_started = time.monotonic(), time.process_time()
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.seed = self.config.seed
        self.report = {"schema": "kavi.connector-language-trial.v1", "state": "running",
                       "configuration": asdict(self.config), "python": platform.python_version()}
        self.report["source_files"] = {str(p.relative_to(self.repo)).replace("\\", "/"):
                                       hashlib.sha256(p.read_bytes()).hexdigest()
                                       for p in sorted((self.repo / "kavi").glob("*.py"))}
        with (self.run_dir / "events.jsonl").open("w", encoding="utf-8") as self.event_file, \
                (self.run_dir / "cases.jsonl").open("w", encoding="utf-8") as self.case_file:
            try:
                self._run()
                self.state = "completed"
            except (RunStopped, BudgetExceeded) as error:
                self.state = "stopped" if isinstance(error, RunStopped) else "budget_exhausted"
                self.report["reason"] = str(error)
            except Exception as error:
                self.state = "failed"
                self.report["reason"] = f"{type(error).__name__}: {error}"
            self.report.update(state=self.state, wall_seconds=time.monotonic()-self.started,
                               cpu_seconds=time.process_time()-self.cpu_started, resources=memory_reading())
            write_json(self.run_dir / "result.json", self.report)
            self.emit("run_finished", {"state": self.state, "seconds": self.report["wall_seconds"]})
        return self.report

    def _run(self):
        packet_path = self.repo / self.config.lessons
        raw = packet_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != self.config.lesson_sha256:
            raise ValueError("Lesson packet differs from the reviewed configuration.")
        packet = json.loads(raw)
        if packet.get("schema") != "kavi.connector-language-lessons.v1":
            raise ValueError("Unknown lesson-packet schema.")
        manifest = SourceManifest.load(self.repo / "curriculum/source-manifest.json")
        admitted = {r.source_id: r for r in manifest.sources
                    if r.is_teaching_admissible and "gutenberg" not in r.original_url.casefold()}
        for lesson in packet["teaching"]:
            if lesson["source"] not in admitted and not lesson["source"].startswith("authored:"):
                raise ValueError("Teaching annotation has unapproved source provenance.")
        for passage in packet["passages"]:
            source = admitted.get(passage["source"])
            if source is None or "gutenberg" in source.original_url.casefold():
                raise ValueError("Passages require admitted original sources outside Gutenberg.")
            if hashlib.sha256(passage["text"].encode()).hexdigest() != passage["sha256"]:
                raise ValueError("Passage hash mismatch.")
        old = ProcedureLibrary.load(self.repo / self.config.foundation)
        self.phase = "compile_shared_product"
        new, certificate = compile_product(old)
        self.report["compiler"] = certificate
        self.emit("compiler_verified", {"local_identity_rows": len(certificate["addition_rows"]),
                                       "kind": "supplied compiler, existing learned gates"})
        save_library(self.run_dir / "library.json", new)
        self.report["library"] = {"before_bytes": len(old.encoded()), **new.storage(), "sha256": new.digest}

        self.phase = "teach_sentence_frames"
        language = LanguageModel()
        self.report["blank_language"] = [language.interpret(t) for t in packet["demonstrations"]]
        language.teach(packet["teaching"], self.check, lambda r: self.emit("sentence_frame_acquired", r))
        for definition in packet.get("definitions", []):
            if definition["source"] not in admitted:
                raise ValueError("Definitions require admitted source provenance.")
            language.definitions.setdefault(definition["term"], []).append(definition)
        self.phase = "read_selected_passages"
        for passage in packet["passages"]:
            self.check()
            language.read_passage(passage["text"], passage["source"])
            self.emit("passage_read", {"source": passage["source"], "lexical_nodes": len(language.lexicon),
                                      "scope": "word adjacency; not passage comprehension"})
        encoded = language.encoded()
        (self.run_dir / "language.json").write_bytes(encoded)
        self.report["language"] = {"bytes": len(encoded), "sha256": hashlib.sha256(encoded).hexdigest(),
                                   "rules": len(language.rules), "lexical_nodes": len(language.lexicon),
                                   "passages": language.evidence, "teaching_examples": len(packet["teaching"]),
                                   "training_work": language.training_stats}
        self.emit("models_sealed", {"library": new.digest, "language": self.report["language"]["sha256"]})
        # No teaching or model changes occur below this boundary.
        self.phase = "evaluate_shared_product"
        counts = {"cases": 0, "correct": 0, "identical_swapped_traces": 0, "swap_pairs": 0}
        rng = random.Random(self.seed)
        pairs = [(a, b) for a in range(128) for b in range(128)]
        transfer = [(3, 100000), (100000, 3), (3, 1000000), (1000000, 3),
                    (1000000, 1000000), (0, 2**4095), (1, 2**4095)]
        for bits in (16, 32, 64, 128, 256):
            transfer.extend((rng.getrandbits(bits), rng.getrandbits(bits)) for _ in range(8))
        for index, (a, b) in enumerate(pairs+transfer):
            self.check()
            value = new.execute("multiply", (a, b), check=self.check)
            correct = value.value == a*b
            counts["cases"] += 1
            counts["correct"] += correct
            self.case_file.write(json.dumps(["product", a, b, a*b, value.value, value.iterations])+"\n")
            if index and index % 4096 == 0:
                self.emit("product_audit", counts)
        for a, b in transfer:
            first = new.execute("multiply", (a, b), trace=True, check=self.check,
                                limits=Limits(max_trace_entries=10000))
            second = new.execute("multiply", (b, a), trace=True, check=self.check,
                                 limits=Limits(max_trace_entries=10000))
            counts["swap_pairs"] += 1
            counts["identical_swapped_traces"] += first == second and not first.trace_truncated
        self.report["product"] = counts
        self.report["demonstrations"] = []
        for a, b in transfer[:5]:
            observed = new.execute("multiply", (a, b), trace=True)
            row = {"inputs": [a, b], **asdict(observed)}
            self.report["demonstrations"].append(row)
            self.emit("shared_path_result", row)

        self.phase = "retention_and_traces"
        protected, regressions = 0, 0
        for name, procedure in old.procedures.items():
            cases = [(n,) for n in range(8)] if procedure.arity == 1 else \
                    [(a, b) for a in range(8) for b in range(8)] if procedure.arity == 2 else \
                    [(a, b, c) for a in range(5) for b in range(5) for c in range(3)]
            for args in cases:
                self.check()
                try:
                    expected = old.execute(name, args, check=self.check).value
                except ValueError:
                    continue
                protected += 1
                try:
                    actual = new.execute(name, args, check=self.check).value
                except ValueError:
                    actual = None
                regressions += actual != expected
                self.case_file.write(json.dumps(["retention", name, args, expected, actual])+"\n")
        self.report["retention"] = {"protected_cases": protected, "regressions": regressions}
        bounded = old.execute("power", (20, 10), trace=True)
        complete = old.execute("power", (20, 10), trace=True, limits=Limits(max_trace_entries=10000))
        self.report["trace_check"] = {"calls": complete.calls, "default_records": len(bounded.trace),
                                      "default_truncated": bounded.trace_truncated,
                                      "complete_records": len(complete.trace), "complete_truncated": complete.trace_truncated}

        self.phase = "evaluate_language"
        results = {"cases": 0, "correct": 0, "by_group": {}}
        for case in packet["evaluation"]:
            self.check()
            observed = language.answer(case["text"], new, check=self.check)
            correct = all(observed.get(key) == value for key, value in case["expected"].items())
            group = results["by_group"].setdefault(case["group"], {"cases": 0, "correct": 0})
            group["cases"] += 1
            group["correct"] += correct
            results["cases"] += 1
            results["correct"] += correct
            self.case_file.write(json.dumps(["language", case, observed, correct])+"\n")
            self.emit("language_result", {"sentence": case["text"], "correct": correct, "result": observed})
        self.report["language_evaluation"] = results
        self.report["sources"] = packet["sources"]
        if new.digest != self.report["library"]["sha256"] or language.encoded() != encoded:
            raise RuntimeError("A sealed model changed during evaluation.")
        self.summary = "Finished: shared product, explicit traces and a bounded sentence-learning trial."


def main(argv=None):
    configure_utf8_output()
    parser = argparse.ArgumentParser(description="Repair shared arithmetic and learn grounded sentence frames.")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run")
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--run-dir", type=Path, required=True)
    ask = sub.add_parser("ask")
    ask.add_argument("--run-dir", type=Path, required=True)
    ask.add_argument("text")
    args = parser.parse_args(argv)
    if args.command == "run":
        config = Config(**json.loads(args.config.read_text(encoding="utf-8")))
        report = ConnectorLanguageRun(config, args.run_dir, show_event).run()
        return 0 if report["state"] == "completed" else 1
    result = LanguageModel.load(args.run_dir / "language.json").answer(
        args.text, ProcedureLibrary.load(args.run_dir / "library.json"))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
