"""Plain-language views of recorded computations, lessons, and measurements."""

from __future__ import annotations


STAGES = {
    "glyph-kinds": "Letters and digits",
    "quantity-and-exact-relations": "Addition and subtraction",
    "unicode-signal-contract": "Keeping each character unchanged",
    "multiscript-glyph-foundations": "Recognizing writing systems",
    "textbook-concepts-expressions-relations": "Expressions and comparisons",
    "typed-compositional-paths": "Connecting skills together",
    "corrective-teaching": "Learning from a mistake",
}


def path_name(value: object) -> str:
    text = str(value or "none")
    if text.startswith("path/composition/"):
        return text.split("/")[2].replace("-", " ") + " connection"
    return (
        text.removeprefix("path/").removeprefix("component/")
        .removeprefix("task/").replace("/", ": ").replace("-", " ")
    )


def format_event(event: dict[str, object]) -> str:
    channel = event["channel"]
    kind = event["kind"]
    stage = STAGES.get(str(event.get("stage")), str(event.get("stage", "Kavi")))
    phase = str(event.get("phase", "")).replace("-", " ")
    if channel == "lessons":
        source = f"\n  Source: {event['source_id']}" if "source_id" in event else ""
        return f"{event.get('title')}\n  {event.get('detail')}{source}"
    if channel == "answers":
        return (
            f"{stage} | {phase}\n"
            f"  Question: {event.get('input')}\n"
            f"  Kavi answered: {event.get('answer')}\n"
            f"  Checked answer: {event.get('expected')}\n"
            "  This is an actual output; the answer key is used by the grader."
        )
    if channel == "pathways":
        lines = [f"{stage} | {phase}", f"  Working on: {event.get('input')}"]
        for index, wave in enumerate(event.get("waves", []), 1):
            lines.append(f"  Step {index}: " + " -> ".join(map(path_name, wave)))
        lines.append(f"  Chosen path: {path_name(event.get('selected_route'))}")
        if "output" in event:
            lines.append(f"  Result leaving this path: {event['output']!r}")
        if event.get("abstain_reason"):
            lines.append(f"  Could not answer: {event['abstain_reason']}")
        lines.append("  These steps describe software connections; execution is serial.")
        return "\n".join(lines)
    if channel == "learning":
        if kind == "parent-archived":
            return (
                f"{stage}: saved the previous version for inspection.\n"
                f"  File: {event.get('archive')}\n"
                "  The saved version does not take part in answering."
            )
        created = ", ".join(map(path_name, event.get("created_routes", []))) or "none"
        modified = ", ".join(map(path_name, event.get("modified_routes", []))) or "none"
        return (
            f"{stage}: proposed change {event.get('decision')}\n"
            f"  New paths: {created}\n  Changed paths: {modified}\n"
            f"  New connections: {len(event.get('created_jumps', []))}; "
            f"adjusted connections: {len(event.get('modified_jumps', []))}\n"
            f"  Active model: {event.get('model_routes')} paths, "
            f"{event.get('model_jump_adapters')} connections.\n"
            f"  Protected check: {float(event.get('protected_before', 0)):.0%} "
            f"-> {float(event.get('protected_after', 0)):.0%}"
        )
    if channel == "grading":
        if kind == "test-case":
            progress = ""
            if "question_index" in event:
                progress = (
                    f"\n  Progress: {event['question_index']}/{event['question_total']}; "
                    f"score so far: {float(event['running_accuracy']):.1%}"
                )
            return (
                f"{stage}: {event.get('result')} | {event.get('partition')}\n"
                f"  Question: {event.get('input')}\n"
                f"  Kavi: {event.get('answer')} | Correct: {event.get('expected')}{progress}"
            )
        if kind == "retention-check":
            scores = ", ".join(
                f"{name}: {float(score):.0%}"
                for name, score in dict(event.get("details", {})).items()
            )
            return f"Checking older skills: {event.get('result')}\n  {scores}"
        if kind == "stage-grade":
            text = (
                f"{stage}: {event.get('result')}\n"
                f"  Protected cases: {float(event.get('protected_accuracy', 0)):.1%}\n"
                f"  Validation cases: {float(event.get('held_out_accuracy', 0)):.1%}"
            )
            if "final_audit_accuracy" in event:
                text += f"\n  Wider audit: {float(event['final_audit_accuracy']):.1%}"
            return text
    return (
        f"Completed stages: {', '.join(event.get('completed_stage_ids', []))}\n"
        f"Next lesson boundary: {event.get('next_gate')}"
    )
