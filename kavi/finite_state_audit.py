"""Independent exhaustive comparison of deterministic finite configurations."""

from collections import deque


def compare(left, right, alphabet, *, check=None):
    """Check all reachable state pairs, returning a shortest failing sequence.

    Undefined transitions or outputs fail the completeness obligation even if
    both machines are undefined. Only a complete comparison certifies equality.
    """
    alphabet = tuple(alphabet)
    queue = deque([((0, 0), ())])
    seen = {(0, 0)}
    columns_left = {s: i for i, s in enumerate(left.alphabet)}
    columns_right = {s: i for i, s in enumerate(right.alphabet)}
    while queue:
        if check:
            check()
        (a, b), witness = queue.popleft()
        y_a = left.outputs[a] if a >= 0 else None
        y_b = right.outputs[b] if b >= 0 else None
        if y_a is None or y_b is None or y_a != y_b:
            return {"equivalent": False, "visited_pairs": len(seen),
                    "witness": list(witness), "left": y_a, "right": y_b,
                    "reason": "unresolved" if y_a is None or y_b is None else "different outputs"}
        for symbol in alphabet:
            col_a, col_b = columns_left.get(symbol), columns_right.get(symbol)
            next_a = left.transitions[a][col_a] if col_a is not None else -1
            next_b = right.transitions[b][col_b] if col_b is not None else -1
            pair = (next_a, next_b)
            if pair not in seen:
                seen.add(pair)
                queue.append((pair, witness + (symbol,)))
    return {"equivalent": True, "visited_pairs": len(seen), "witness": None}
