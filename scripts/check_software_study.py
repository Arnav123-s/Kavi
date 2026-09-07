"""Read-only certificate audit and small software-method examples.

These checks do not train or alter Kavi, adopt search recommendations, or
benchmark a quantum simulator. Run from the repository root with Python.
"""
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kavi.circuit_core import Circuit, MAX_INPUT_BITS
from kavi.circuit_runtime import local_invariant
from kavi.procedure_optimizations import addition_certificate


def online_weighted_mean(scores, values):
    """One scalar softmax-weighted result, without storing all probabilities."""
    maximum, denominator, numerator = -math.inf, 0.0, 0.0
    for score, value in zip(scores, values, strict=True):
        following = max(maximum, score)
        old_scale = math.exp(maximum - following)
        new_scale = math.exp(score - following)
        denominator = old_scale * denominator + new_scale
        numerator = old_scale * numerator + new_scale * value
        maximum = following
    if denominator == 0:
        raise ValueError("At least one finite score is required.")
    return numerator / denominator


def audit():
    circuit = Circuit.load(ROOT / 'experiments/circuit-20260905-model.json')
    certificate = local_invariant(circuit)
    rows = addition_certificate(circuit)
    assert certificate['valid_rows'] == 8 and len(rows) == 8
    for a, b, carry, emit, following in rows:
        assert circuit.step(a, b, carry) == (emit, following)
    mask = 255
    packed = [sum(row[i] << j for j, row in enumerate(rows)) for i in range(3)] + [0, mask]
    for gate in circuit.gates:
        values = [packed[i] for i in gate.inputs]
        packed.append(values[0] ^ values[1] if gate.op == 'XOR' else
                      values[0] & values[1] if gate.op == 'AND' else (~values[0]) & mask)
    for j, row in enumerate(rows):
        assert ((packed[circuit.emit] >> j) & 1, (packed[circuit.next_state] >> j) & 1) == tuple(row[3:])
    largest = (1 << MAX_INPUT_BITS) - 1
    assert circuit.execute(largest, 1).value == (1 << MAX_INPUT_BITS)
    rejected = False
    try:
        circuit.execute(1 << MAX_INPUT_BITS, 0)
    except ValueError:
        rejected = True
    assert rejected
    bad = Circuit(circuit.gates, circuit.next_state, circuit.emit)
    assert local_invariant(bad)['valid_rows'] < 8
    assert circuit.step(1, 1, 0)[0] == 0  # Missing flush would lose the carry.
    scores, values = [1000.0, 1001.0, 999.0, 1003.0], [2.0, -1.0, 4.0, 7.0]
    weights = [math.exp(x - max(scores)) for x in scores]
    reference = sum(w*v for w, v in zip(weights, values)) / sum(weights)
    observed = online_weighted_mean(scores, values)
    assert math.isclose(reference, observed, rel_tol=1e-14, abs_tol=1e-14)
    return {'kind': 'read_only_certificate_and_software_examples',
            'source_revision': '288e9ec', 'training_performed': False,
            'search_recommendations_adopted': False, 'quantum_hardware_used': False,
            'model_sha256': circuit.digest, 'canonical_model_bytes': len(circuit.encoded()),
            'runtime_input_bit_limit': MAX_INPUT_BITS, 'local_certificate': certificate,
            'compiler_certificate_agrees': True, 'packed_eight_rows_agree': True,
            'boundary_input_passed': True, 'over_limit_input_rejected': rejected,
            'swapped_outputs_negative_control_valid_rows': local_invariant(bad)['valid_rows'],
            'online_softmax_mean': {'reference': reference, 'observed': observed,
                                    'absolute_error': abs(reference-observed)},
            'scope': 'Finite checks support the documented proof assumptions; no proof-assistant verification or speed benchmark.'}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2))
