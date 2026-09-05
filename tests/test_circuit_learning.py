from dataclasses import replace
import json
from pathlib import Path
import random
import tempfile
import unittest

from kavi.circuit_core import Circuit, Gate, MAX_INPUT_BITS
from kavi.circuit_runtime import CircuitRun, CircuitRunConfig, local_invariant, teaching_partition
from kavi.circuit_search import CircuitSearch, Example, NoConsistentCircuit, build_catalog, compile_pair, predict_masks


class CircuitLearningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = build_catalog()
        cls.foundation, cls.repairs, cls.held_out = teaching_partition(4, 48, 7)
        cls.parent = CircuitSearch(cls.catalog).learn(cls.foundation, state_enabled=False)
        cls.learner = CircuitSearch(cls.catalog)
        cls.learned = cls.learner.learn(cls.repairs, protected=cls.foundation, parent=cls.parent)

    def test_catalog_covers_every_boolean_function_with_executable_gates(self):
        self.assertEqual(set(self.catalog), set(range(256)))
        for mask, expression in self.catalog.items():
            circuit = compile_pair(expression, self.catalog[0])
            for row in range(8):
                self.assertEqual(circuit.step(row & 1, row >> 1 & 1, row >> 2 & 1), (mask >> row & 1, 0))

    def test_search_accelerator_agrees_with_actual_graphs(self):
        rng = random.Random(123)
        for _ in range(150):
            first, second = rng.randrange(256), rng.randrange(256)
            circuit = compile_pair(self.catalog[first], self.catalog[second])
            left, right = rng.getrandbits(12), rng.getrandbits(12)
            self.assertEqual(predict_masks(first, second, left, right), circuit.execute(left, right).value)

    def test_correction_repairs_shared_operation_and_retains_foundation(self):
        self.assertNotEqual(self.parent.execute(1, 1).value, 2)
        for left in range(32):
            for right in range(32):
                self.assertEqual(self.learned.execute(left, right).value, left + right)
        for case in self.foundation:
            self.assertEqual(self.parent.execute(case.left, case.right).value,
                             self.learned.execute(case.left, case.right).value)
        self.assertGreater(self.learner.stats.counterexamples, 0)
        self.assertLessEqual(len(self.learned.gates), 6)

    def test_roundtrip_executes_large_unseen_inputs_without_teaching_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "model.json"
            path.write_bytes(self.learned.encoded())
            model = Circuit.load(path)
            self.assertEqual(list(Path(directory).iterdir()), [path])
            for bits in (16, 64, 1024, MAX_INPUT_BITS):
                full = (1 << bits) - 1
                self.assertEqual(model.execute(full, 1).value, 1 << bits)
                self.assertEqual(model.execute(full, full).value, full + full)
            self.assertEqual(model.digest, self.learned.digest)

    def test_execution_resets_temporary_state_and_trace_matches_result(self):
        first = self.learned.execute(255, 255, trace=True)
        self.assertEqual(sum(row["emit"] << row["frame"] for row in first.trace), first.value)
        self.assertEqual(first.gate_evaluations, first.frames * len(self.learned.gates))
        self.assertEqual(self.learned.execute(0, 0).value, 0)
        self.assertEqual(self.learned.execute(2, 2).value, 4)
        traced = self.learned.execute(1 << 100, 1, trace=True)
        self.assertEqual(len(traced.trace), 64)
        self.assertTrue(traced.trace_truncated)

    def test_counterexample_contradiction_cannot_replace_parent(self):
        before = self.parent.digest
        search = CircuitSearch(self.catalog)
        with self.assertRaises(NoConsistentCircuit):
            search.learn([Example(1, 1, 2), Example(1, 1, 3)], parent=self.parent)
        self.assertEqual(self.parent.digest, before)

    def test_local_invariant_is_independent_of_teaching_examples(self):
        self.assertEqual(local_invariant(self.learned)["valid_rows"], 8)
        self.assertLess(local_invariant(self.parent)["valid_rows"], 8)
        self.assertFalse(local_invariant(self.learned)["used_for_selection"])

    def test_graph_loader_rejects_cycles_extra_memory_and_unknown_operations(self):
        invalid = [lambda: Circuit((Gate("XOR", (0, 5)),), 5, 3),
                   lambda: Circuit((Gate("ADD", (0, 1)),), 5, 3),
                   lambda: Circuit((), True, 3)]
        for build in invalid:
            with self.assertRaises(ValueError):
                build()
        raw = self.learned.to_dict()
        raw["teaching_examples"] = [[2, 2, 4]]
        with self.assertRaises(ValueError):
            Circuit.from_dict(raw)

    def test_invalid_values_are_rejected_before_execution(self):
        for value in (-1, True, 1.5, 1 << MAX_INPUT_BITS):
            with self.assertRaises(ValueError):
                self.learned.execute(value, 1)

    def test_final_partition_is_disjoint_from_teaching(self):
        teaching = {(case.left, case.right) for case in [*self.foundation, *self.repairs]}
        held_out = {(case.left, case.right) for case in self.held_out}
        self.assertFalse(teaching & held_out)
        self.assertEqual(len(teaching | held_out), 256)
        self.assertEqual((len(self.foundation), len(self.repairs), len(self.held_out)), (81, 48, 127))


class CircuitRuntimeTests(unittest.TestCase):
    def config(self):
        return CircuitRunConfig(seeds=(7,), teaching_bits=2, repair_examples=4, audit_bits=2,
                                transfer_bits=(3, 4), transfer_random_cases=2, max_seconds=15)

    def test_finite_run_persists_model_lock_and_per_case_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "trial"
            report = CircuitRun(self.config(), root).run()
            self.assertEqual(report["state"], "completed", report.get("reason"))
            model = Circuit.load(root / "seed-7/learned.json")
            locked = json.loads((root / "seed-7/selection-lock.json").read_text())
            self.assertEqual(model.digest, locked["sha256"])
            rows = [json.loads(line) for line in (root / "cases.jsonl").read_text().splitlines()]
            exhaustive = [row for row in rows if row[1] == "exhaustive"]
            self.assertEqual(len(exhaustive), 16)
            self.assertEqual(report["seeds"][0]["evaluations"]["exhaustive"]["correct"],
                             sum(row[4] == row[5] for row in exhaustive))

    def test_stop_keeps_an_honest_partial_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "trial"
            def stop(event):
                if event["kind"] == "run_started":
                    (root / "STOP").touch()
            report = CircuitRun(self.config(), root, stop).run()
            self.assertEqual(report["state"], "stopped")
            self.assertEqual(report["seeds"], [])
            self.assertFalse((root / "model.json").exists())

    def test_pause_and_resume_are_observable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "trial"
            events = []
            def control(event):
                events.append(event["kind"])
                if event["kind"] == "run_started":
                    (root / "PAUSE").touch()
                elif event["kind"] == "paused":
                    (root / "PAUSE").unlink()
            report = CircuitRun(self.config(), root, control).run()
            self.assertEqual(report["state"], "completed")
            self.assertIn("paused", events)
            self.assertIn("resumed", events)

    def test_time_budget_does_not_report_success(self):
        with tempfile.TemporaryDirectory() as directory:
            report = CircuitRun(replace(self.config(), max_seconds=0.000001), Path(directory) / "trial").run()
            self.assertEqual(report["state"], "budget_exhausted")

    def test_existing_run_directory_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sentinel = root / "keep.txt"
            sentinel.write_text("existing result")
            with self.assertRaises(FileExistsError):
                CircuitRun(self.config(), root).run()
            self.assertEqual(sentinel.read_text(), "existing result")


if __name__ == "__main__":
    unittest.main()
