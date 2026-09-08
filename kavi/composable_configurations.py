"""Finite hierarchical configurations, local completion and guarded expansion."""

from dataclasses import dataclass, field
import hashlib
import itertools
import json
import math


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('utf-8')


class Unresolved(ValueError):
    pass


class StaleConfiguration(ValueError):
    pass


@dataclass(frozen=True)
class Configuration:
    arity: int
    calls: tuple = ()
    output: int = 0
    kernel: str | None = None

    def __post_init__(self):
        if type(self.arity) is not int or not 0 <= self.arity <= 8:
            raise ValueError('Invalid interface arity')
        if self.kernel is not None:
            if not isinstance(self.kernel, str) or self.calls or self.output != 0:
                raise ValueError('A kernel configuration has no internal calls')
            return
        if len(self.calls) > 128:
            raise ValueError('Configuration exceeds the call limit')
        for i, (name, refs) in enumerate(self.calls):
            if not isinstance(name, str) or any(type(r) is not int or not 0 <= r < self.arity+i for r in refs):
                raise ValueError('Connections must reference inputs or earlier outputs')
        if type(self.output) is not int or not 0 <= self.output < self.arity + len(self.calls):
            raise ValueError('Invalid output connection')

    def record(self):
        return {'arity': self.arity, 'calls': self.calls, 'output': self.output, 'kernel': self.kernel}

    @classmethod
    def decode(cls, value):
        if set(value) != {'arity', 'calls', 'output', 'kernel'}:
            raise ValueError('Invalid configuration record')
        return cls(value['arity'], tuple((n, tuple(r)) for n, r in value['calls']),
                   value['output'], value['kernel'])


@dataclass
class Work:
    counts: dict = field(default_factory=dict)
    check: object = lambda: None
    limit: int = 5_000_000

    def add(self, key, amount=1):
        self.check()
        self.counts[key] = self.counts.get(key, 0) + amount
        if sum(self.counts.values()) > self.limit:
            raise InterruptedError('Configuration work budget exhausted')


@dataclass(frozen=True)
class Expansion:
    arity: int
    calls: tuple
    output: int
    dependencies: tuple
    substrate: str

    def record(self):
        return {'arity': self.arity, 'calls': self.calls, 'output': self.output,
                'dependencies': self.dependencies, 'substrate': self.substrate}

    def execute(self, args, registry, work, *, verify=True):
        if len(args) != self.arity:
            raise ValueError('Input interface mismatch')
        if verify:
            work.add('guard_dependencies', len(self.dependencies))
            if self.substrate != registry.substrate:
                raise StaleConfiguration('The supplied substrate changed')
            for name, digest in self.dependencies:
                current = registry.definitions.get(name)
                if current is None:
                    raise StaleConfiguration('A required configuration disappeared')
                raw = encoded(current.record())
                work.add('guard_bytes', len(raw))
                if hashlib.sha256(raw).hexdigest() != digest:
                    raise StaleConfiguration('A dependency changed; expand again')
        values = list(args)
        for kernel, refs in self.calls:
            values.append(registry.invoke(kernel, tuple(values[r] for r in refs), work))
        return values[self.output]


class Registry:
    """Definitions share structure, while each invocation owns its temporary values."""

    def __init__(self, kernels, substrate, definitions=None, costs=None):
        self.kernels = kernels
        self.substrate = substrate
        self.definitions = dict(definitions or {})
        self.costs = costs or {}

    def copy(self):
        return Registry(self.kernels, self.substrate, self.definitions, self.costs)

    def install(self, name, config):
        self.definitions[name] = config

    def invoke(self, name, args, work):
        if name not in self.kernels:
            raise Unresolved('Unknown kernel: ' + name)
        work.add('kernel_calls')
        work.add('kernel_work_units', self.costs.get(name, 1))
        work.add('kernel_' + name)
        return self.kernels[name](args, work)

    def execute(self, name, args, work, depth=0):
        work.add('configuration_entries')
        if depth > 32:
            raise ValueError('Hierarchical depth limit exceeded')
        config = self.definitions.get(name)
        if config is None:
            raise Unresolved('Unknown configuration: ' + name)
        if len(args) != config.arity:
            raise ValueError('Input interface mismatch')
        if config.kernel is not None:
            return self.invoke(config.kernel, args, work)
        values = list(args)
        for callee, refs in config.calls:
            values.append(self.execute(callee, tuple(values[r] for r in refs), work, depth+1))
        return values[config.output]

    def expand(self, name, work):
        calls, dependencies = [], {}

        def visit(callee, refs, stack):
            work.add('expansion_visits')
            if callee in stack or len(stack) > 32 or len(calls) > 2048:
                raise ValueError('Cyclic or excessive expansion')
            config = self.definitions.get(callee)
            if config is None:
                raise Unresolved('Unknown configuration: ' + callee)
            if len(refs) != config.arity:
                raise ValueError('Input interface mismatch')
            raw = encoded(config.record())
            work.add('expansion_hash_bytes', len(raw))
            dependencies[callee] = hashlib.sha256(raw).hexdigest()
            if config.kernel is not None:
                calls.append((config.kernel, tuple(refs)))
                return arity + len(calls)-1
            values = list(refs)
            for target, local_refs in config.calls:
                values.append(visit(target, tuple(values[r] for r in local_refs), stack+(callee,)))
            return values[config.output]

        if name not in self.definitions:
            raise Unresolved('Unknown configuration: ' + name)
        arity = self.definitions[name].arity
        output = visit(name, tuple(range(arity)), ())
        return Expansion(arity, tuple(calls), output, tuple(sorted(dependencies.items())), self.substrate)

    def record(self):
        return {'format': 'kavi-hierarchical-configurations-1', 'substrate': self.substrate,
                'definitions': {name: c.record() for name, c in sorted(self.definitions.items())}}


def candidates(registry, operations, arity=2):
    """All zero-, one- and two-call graphs in the declared grammar."""
    for ref in range(arity):
        yield Configuration(arity, output=ref)
    first = [(op, refs) for op in operations for refs in itertools.product(
             range(arity), repeat=registry.definitions[op].arity)]
    for call in first:
        yield Configuration(arity, (call,), arity)
    for call in first:
        for op in operations:
            for refs in itertools.product(range(arity+1), repeat=registry.definitions[op].arity):
                yield Configuration(arity, (call, (op, refs)), arity+1)


def agrees(a, b):
    if isinstance(a, (tuple, list)) or isinstance(b, (tuple, list)):
        return isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)) and len(a) == len(b) and all(
            agrees(x, y) for x, y in zip(a, b))
    if type(a) is int and type(b) is int:
        return a == b
    if not isinstance(a, (int, float, complex)) or not isinstance(b, (int, float, complex)):
        return False
    return math.isfinite(abs(a)) and math.isfinite(abs(b)) and abs(a-b) <= 1e-10 * max(1, abs(a), abs(b))


def fit(registry, name, lessons, operations, work, *, outer=None, local=False, arity=2):
    """Learn a missing subconfiguration from final-output supervision.

    The outer graph supplies one missing call's boundary. In local mode, known
    prefix values are reused only within this teaching transaction.
    """
    lessons = list(lessons)
    if not lessons:
        raise ValueError('Teaching examples are required')
    trial = registry.copy()
    frames = []
    outer_config = registry.definitions[outer] if outer else None
    if outer:
        locations = [i for i, (callee, _) in enumerate(outer_config.calls) if callee == name]
        if len(locations) != 1:
            raise ValueError('This local learner requires exactly one explicit missing call')
        boundary = locations[0]
    if outer and local:
        for args, expected in lessons:
            values = list(args)
            for callee, refs in outer_config.calls[:boundary]:
                values.append(registry.execute(callee, tuple(values[r] for r in refs), work))
            frames.append((tuple(values), expected))
        work.add('prepared_prefixes', len(frames))
    consistent = []
    for proposal in candidates(registry, operations, arity):
        work.add('candidate_proposals')
        trial.install(name, proposal)
        valid = True
        for index, (args, expected) in enumerate(lessons):
            work.add('candidate_examples')
            try:
                if outer and local:
                    values = list(frames[index][0])
                    for callee, refs in outer_config.calls[boundary:]:
                        values.append(trial.execute(callee, tuple(values[r] for r in refs), work))
                    observed = values[outer_config.output]
                else:
                    observed = trial.execute(outer or name, args, work)
                if not agrees(observed, expected):
                    valid = False
                    break
            except (ValueError, TypeError, OverflowError, ZeroDivisionError):
                work.add('invalid_candidates')
                valid = False
                break
        if valid:
            consistent.append(proposal)
    work.add('consistent_candidates', len(consistent))
    def rank(config):
        cost = sum(registry.costs.get(registry.definitions[n].kernel or n, 1) for n, _ in config.calls)
        return cost, len(config.calls), encoded(config.record())
    return min(consistent, key=rank, default=None)


def differentiate(registry, name, variable, work):
    """Supplied exact chain/product-rule transformation over arithmetic graphs."""
    plan = registry.expand(name, work)
    if not 0 <= variable < plan.arity:
        raise ValueError('Invalid differentiation variable')
    calls, shared = [], {}

    def emit(op, refs):
        key = (op, tuple(refs))
        if key not in shared:
            calls.append(key)
            shared[key] = plan.arity + len(calls)-1
        return shared[key]

    zero, one = emit('zero', ()), emit('one', ())
    values = list(range(plan.arity))
    derivs = [one if i == variable else zero for i in range(plan.arity)]
    for kernel, refs in plan.calls:
        work.add('differentiation_steps')
        if kernel not in ('add', 'subtract', 'multiply'):
            raise ValueError('Only polynomial arithmetic can be differentiated here')
        a, b = refs
        values.append(emit(kernel, (values[a], values[b])))
        if kernel in ('add', 'subtract'):
            derivs.append(emit(kernel, (derivs[a], derivs[b])))
        else:
            left = emit('multiply', (derivs[a], values[b]))
            right = emit('multiply', (values[a], derivs[b]))
            derivs.append(emit('add', (left, right)))
    return Configuration(plan.arity, tuple(calls), derivs[plan.output])
