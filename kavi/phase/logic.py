"""Supplied formula composition using only learned phase-circuit truth values.

Syntax, variable binding and postorder scheduling are installed mechanisms.
No connective's truth function is implemented here.
"""

ARITIES = {'not': 1, 'and': 2, 'or': 2, 'implies': 2, 'iff': 2}


def gate_events(operator, operands):
    if operator not in ARITIES or len(operands) != ARITIES[operator]:
        raise ValueError('Invalid connective or arity')
    if any(type(v) is not int or v not in (0, 1) for v in operands):
        raise ValueError('Truth inputs must be integer zero or one')
    values = tuple('true' if v else 'false' for v in operands)
    return (operator, values[0]) if len(values) == 1 else (values[0], operator, values[1])


def evaluate_formula(circuit, expression, assignments, work, *, max_nodes=4096):
    """Evaluate a tuple syntax tree with finite workspace and shared work limits.

    Variables are strings; compound nodes are (operator, child, ...).
    Missing assignments or unresolved subexpressions return None. Malformed syntax
    raises ValueError. No source text, truth table or prior answer is consulted.
    """
    if type(max_nodes) is not int or not 1 <= max_nodes <= 100_000:
        raise ValueError('Invalid expression limit')
    pending, plan = [(expression, False)], []
    visited = 0
    while pending:
        node, ready = pending.pop()
        work.add('logic_syntax_visits')
        if ready:
            plan.append(('gate', node[0]))
            continue
        visited += 1
        if visited > max_nodes:
            raise InterruptedError('Expression node budget exhausted')
        if type(node) is str and node:
            plan.append(('variable', node))
        elif (type(node) is tuple and node and type(node[0]) is str
              and node[0] in ARITIES and len(node) == ARITIES[node[0]]+1):
            pending.append((node, True))
            pending.extend((child, False) for child in reversed(node[1:]))
        else:
            raise ValueError('Malformed expression')
    values = []
    for kind, value in plan:
        work.add('logic_execution_steps')
        if kind == 'variable':
            if value not in assignments:
                return None
            v = assignments[value]
            if type(v) is not int or v not in (0, 1):
                raise ValueError('Variable truth value must be integer zero or one')
            values.append(v)
        else:
            size = ARITIES[value]
            operands = tuple(values[-size:])
            del values[-size:]
            work.add('logic_gate_calls')
            result = circuit.predict(gate_events(value, operands), work)
            if result is None:
                return None
            if type(result) is not int or result not in (0, 1):
                raise ValueError('Circuit returned a non-Boolean output port')
            values.append(result)
    return values[0]
