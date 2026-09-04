"""Focused tests for Kavi's typed, nested pathway composition stage."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from kavi.composition_curriculum import composition_units, held_out_manifest
from kavi.pathway_circuit import (
    CircuitState,
    CompositionCall,
    CompositionExample,
    CompositionLiteral,
    CompositionRule,
    PathwayCircuitCore,
    arithmetic_target_weights,
)
from kavi.pathway_live import _script_sample, _symbol_sample
from kavi.runtime import ArithmeticCurriculum
from kavi.symbol_runtime import SymbolCurriculum
from kavi.unicode_runtime import SCRIPT_SPECS, UnicodeScriptCurriculum


ROOT = Path(__file__).resolve().parents[1]


def prerequisite_core() -> PathwayCircuitCore:
    core = PathwayCircuitCore()
    symbols = SymbolCurriculum(31)
    candidate, _ = core.propose_category_update(
        tuple(_symbol_sample(symbols.event_at(step)) for step in range(1, 9))
    )
    core.promote(candidate)

    arithmetic = ArithmeticCurriculum(31, conflict_every=0)
    for step in range(1, 13):
        event = arithmetic.event_at(step)
        candidate, _ = core.propose_arithmetic_update(
            event,
            arithmetic_target_weights(event.operation),
        )
        core.promote(candidate)

    core.verify_foundation("path/unicode-scalar")
    scripts = UnicodeScriptCurriculum(31)
    candidate, _ = core.propose_category_update(
        tuple(
            _script_sample(scripts.event_at(step))
            for step in range(1, len(SCRIPT_SPECS) * 3 + 1)
        )
    )
    core.promote(candidate)
    return core


def composed_core() -> PathwayCircuitCore:
    core = prerequisite_core()
    for unit in composition_units():
        candidate, _ = core.propose_composition_update(unit.rule)
        core.promote(candidate)
    return core


class CompositionPathTests(unittest.TestCase):
    def test_unified_curriculum_orders_composition_before_language(self) -> None:
        plan = json.loads(
            (ROOT / "curriculum" / "pathway-curriculum.json").read_text(encoding="utf-8")
        )
        stage_ids = [stage["stage_id"] for stage in plan["stages"]]
        self.assertEqual(stage_ids[-1], "typed-compositional-paths")
        self.assertEqual(plan["next_gate"]["stage_id"], "word-forms-and-definitions")
        self.assertEqual(
            plan["next_gate"]["status"],
            "awaiting-model-capability-and-source-review",
        )

    def test_candidate_adds_only_composition_structure(self) -> None:
        core = prerequisite_core()
        parent = core.state
        candidate, delta = core.propose_composition_update(composition_units()[0].rule)

        self.assertEqual(candidate.routes, parent.routes)
        self.assertEqual(candidate.transforms, parent.transforms)
        self.assertEqual(candidate.verified_foundations, parent.verified_foundations)
        self.assertEqual(len(candidate.composition_routes), 1)
        self.assertEqual(len(delta.created_route_ids), 1)
        parent_adapters = parent.adapter_map()
        candidate_adapters = candidate.adapter_map()
        for adapter_id, adapter in parent_adapters.items():
            self.assertEqual(candidate_adapters[adapter_id], adapter)
        self.assertEqual(core.state, parent)

    def test_unseen_nested_programs_reuse_multiple_earlier_paths(self) -> None:
        core = composed_core()
        nested = tuple(
            example
            for example in held_out_manifest()
            if example.event_id.startswith("compose-select-held")
        )
        self.assertEqual(len(nested), 2)
        for example in nested:
            inference = core.infer_composition(example, max_parallel_paths=4)
            self.assertEqual(inference.output_type, example.expected_type)
            self.assertEqual(inference.answer, example.expected_value)
            self.assertTrue(
                any(route.startswith("path/composition/") for route in inference.selected_route_ids)
            )
            self.assertTrue(
                any(route.startswith("path/arithmetic/") for route in inference.selected_route_ids)
            )
            self.assertTrue(
                any(route.startswith("path/unicode-script/") for route in inference.selected_route_ids)
            )
            self.assertTrue(all(len(step) <= 4 for item in inference.steps for step in item.activation_waves))

    def test_rule_cannot_relabel_a_verified_target_contract(self) -> None:
        core = prerequisite_core()
        invalid = CompositionRule(
            "invalid-rule",
            "mislabel-add",
            ("integer", "integer"),
            "boolean",
            "path/arithmetic/add",
        )
        with self.assertRaisesRegex(ValueError, "typed contract"):
            core.propose_composition_update(invalid)

    def test_unknown_type_signature_abstains_instead_of_crossing_paths(self) -> None:
        core = composed_core()
        invalid = CompositionExample(
            "invalid-signature",
            CompositionCall(
                "invalid-add",
                "add",
                (
                    CompositionLiteral("left", "scalar", "a"),
                    CompositionLiteral("right", "integer", 2),
                ),
            ),
            "integer",
            0,
            "add('a', 2)",
        )
        inference = core.infer_composition(invalid)
        self.assertIsNone(inference.answer)
        self.assertIn("type signature", inference.abstain_reason or "")

    def test_depth_budget_stops_an_oversized_tree(self) -> None:
        core = composed_core()
        example = next(
            item for item in held_out_manifest() if item.event_id == "compose-select-held-true"
        )
        inference = core.infer_composition(example, max_depth=2)
        self.assertIsNone(inference.answer)
        self.assertIn("budget exceeded", inference.abstain_reason or "")

    def test_final_audit_reuses_routes_without_mutating_state(self) -> None:
        from kavi.composition_evaluation import AUDIT_CASES, final_audit_manifest

        core = composed_core()
        parent = core.state
        cases = final_audit_manifest()
        self.assertEqual(len(cases), AUDIT_CASES)
        self.assertEqual(len({case.display_text for case in cases}), AUDIT_CASES)
        metrics = core.evaluate_compositions(cases)
        # Preserve the measured baseline failure. The automated teacher must
        # improve this state; the test must not silently call it mastery.
        self.assertEqual(metrics.correct, 62)
        self.assertEqual(metrics.errors, 2)
        self.assertEqual(core.state, parent)

    def test_deep_input_is_rejected_before_recursive_execution(self) -> None:
        node = CompositionLiteral("zero", "integer", 0)
        for index in range(2000):
            node = CompositionCall(f"deep-{index}", "add", (node, node))
        example = CompositionExample("deep", node, "integer", 0, "oversized")
        inference = composed_core().infer_composition(example)
        self.assertIsNone(inference.answer)
        self.assertIn("budget exceeded", inference.abstain_reason or "")

    def test_invalid_scalars_and_mutable_argument_lists_are_rejected(self) -> None:
        for value in ("", "ab", "\ud800", "\udfff"):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                CompositionLiteral("invalid", "scalar", value)
        value = CompositionLiteral("valid", "integer", 1)
        with self.assertRaises(ValueError):
            CompositionCall("invalid", "add", [value, value])

    def test_arithmetic_precision_limit_abstains(self) -> None:
        example = CompositionExample(
            "huge", CompositionCall("huge", "add", (
                CompositionLiteral("left", "integer", 2**60),
                CompositionLiteral("right", "integer", 1),
            )), "integer", 2**60 + 1, "add(2**60, 1)",
        )
        inference = composed_core().infer_composition(example)
        self.assertIsNone(inference.answer)
        self.assertIn("exact float-transform", inference.abstain_reason or "")

    def test_expected_answer_is_not_used_for_inference(self) -> None:
        from dataclasses import replace

        example = held_out_manifest()[0]
        core = composed_core()
        correct_label = core.infer_composition(example)
        wrong_label = core.infer_composition(replace(example, expected_value=-999))
        self.assertEqual(correct_label, wrong_label)
        self.assertEqual(correct_label.answer, example.expected_value)

    def test_state_round_trip_keeps_rules_but_not_program_text(self) -> None:
        core = composed_core()
        mapping = core.state.as_mapping()
        serialized = json.dumps(mapping, ensure_ascii=False)
        self.assertEqual(mapping["schema_version"], 2)
        self.assertEqual(CircuitState.from_mapping(mapping), core.state)
        self.assertNotIn("select(same scripts", serialized)
        self.assertNotIn("subtract(add(20,5)", serialized)


if __name__ == "__main__":
    unittest.main()
