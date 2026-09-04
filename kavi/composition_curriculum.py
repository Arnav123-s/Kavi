"""Supplied structural contracts for Kavi's typed composition experiment.

These connections are taught directly; the model does not discover the target
operators from the check programs. The protected and held_out cases participate
in promotion decisions, so both are validation sets, not a sealed final test.
"""

from __future__ import annotations

from dataclasses import dataclass

from .pathway_circuit import (
    CompositionCall,
    CompositionExample,
    CompositionLiteral,
    CompositionRule,
    PathValue,
)


Node = CompositionLiteral | CompositionCall


def _literal(node_id: str, type_id: str, value: PathValue) -> CompositionLiteral:
    return CompositionLiteral(node_id, type_id, value)


def _call(node_id: str, operator_id: str, *arguments: Node) -> CompositionCall:
    return CompositionCall(node_id, operator_id, tuple(arguments))


def _example(
    event_id: str,
    expression: CompositionCall,
    expected_type: str,
    expected_value: PathValue,
    display_text: str,
) -> CompositionExample:
    return CompositionExample(
        event_id, expression, expected_type, expected_value, display_text
    )


def _numbers(node_id: str, operator: str, left: int, right: int) -> CompositionCall:
    return _call(
        node_id, operator,
        _literal(f"{node_id}-left", "integer", left),
        _literal(f"{node_id}-right", "integer", right),
    )


def _classify(node_id: str, operator: str, glyph: str) -> CompositionCall:
    return _call(node_id, operator, _literal(f"{node_id}-glyph", "scalar", glyph))


def _compare(operator: str, left: str, right: str) -> CompositionCall:
    return _call(
        "condition", "same-label",
        _classify("left-kind", operator, left),
        _classify("right-kind", operator, right),
    )


@dataclass(frozen=True, slots=True)
class CompositionUnit:
    """One supplied route contract and its disjoint validation cases."""

    rule: CompositionRule
    train: tuple[CompositionExample, ...]
    protected: tuple[CompositionExample, ...]
    held_out: tuple[CompositionExample, ...]


def composition_units() -> tuple[CompositionUnit, ...]:
    """Return the fixed prerequisite order for the composition stage."""

    add = CompositionUnit(
        CompositionRule(
            "rule-add", "add", ("integer", "integer"),
            "integer", "path/arithmetic/add",
        ),
        (_example(
            "compose-add-train", _numbers("add-train", "add", 2, 3),
            "integer", 5, "add(2, 3)",
        ),),
        (_example(
            "compose-add-protected", _numbers("add-protected", "add", 7, 11),
            "integer", 18, "add(7, 11)",
        ),),
        (_example(
            "compose-add-held", _numbers("add-held", "add", 40, 2),
            "integer", 42, "add(40, 2)",
        ),),
    )
    subtract = CompositionUnit(
        CompositionRule(
            "rule-subtract", "subtract", ("integer", "integer"),
            "integer", "path/arithmetic/subtract",
        ),
        (_example(
            "compose-subtract-train", _numbers("subtract-train", "subtract", 9, 4),
            "integer", 5, "subtract(9, 4)",
        ),),
        (_example(
            "compose-subtract-protected",
            _numbers("subtract-protected", "subtract", 15, 6),
            "integer", 9, "subtract(15, 6)",
        ),),
        (_example(
            "compose-subtract-held", _numbers("subtract-held", "subtract", 41, 19),
            "integer", 22, "subtract(41, 19)",
        ),),
    )
    glyph_kind = CompositionUnit(
        CompositionRule(
            "rule-glyph-kind", "glyph-kind", ("scalar",),
            "concept-label", "task/glyph-kind",
        ),
        (_example(
            "compose-glyph-train", _classify("glyph-train", "glyph-kind", "b"),
            "concept-label", "letter", "glyph-kind('b')",
        ),),
        (_example(
            "compose-glyph-protected",
            _classify("glyph-protected", "glyph-kind", "7"),
            "concept-label", "digit", "glyph-kind('7')",
        ),),
        (_example(
            "compose-glyph-held", _classify("glyph-held", "glyph-kind", "m"),
            "concept-label", "letter", "glyph-kind('m')",
        ),),
    )
    unicode_script = CompositionUnit(
        CompositionRule(
            "rule-unicode-script", "unicode-script", ("scalar",),
            "concept-label", "task/unicode-script",
        ),
        (_example(
            "compose-script-train", _classify("script-train", "unicode-script", "б"),
            "concept-label", "cyrillic", "unicode-script('б')",
        ),),
        (_example(
            "compose-script-protected",
            _classify("script-protected", "unicode-script", "आ"),
            "concept-label", "devanagari", "unicode-script('आ')",
        ),),
        (_example(
            "compose-script-held", _classify("script-held", "unicode-script", "字"),
            "concept-label", "han", "unicode-script('字')",
        ),),
    )
    same_label = CompositionUnit(
        CompositionRule(
            "rule-same-label", "same-label", ("concept-label", "concept-label"),
            "boolean", "component/equality-transformer",
        ),
        (_example(
            "compose-same-train", _compare("glyph-kind", "b", "c"),
            "boolean", True, "same-label(glyph-kind('b'), glyph-kind('c'))",
        ),),
        (_example(
            "compose-same-protected", _compare("glyph-kind", "3", "m"),
            "boolean", False, "same-label(glyph-kind('3'), glyph-kind('m'))",
        ),),
        (_example(
            "compose-same-held", _compare("unicode-script", "Α", "ο"),
            "boolean", True, "same-label(unicode-script('Α'), unicode-script('ο'))",
        ),),
    )
    select_integer = CompositionUnit(
        CompositionRule(
            "rule-select-integer", "select-integer",
            ("boolean", "integer", "integer"),
            "integer", "component/select-integer-transformer",
        ),
        (_example(
            "compose-select-train",
            _call(
                "select-train", "select-integer", _compare("glyph-kind", "b", "c"),
                _numbers("true-branch", "add", 2, 3),
                _numbers("false-branch", "subtract", 9, 2),
            ),
            "integer", 5, "select(same letter kinds, add(2,3), subtract(9,2))",
        ),),
        (_example(
            "compose-select-protected",
            _call(
                "select-protected", "select-integer",
                _compare("glyph-kind", "3", "m"),
                _numbers("true-branch", "add", 2, 3),
                _numbers("false-branch", "subtract", 9, 2),
            ),
            "integer", 7, "select(different glyph kinds, add(2,3), subtract(9,2))",
        ),),
        (
            _example(
                "compose-select-held-true",
                _call(
                    "select-held-true", "select-integer",
                    _compare("unicode-script", "А", "о"),
                    _call(
                        "true-branch", "add",
                        _numbers("nested-subtract", "subtract", 20, 8),
                        _numbers("nested-add", "add", 3, 4),
                    ),
                    _numbers("false-branch", "subtract", 100, 1),
                ),
                "integer", 19,
                "select(same scripts, add(subtract(20,8), add(3,4)), subtract(100,1))",
            ),
            _example(
                "compose-select-held-false",
                _call(
                    "select-held-false", "select-integer",
                    _compare("unicode-script", "А", "आ"),
                    _numbers("true-branch", "add", 1, 2),
                    _call(
                        "false-branch", "subtract",
                        _numbers("nested-add-left", "add", 20, 5),
                        _numbers("nested-add-right", "add", 3, 4),
                    ),
                ),
                "integer", 18,
                "select(different scripts, add(1,2), subtract(add(20,5), add(3,4)))",
            ),
        ),
    )
    return add, subtract, glyph_kind, unicode_script, same_label, select_integer


def protected_manifest() -> tuple[CompositionExample, ...]:
    return tuple(example for unit in composition_units() for example in unit.protected)


def held_out_manifest() -> tuple[CompositionExample, ...]:
    return tuple(example for unit in composition_units() for example in unit.held_out)
