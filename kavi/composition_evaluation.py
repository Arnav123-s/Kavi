"""Final composition audit; never imported by the candidate learner.

This is a seeded engineering test of supplied operators, not a language or
intelligence benchmark. Expected results use a separate integer interpreter
and explicit scalar labels rather than querying learned paths.
"""

from __future__ import annotations

import random

from .pathway_circuit import (
    CompositionCall,
    CompositionExample,
    CompositionLiteral,
    PathValue,
)


AUDIT_SEED = 20260904
AUDIT_CASES = 64
GLYPH_LABELS = {"e": "letter", "v": "letter", "2": "digit", "8": "digit"}
SCRIPT_LABELS = {
    "Д": "cyrillic", "ж": "cyrillic",
    "इ": "devanagari", "उ": "devanagari",
    "文": "han", "語": "han",
}
Node = CompositionLiteral | CompositionCall


def reference_value(node: Node) -> PathValue:
    """Evaluate this tiny test language without calling the model."""

    if isinstance(node, CompositionLiteral):
        return node.value
    values = tuple(reference_value(child) for child in node.arguments)
    if node.operator_id == "add":
        return values[0] + values[1]
    if node.operator_id == "subtract":
        return values[0] - values[1]
    if node.operator_id == "glyph-kind":
        return GLYPH_LABELS[values[0]]
    if node.operator_id == "unicode-script":
        return SCRIPT_LABELS[values[0]]
    if node.operator_id == "same-label":
        return values[0] == values[1]
    if node.operator_id == "select-integer":
        return values[1] if values[0] else values[2]
    raise ValueError(f"Unknown reference operator: {node.operator_id}")


def display_program(node: Node) -> str:
    if isinstance(node, CompositionLiteral):
        return repr(node.value)
    return f"{node.operator_id}({', '.join(map(display_program, node.arguments))})"


def final_audit_manifest(
    *, seed: int = AUDIT_SEED, cases: int = AUDIT_CASES, harder: bool = False
) -> tuple[CompositionExample, ...]:
    """Generate the fixed final checks, after all route promotions have ended.

    Both true and false conditions, negative integers, and varied arithmetic
    subtrees are covered. The default execution budgets accommodate every
    generated program. No audit result is fed back into route selection.
    """

    rng = random.Random(seed)
    examples: list[CompositionExample] = []
    node_index = 0

    def identifier() -> str:
        nonlocal node_index
        node_index += 1
        return f"audit-node-{node_index}"

    def call(operator: str, *children: Node) -> CompositionCall:
        return CompositionCall(identifier(), operator, tuple(children))

    def literal(type_id: str, value: PathValue) -> CompositionLiteral:
        return CompositionLiteral(identifier(), type_id, value)

    def arithmetic(level: int) -> Node:
        if level == 0 or rng.random() < 0.25:
            return literal("integer", rng.randint(-256, 256) if harder else rng.randint(-32, 64))
        return call(
            rng.choice(("add", "subtract")),
            arithmetic(level - 1),
            arithmetic(level - 1),
        )

    for index in range(cases):
        operator = "glyph-kind" if index % 2 == 0 else "unicode-script"
        labels = GLYPH_LABELS if operator == "glyph-kind" else SCRIPT_LABELS
        first = rng.choice(tuple(labels))
        want_equal = index % 4 < 2
        choices = tuple(
            char for char in labels
            if (labels[char] == labels[first]) == want_equal
        )
        second = rng.choice(choices)
        condition = call(
            "same-label",
            call(operator, literal("scalar", first)),
            call(operator, literal("scalar", second)),
        )
        expression = call(
            "select-integer", condition,
            arithmetic(4 if harder else 3), arithmetic(2 if harder else 3),
        )
        examples.append(
            CompositionExample(
                f"final-audit-{seed}-{index:03d}",
                expression,
                "integer",
                reference_value(expression),
                display_program(expression),
            )
        )
    return tuple(examples)
