from dataclasses import replace
import hashlib
from itertools import product
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

from kavi.circuit_core import Circuit, Gate
from kavi.circuit_search import CircuitSearch, Example, build_catalog
from kavi.library_curriculum import LESSONS, SCALING_LESSON, partition, source_witness, target, transfer_cases
from kavi.library_runtime import LibraryRun, LibraryRunConfig, subtraction_partition
from kavi.circuit_runtime import RunStopped, BudgetExceeded
from kavi.procedure_core import ExecutionLimit, Limits, Procedure, ProcedureLibrary
from kavi.procedure_search import ProgramExample, ProgramSearch, SearchExhausted


def adder():
    return Circuit((Gate("XOR", (0, 1)), Gate("XOR", (5, 2)), Gate("XOR", (0, 2)),
                    Gate("AND", (5, 7)), Gate("XOR", (8, 0))), 6, 9)


def base():
    return ProcedureLibrary([Procedure("add", 2, "naturals", circuit=adder())])


def arithmetic_library():
    lib = base()
    lib.add(Procedure("multiply", 2, "naturals", body=("repeat", "add", ("arg", 1), ("const", 0), ("arg", 0))))
    lib.add(Procedure("power", 2, "naturals", body=("repeat", "multiply", ("arg", 1), ("const", 1), ("arg", 0))))
    lib.add(Procedure("factorial", 1, "naturals", body=("range", "multiply", ("arg", 0), ("const", 1))))
    return lib


class ProcedureTests(unittest.TestCase):
    def test_isolated_serialization_and_actual_reused_calls(self):
        library = arithmetic_library()
        restored = ProcedureLibrary.from_dict(json.loads(library.encoded()))
        with patch("kavi.library_curriculum.target", side_effect=AssertionError("teacher unavailable")):
            result = restored.execute("power", (3, 4), trace=True)
        self.assertEqual(result.value, 81)
        self.assertTrue(any(row["procedure"] == "multiply" for row in result.trace))
        self.assertTrue(any(row["procedure"] == "add" for row in result.trace))
        self.assertGreater(result.gates, 0)
        self.assertEqual(restored.digest, library.digest)

    def test_range_zero_and_nested_iteration(self):
        library = arithmetic_library()
        self.assertEqual(library.execute("factorial", (0,)).value, 1)
        self.assertEqual(library.execute("factorial", (8,)).value, 40320)
        self.assertEqual(library.execute("multiply", (123, 0)).value, 0)
        self.assertEqual(library.execute("power", (0, 0)).value, 1)

    def test_temporary_state_resets_and_long_inputs(self):
        library = base()
        first = library.execute("add", (2**1024 - 1, 1))
        library.execute("add", (7, 9))
        self.assertEqual(first.value, 2**1024)
        self.assertEqual(library.execute("add", (2**1024 - 1, 1)), first)

    def test_cycles_unknown_fields_and_nonprimitive_constants_rejected(self):
        with self.assertRaises(ValueError):
            base().add(Procedure("cycle", 1, "naturals", body=("call", "cycle", ("arg", 0))))
        raw = base().to_dict()
        raw["examples"] = [[2, 2, 4]]
        with self.assertRaises(ValueError): ProcedureLibrary.from_dict(raw)
        with self.assertRaises(ValueError):
            base().add(Procedure("answer", 1, "naturals", body=("const", 42)))
        with self.assertRaises(ValueError):
            base().add(Procedure("bad", 1, "naturals", body=("call", "add", ("arg", 1), ("const", 0))))

    def test_execution_budget_counts_partial_nested_work(self):
        library = arithmetic_library()
        with self.assertRaises(ExecutionLimit) as context:
            library.execute("power", (4, 5), limits=Limits(max_iterations=12))
        self.assertGreater(context.exception.execution.gates, 0)
        self.assertLessEqual(context.exception.execution.iterations, 12)
        with self.assertRaises(ValueError): library.execute("add", (-1, 2))

    def test_imported_procedure_unchanged_by_extension(self):
        library = base()
        before = library.procedures["add"].to_dict()
        library.add(Procedure("double", 1, "naturals", body=("call", "add", ("arg", 0), ("arg", 0))))
        self.assertEqual(library.procedures["add"].to_dict(), before)
        for n in range(32): self.assertEqual(library.execute("add", (n, 31-n)).value, 31)
        self.assertGreater(library.storage()["independent_closure_bytes"], library.storage()["shared_library_bytes"])

    def test_search_acquires_program_without_teacher_at_inference(self):
        library = base()
        examples = [ProgramExample((n,), n*2) for n in (0, 1, 3, 5)]
        search = ProgramSearch(library, max_nodes=2)
        body = search.learn(1, examples)
        library.add(Procedure("double", 1, "naturals", body=body))
        self.assertEqual(library.execute("double", (1234567,)).value, 2469134)
        self.assertEqual(search.stats.verification_cases, len(examples))
        self.assertGreater(search.stats.executed_gates, 0)

    def test_search_can_select_repeated_use_of_acquired_procedure(self):
        library = base()
        bank = [ProgramExample((a, b), a*b) for a, b in product(range(4), repeat=2)]
        search = ProgramSearch(library, max_nodes=1, max_seconds=3)
        body = search.learn(2, bank)
        library.add(Procedure("multiply", 2, "naturals", body=body))
        self.assertEqual(library.execute("multiply", (9, 13)).value, 117)
        self.assertEqual(body[0], "repeat")

    def test_search_reports_budget_exhaustion(self):
        search = ProgramSearch(base(), max_candidates=1)
        with self.assertRaises(SearchExhausted):
            search.learn(1, [ProgramExample((0,), 1), ProgramExample((3,), 27)])
        self.assertEqual(search.stats.state, "exhausted")
        self.assertEqual(search.stats.candidates, 1)

    def test_large_quantity_lesson_acquires_usable_call_order(self):
        library = base()
        library.add(Procedure("multiply", 2, "naturals", body=("repeat", "add", ("arg", 0), ("const", 0), ("arg", 1))))
        original = library.procedures["multiply"].to_dict()
        teaching, final = partition(SCALING_LESSON, 43)
        self.assertFalse({e.inputs for e in teaching} & {e.inputs for e in final})
        body = ProgramSearch(library, max_nodes=1).learn(2, teaching)
        library.add(Procedure("scale", 2, "naturals", body=body))
        self.assertEqual(library.procedures["multiply"].to_dict(), original)
        self.assertEqual(library.execute("scale", (2**256, 31)).value, 31 * 2**256)
        for example in final:
            self.assertEqual(library.execute("scale", example.inputs).value, example.target)
        with self.assertRaises(ExecutionLimit): library.execute("scale", (31, 2**256))
        power = next(lesson for lesson in LESSONS if lesson.name == "power")
        bank, _ = partition(power, 43)
        learned = ProgramSearch(library, max_nodes=1).learn(2, bank)
        library.add(Procedure("power", 2, "naturals", body=learned))
        self.assertEqual(library.execute("power", (17, 10)).value, 17**10)

    def test_followup_transfer_scope_and_option_validation(self):
        for name in ("power", "factorial"):
            old = {e.inputs for e in transfer_cases(name, 7)}
            new = {e.inputs for e in transfer_cases(name, 43, extended=True)}
            self.assertTrue(new)
            self.assertFalse(old & new)
        with self.assertRaises(ValueError): LibraryRunConfig(scaling_lesson=1).validate()

    def test_subtraction_acquisition_and_local_identity(self):
        teaching, held_out = subtraction_partition(11, 48)
        learned = CircuitSearch(build_catalog()).learn(teaching, parent=adder())
        for example in held_out:
            self.assertEqual(learned.execute(*example.inputs).value, example.target)
        for a, b, state in product((0, 1), repeat=3):
            out, following = learned.step(a, b, state)
            self.assertEqual(out - 2*following, a - b - state)

    def test_teacher_splits_and_long_input_orders(self):
        for lesson in LESSONS:
            teaching, final = partition(lesson, 7)
            self.assertTrue(teaching and final)
            self.assertFalse({e.inputs for e in teaching} & {e.inputs for e in final})
        cases = transfer_cases("multiply", 7)
        self.assertTrue(any(e.inputs[0] > 10000 and e.inputs[1] < 41 for e in cases))
        self.assertTrue(any(e.inputs[1] > 10000 and e.inputs[0] < 41 for e in cases))

    def test_source_fingerprint_and_scope_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "curriculum").mkdir()
            (root / "private/sources").mkdir(parents=True)
            raw = "\n".join(f"{n}. Test passage {n}." for n in range(28, 210)).encode()
            (root / "private/sources/witness.txt").write_bytes(raw)
            metadata = {"source_id": "test", "local_path": "private/sources/witness.txt", "sha256": hashlib.sha256(raw).hexdigest(),
                        "title": "Test witness", "author": "Test author", "catalog_url": "https://example.invalid/test"}
            (root / "curriculum/arithmetic-original.json").write_text(json.dumps(metadata))
            (root / "curriculum/source-manifest.json").write_text(json.dumps({"sources": [{"source_id": "test", "status": "approved", "license_class": "public-domain-us"}]}))
            witness, extracts = source_witness(root)
            self.assertEqual(witness["scopes"]["addition"]["paragraphs"], [28, 30])
            self.assertIn("29. Test passage", extracts["addition"])
            (root / "private/sources/witness.txt").write_bytes(raw + b"changed")
            with self.assertRaises(ValueError): source_witness(root)

    def test_stop_and_wall_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            run = LibraryRun(LibraryRunConfig(seeds=(7,)), path)
            run.started = time.monotonic()
            (path / "STOP").touch()
            with self.assertRaises(RunStopped): run.check()
            (path / "STOP").unlink()
            run.started -= 901
            with self.assertRaises(BudgetExceeded): run.check()

    def test_small_end_to_end_run_and_preserved_existing_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            foundation = root / "foundation.json"
            foundation.write_bytes(adder().encoded())
            config = LibraryRunConfig(seeds=(7,), foundation_model=str(foundation), max_program_nodes=1)
            source = {"title": "Test source", "teaching_boundary": "Generated test fixture"}
            def audit(name):
                args = (2,) if name == "double" else (3, 2)
                return [ProgramExample(args, target(name, args))]
            with patch("kavi.library_runtime.source_witness", return_value=(source, {})), \
                 patch("kavi.library_runtime.LESSONS", LESSONS[:1]), \
                 patch("kavi.library_runtime.audit_cases", side_effect=audit), \
                 patch("kavi.library_runtime.transfer_cases", side_effect=lambda name, seed: audit(name)):
                path = root / "run"
                report = LibraryRun(config, path).run()
                self.assertEqual(report["state"], "completed", report.get("summary"))
                self.assertEqual(report["seeds"][0]["acquisition"]["double"]["state"], "acquired")
                library = ProcedureLibrary.load(path / "library.json")
                self.assertEqual((path / "library.json").stat().st_size, len(library.encoded()))
                self.assertEqual(library.execute("double", (123,)).value, 246)
                with self.assertRaises(FileExistsError): LibraryRun(config, path).run()


if __name__ == "__main__":
    unittest.main()
