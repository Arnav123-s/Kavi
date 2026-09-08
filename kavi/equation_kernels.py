"""Supplied equation kernels for finite configuration-learning experiments."""

import hashlib
import math

from .composable_configurations import Configuration, Registry
from .configuration_composition import COST_FIELDS


def scalar(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1e100:
        raise ValueError('A finite real scalar within the trial range is required')
    return value


def heat(args, work):
    state, interval = args
    t = scalar(interval)
    if not isinstance(state, tuple) or len(state) != 3 or t < 0:
        raise ValueError('Three temperatures and a nonnegative interval are required')
    state = tuple(scalar(v) for v in state)
    mean = math.fsum(state) / 3
    factor = math.exp(-3*t)
    return tuple(mean + factor * (v-mean) for v in state)


def schrodinger(args, work):
    state, interval = args
    t = scalar(interval)
    if not isinstance(state, tuple) or len(state) != 2:
        raise ValueError('A two-amplitude state is required')
    if any(not isinstance(v, (int, float, complex)) or not math.isfinite(abs(v)) for v in state):
        raise ValueError('Finite amplitudes are required')
    a, b = state
    c, s = math.cos(t), math.sin(t)
    return (c*a-1j*s*b, c*b-1j*s*a)


def probability(args, work):
    state, = args
    if not isinstance(state, tuple) or len(state) != 2 or not math.isclose(
            sum(abs(v)**2 for v in state), 1, abs_tol=1e-10):
        raise ValueError('A normalized two-amplitude state is required')
    return abs(state[1])**2


def make_registry(library):
    def acquired(name):
        def call(args, work):
            try:
                execution = library.execute(name, args, check=work.check)
            except Exception as error:
                execution = getattr(error, 'execution', None)
                if execution is not None:
                    for key in COST_FIELDS:
                        work.add('arithmetic_' + key, getattr(execution, key))
                raise
            for key in COST_FIELDS:
                work.add('arithmetic_' + key, getattr(execution, key))
            return execution.value
        return call
    kernels = {name: acquired(name) for name in ('add', 'subtract', 'multiply')}
    kernels.update(zero=lambda args, work: 0, one=lambda args, work: 1,
        real_add=lambda args, work: scalar(args[0]) + scalar(args[1]),
        real_subtract=lambda args, work: scalar(args[0]) - scalar(args[1]),
        real_multiply=lambda args, work: scalar(args[0]) * scalar(args[1]),
        real_divide=lambda args, work: scalar(args[0]) / scalar(args[1]),
        heat=heat, schrodinger=schrodinger, probability=probability)
    costs = {'heat': 12, 'schrodinger': 12}
    # This fingerprint binds supplied code and the acquired arithmetic dependency.
    from pathlib import Path
    source = Path(__file__).read_text(encoding='utf-8').encode('utf-8')
    substrate = hashlib.sha256(source + library.encoded()).hexdigest()
    registry = Registry(kernels, substrate, costs=costs)
    for name in kernels:
        arity = 0 if name in ('zero', 'one') else 1 if name == 'probability' else 2
        registry.install(name, Configuration(arity, kernel=name))
    registry.install('wire', Configuration(1, output=0))
    return registry
