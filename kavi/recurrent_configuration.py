"""Infer recurrent finite-state configurations from labeled token sequences."""

from collections import deque
from dataclasses import dataclass
import json
import random
import time


@dataclass(frozen=True)
class Configuration:
    """A deterministic Moore machine, with state zero as its entry point."""

    alphabet: tuple[str, ...]
    transitions: tuple[tuple[int, ...], ...]
    outputs: tuple[int | None, ...]

    def __post_init__(self):
        if not self.transitions or len(self.transitions) != len(self.outputs):
            raise ValueError("A configuration needs equally many states and outputs")
        if len(set(self.alphabet)) != len(self.alphabet) or any(
                not isinstance(s, str) or not s for s in self.alphabet):
            raise ValueError("Tokens must be distinct nonempty strings")
        size = len(self.outputs)
        if any(len(row) != len(self.alphabet) or any(
                type(target) is not int or not -1 <= target < size for target in row)
                for row in self.transitions):
            raise ValueError("Invalid transition table")
        if any(y is not None and type(y) is not int for y in self.outputs):
            raise ValueError("Outputs must be integers or unresolved")

    def predict(self, tokens, *, check=None):
        state = 0
        columns = {s: i for i, s in enumerate(self.alphabet)}
        for token in tokens:
            if check:
                check()
            column = columns.get(token)
            if column is None:
                return None
            state = self.transitions[state][column]
            if state < 0:
                return None
        return self.outputs[state]

    def trace(self, tokens):
        state = 0
        visited = [state]
        steps = []
        for token in tokens:
            before = state
            if state >= 0 and token in self.alphabet:
                state = self.transitions[state][self.alphabet.index(token)]
            else:
                state = -1
            steps.append({"token": token, "from": before, "to": state,
                          "output": self.outputs[state] if state >= 0 else None,
                          "revisit": state >= 0 and state in visited})
            visited.append(state)
        return steps

    def as_dict(self):
        return {"format": "kavi-finite-configuration-1", "alphabet": list(self.alphabet),
                "transitions": [list(row) for row in self.transitions],
                "outputs": list(self.outputs)}

    def encoded(self):
        return json.dumps(self.as_dict(), ensure_ascii=False,
                          separators=(",", ":")).encode("utf-8")

    @classmethod
    def decode(cls, raw):
        value = json.loads(raw)
        if value.get("format") != "kavi-finite-configuration-1":
            raise ValueError("Unknown configuration format")
        if set(value) != {"format", "alphabet", "transitions", "outputs"}:
            raise ValueError("Unexpected configuration fields")
        return cls(tuple(value["alphabet"]), tuple(tuple(row) for row in value["transitions"]),
                   tuple(value["outputs"]))


def prefix_configuration(examples, *, max_states=2000, check=None):
    """Build evidence without folding it. Contradictory labels are errors."""
    rows = [(tuple(tokens), label) for tokens, label in examples]
    if not rows:
        raise ValueError("At least one labeled sequence is required")
    alphabet = tuple(sorted({token for tokens, _ in rows for token in tokens}))
    columns = {symbol: i for i, symbol in enumerate(alphabet)}
    transitions = [[-1] * len(alphabet)]
    outputs = [None]
    for tokens, label in sorted(rows, key=lambda row: (len(row[0]), row[0])):
        if type(label) is not int:
            raise ValueError("Teaching labels must be integers")
        state = 0
        if check:
            check()
        for token in tokens:
            if check:
                check()
            column = columns[token]
            if transitions[state][column] == -1:
                if len(outputs) >= max_states:
                    raise RuntimeError("Prefix-state budget exhausted")
                transitions[state][column] = len(outputs)
                outputs.append(None)
                transitions.append([-1] * len(alphabet))
            state = transitions[state][column]
        if outputs[state] is not None and outputs[state] != label:
            raise ValueError("Contradictory teaching labels for one sequence")
        outputs[state] = label
    return Configuration(alphabet, tuple(tuple(row) for row in transitions), tuple(outputs))


def _merge(model, left, right, stats, check):
    """Close a proposed state identification under deterministic transitions."""
    size = len(model.outputs)
    parent = list(range(size))
    edges = [list(row) for row in model.transitions]
    outputs = list(model.outputs)
    stats["copied_transition_cells"] += size * len(model.alphabet)

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    pending = [(left, right)]
    while pending:
        if check:
            check()
        stats["closure_pairs"] += 1
        a, b = (find(node) for node in pending.pop())
        if a == b:
            continue
        if outputs[a] is not None and outputs[b] is not None and outputs[a] != outputs[b]:
            return None
        parent[b] = a
        if outputs[a] is None:
            outputs[a] = outputs[b]
        for column, child in enumerate(edges[b]):
            if child < 0:
                continue
            if edges[a][column] >= 0:
                pending.append((edges[a][column], child))
            else:
                edges[a][column] = child

    # Canonical numbering follows reachable connections from the entry state.
    entry = find(0)
    numbering = {entry: 0}
    queue = deque([entry])
    new_edges, new_outputs = [], []
    while queue:
        if check:
            check()
        node = queue.popleft()
        row = []
        for child in edges[node]:
            if child < 0:
                row.append(-1)
                continue
            child = find(child)
            if child not in numbering:
                numbering[child] = len(numbering)
                queue.append(child)
            row.append(numbering[child])
        new_edges.append(tuple(row))
        new_outputs.append(outputs[node])
    mapping = {node: numbering[find(node)] for node in range(size)}
    return Configuration(model.alphabet, tuple(new_edges), tuple(new_outputs)), mapping


def learn(examples, *, seed=7, max_states=2000, max_merges=20000, check=None):
    """First-compatible frontier merging; no target state graph is supplied."""
    started = time.perf_counter()
    model = prefix_configuration(examples, max_states=max_states, check=check)
    stats = {"prefix_states": len(model.outputs), "proposed_merges": 0,
             "accepted_merges": 0, "rejected_merges": 0, "closure_pairs": 0,
             "copied_transition_cells": 0, "seed": seed}
    rng = random.Random(seed)
    red = {0}
    while True:
        if check:
            check()
        blue = sorted({child for state in red for child in model.transitions[state]
                       if child >= 0 and child not in red})
        if not blue:
            break
        frontier = blue[0]
        candidates = sorted(red)
        rng.shuffle(candidates)
        for established in candidates:
            if stats["proposed_merges"] >= max_merges:
                raise RuntimeError("Merge-proposal budget exhausted")
            stats["proposed_merges"] += 1
            proposal = _merge(model, established, frontier, stats, check)
            if proposal is None:
                stats["rejected_merges"] += 1
                continue
            model, mapping = proposal
            red = {mapping[state] for state in red}
            stats["accepted_merges"] += 1
            break
        else:
            red.add(frontier)
    stats.update(states=len(model.outputs), transitions=sum(target >= 0 for row in
                 model.transitions for target in row), model_bytes=len(model.encoded()),
                 seconds=time.perf_counter() - started)
    return model, stats
