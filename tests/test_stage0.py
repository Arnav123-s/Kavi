"""Tests for the first falsifiable hard-pathway slice."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from kritjnah.graph import PathwayFabric
from kritjnah.learning import IndependentEvaluator, VerifierGatedLearner
from kritjnah.runtime import LiveRuntime, RuntimeConfig
from kritjnah.types import ArithmeticEvent, Information, Operation, SignalType


class HardPathTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fabric = PathwayFabric()

    def test_wrong_type_has_no_route(self) -> None:
        wrong_information = Information(
            event_id="wrong-type",
            correlation_id="wrong-type",
            kind=SignalType.RELATION,
            payload=(1.0,),
            operation=Operation.ADD,
        )
        route = self.fabric.shortest_compatible_route(
            wrong_information,
            start="quantity-mid",
            goal="typed-join",
        )
        self.assertIsNone(route)

    def test_route_is_deterministic_and_hard_typed(self) -> None:
        event = ArithmeticEvent("event", 3, 4, Operation.ADD, "correlation")
        quantity, _ = self.fabric.facets(event)
        first = self.fabric.shortest_compatible_route(quantity)
        second = self.fabric.shortest_compatible_route(quantity)
        self.assertIsNotNone(first)
        self.assertEqual(first, second)
        self.assertEqual(
            first.pipe_ids,
            ("quantity-ingress", "quantity-to-join"),
        )

    def test_constructive_and_destructive_joins_are_exposed(self) -> None:
        normal = ArithmeticEvent("normal", 2, 3, Operation.ADD, "normal")
        conflicted = ArithmeticEvent(
            "conflict", 2, 3, Operation.ADD, "conflict", conflicted=True
        )
        normal_result = self.fabric.infer(normal)
        conflicted_result = self.fabric.infer(conflicted)
        self.assertGreater(normal_result.interference, 0.0)
        self.assertLess(conflicted_result.interference, 0.0)
        self.assertIsNone(conflicted_result.answer)
        self.assertIsNotNone(conflicted_result.abstain_reason)

    def test_verified_candidate_can_reduce_current_error(self) -> None:
        event = ArithmeticEvent("learn", 4, 3, Operation.ADD, "learn")
        before = self.fabric.infer(event)
        learner = VerifierGatedLearner(IndependentEvaluator())
        feedback = learner.observe(self.fabric, before)
        after = self.fabric.infer(event)
        self.assertEqual(feedback.valence.value, "negative")
        self.assertTrue(feedback.promoted)
        self.assertLess(
            abs(after.raw_value - event.target),
            abs(before.raw_value - event.target),
        )

    def test_route_budget_can_force_explicit_abstention(self) -> None:
        event = ArithmeticEvent("budget", 4, 1, Operation.SUBTRACT, "budget")
        result = self.fabric.infer(event, max_active_routes=1)
        self.assertIsNone(result.answer)
        self.assertIn("route budget", result.abstain_reason)


class RuntimeControlTests(unittest.TestCase):
    def test_existing_stop_file_stops_before_first_event(self) -> None:
        with TemporaryDirectory() as directory:
            stop_file = Path(directory) / "stop"
            stop_file.write_text("stop", encoding="utf-8")
            output: list[str] = []
            runtime = LiveRuntime(
                RuntimeConfig(steps=3, interval_ms=0, stop_file=stop_file),
                emit=output.append,
            )
            summary = runtime.run()
        self.assertTrue(summary.stopped)
        self.assertEqual(summary.completed_steps, 0)
        self.assertTrue(any("stop requested" in line for line in output))


if __name__ == "__main__":
    unittest.main()
