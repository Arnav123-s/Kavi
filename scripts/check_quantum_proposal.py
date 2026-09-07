"""Reproduce small classical algebra checks for the quantum research proposal.

No learning, quantum hardware, external packages, or model artifacts are used.
Run: python scripts/check_quantum_proposal.py --output <results.json>
"""
import argparse
import cmath
import json
import math
from pathlib import Path


def mv(a, x):
    return [sum(v * w for v, w in zip(row, x)) for row in a]


def norm2(x):
    return sum(abs(v) ** 2 for v in x)


def check():
    h = [[1 / math.sqrt(2), 1 / math.sqrt(2)],
         [1 / math.sqrt(2), -1 / math.sqrt(2)]]
    checks = {}
    probs = []
    for phi in (0, math.pi / 2, math.pi):
        state = mv(h, [1, 0])
        state[1] *= cmath.exp(1j * phi)
        probability = abs(mv(h, state)[0]) ** 2
        assert math.isclose(probability, math.cos(phi / 2) ** 2, abs_tol=1e-12)
        probs.append(probability)
    checks['interference'] = {'p_zero': probs, 'passed': True}
    pure = abs(mv(h, [1 / math.sqrt(2)] * 2)[0]) ** 2
    mixed = sum(0.5 * abs(mv(h, basis)[0]) ** 2 for basis in ([1, 0], [0, 1]))
    assert math.isclose(pure, 1, abs_tol=1e-12) and math.isclose(mixed, 0.5)
    checks['coherence_vs_mixture'] = {'pure_p_zero': pure, 'mixed_p_zero': mixed, 'passed': True}
    state = [0.5] * 4
    state[3] *= -1
    before = abs(state[3]) ** 2
    mean = sum(state) / 4
    state = [2 * mean - a for a in state]
    assert before == 0.25 and state == [0, 0, 0, 1]
    checks['four_candidate_grover'] = {'marked_probability_before_diffusion': before,
                                     'after_diffusion': abs(state[3]) ** 2, 'passed': True}
    directed = mv([[1, -1j], [0, 1]], [0, 1])
    assert norm2(directed) == 2
    checks['directed_nonunitary'] = {'output_norm_squared': norm2(directed), 'passed': True}
    dt = 0.1
    a = dt / 2
    cayley = [[(1 - a*a) / (1 + a*a), -2j*a / (1 + a*a)],
              [-2j*a / (1 + a*a), (1 - a*a) / (1 + a*a)]]
    euler = [[1, -1j*dt], [-1j*dt, 1]]
    x, y = [1, 0], [1, 0]
    for _ in range(100):
        x, y = mv(cayley, x), mv(euler, y)
    assert math.isclose(norm2(x), 1, abs_tol=1e-12)
    assert math.isclose(norm2(y), (1 + dt*dt)**100, rel_tol=1e-12)
    checks['cayley_vs_euler'] = {'steps': 100, 'dt': dt, 'cayley_norm_squared': norm2(x),
                                'euler_norm_squared': norm2(y), 'passed': True}
    gamma = 0.3
    k0 = [[1, 0], [0, math.sqrt(1-gamma)]]
    k1 = [[0, math.sqrt(gamma)], [0, 0]]
    completeness = [[sum(sum(k[r][i].conjugate()*k[r][j] for r in range(2))
                        for k in (k0, k1)) for j in range(2)] for i in range(2)]
    assert all(abs(completeness[i][j] - (i == j)) < 1e-12 for i in range(2) for j in range(2))
    branches = [mv(k, [0, 1]) for k in (k0, k1)]
    rho = [[sum(v[i]*v[j].conjugate() for v in branches) for j in range(2)] for i in range(2)]
    assert abs(rho[0][0] - gamma) < 1e-12 and abs(rho[1][1] - (1-gamma)) < 1e-12
    checks['amplitude_damping'] = {'diagonal': [rho[0][0], rho[1][1]], 'passed': True}
    assert all(x == x*x for x in (0, 1)) and 2 != 2*2
    checks['finite_signature_collision'] = {'shared_inputs': [0, 1], 'counterexample': 2, 'passed': True}
    pairs = [(a, b) for a in range(8) for b in range(8)]
    unordered = {(min(a, b), max(a, b)) for a, b in pairs}
    reversible = {(min(a, b), max(a, b), a > b) for a, b in pairs}
    assert len(unordered) == 36 and len(reversible) == len(pairs) == 64
    checks['sorting_orientation'] = {'inputs': 64, 'sorted_only': 36, 'with_orientation': 64, 'passed': True}
    shots = math.ceil(math.log(2 / 0.05) / (2 * 0.01**2))
    assert shots == 18445
    checks['bernoulli_shot_bound'] = {'epsilon': 0.01, 'delta': 0.05, 'shots': shots, 'passed': True}
    return {'kind': 'classical_algebra_sanity_checks', 'quantum_hardware_used': False,
            'learning_performed': False, 'check_groups': len(checks), 'checks': checks}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(check(), indent=2) + '\n'
    if args.output:
        args.output.write_text(result, encoding='utf-8')
    print(result, end='')
