"""Bounded composition of acquired procedures and feedback-selected connections."""

from dataclasses import dataclass
import itertools
import json
import re

from .procedure_core import Execution, Limits, ProcedureLibrary
from .recurrent_configuration import Configuration


COST_FIELDS = ('calls', 'frames', 'gates', 'iterations', 'connector_comparisons',
               'bit_tests', 'shifts')


def add_cost(target, execution):
    for key in COST_FIELDS:
        target[key] = target.get(key, 0) + getattr(execution, key, 0)


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':')).encode('utf-8')


@dataclass(frozen=True)
class ProgramGraph:
    """Two inputs followed by acyclic calls; each intermediate is computed once."""

    nodes: tuple[tuple[str, int, int], ...]
    output: int

    def __post_init__(self):
        if len(self.nodes) > 16:
            raise ValueError('At most sixteen call nodes are permitted')
        for index, node in enumerate(self.nodes):
            if (len(node) != 3 or not isinstance(node[0], str) or any(
                    type(ref) is not int or not 0 <= ref < index + 2 for ref in node[1:])):
                raise ValueError('A node may reference only inputs and earlier nodes')
        if type(self.output) is not int or not 0 <= self.output < len(self.nodes) + 2:
            raise ValueError('Invalid output reference')

    def as_dict(self):
        return {'nodes': [list(node) for node in self.nodes], 'output': self.output}

    @classmethod
    def decode(cls, value):
        if set(value) != {'nodes', 'output'}:
            raise ValueError('Invalid program graph fields')
        return cls(tuple(tuple(node) for node in value['nodes']), value['output'])

    def execute(self, args, library, *, limits=Limits(), check=lambda: None):
        result = Execution()
        try:
            if len(args) != 2:
                raise ValueError('Two inputs are required')
            values = list(args)
            for value in values:
                ProcedureLibrary._natural(value)
            for name, left, right in self.nodes:
                check()
                remaining = Limits(max_calls=limits.max_calls-result.calls,
                                   max_gates=limits.max_gates-result.gates,
                                   max_iterations=limits.max_iterations-result.iterations,
                                   max_depth=limits.max_depth,
                                   max_trace_entries=limits.max_trace_entries)
                try:
                    execution = library.execute(name, (values[left], values[right]),
                                                limits=remaining, check=check)
                except Exception as error:
                    partial = getattr(error, 'execution', Execution())
                    for key in COST_FIELDS:
                        setattr(result, key, getattr(result, key) + getattr(partial, key))
                    raise
                for key in COST_FIELDS:
                    setattr(result, key, getattr(result, key) + getattr(execution, key))
                values.append(execution.value)
            result.value = values[self.output]
            return result
        except Exception as error:
            error.execution = result
            raise


def candidate_graphs(operations=('add', 'subtract', 'multiply')):
    """The declared 338-member space, without behavioral deduplication."""
    yield ProgramGraph((), 0)
    yield ProgramGraph((), 1)
    first_nodes = list(itertools.product(operations, range(2), range(2)))
    for first in first_nodes:
        yield ProgramGraph((first,), 2)
    for first in first_nodes:
        for second in itertools.product(operations, range(3), range(3)):
            yield ProgramGraph((first, second), 3)


def fit_graph(examples, library, *, check=lambda: None):
    examples = list(examples)
    if not examples:
        raise ValueError('Numerical teaching examples are required')
    stats = {'candidates': 0, 'executions': 0, 'invalid_executions': 0,
             'consistent_candidates': 0}
    consistent = []
    for graph in candidate_graphs():
        check()
        stats['candidates'] += 1
        matches = True
        for args, expected in examples:
            stats['executions'] += 1
            try:
                execution = graph.execute(args, library, check=check)
                add_cost(stats, execution)
                matches = execution.value == expected
            except ValueError as error:
                add_cost(stats, getattr(error, 'execution', Execution()))
                stats['invalid_executions'] += 1
                matches = False
            if not matches:
                break
        if matches:
            consistent.append(graph)
    stats['consistent_candidates'] = len(consistent)
    selected = min(consistent, key=lambda g: (len(g.nodes), encoded(g.as_dict())), default=None)
    return selected, stats


@dataclass(frozen=True)
class GraphCatalog:
    base_digest: str
    entries: tuple[tuple[str, ProgramGraph], ...] = ()

    def __post_init__(self):
        if not re.fullmatch('[a-f0-9]{64}', self.base_digest):
            raise ValueError('Invalid base library digest')
        names = [name for name, _ in self.entries]
        if len(names) != len(set(names)) or len(names) > 32 or any(
                not re.fullmatch('[a-z][a-z0-9_]{0,39}', name) for name in names):
            raise ValueError('Invalid or duplicate catalog names')

    def _check_base(self, library):
        if library.digest != self.base_digest:
            raise ValueError('Base library changed; review the configuration again')
        if any(name in library.procedures for name, _ in self.entries):
            raise ValueError('A new name cannot replace an earlier procedure')

    def execute(self, name, args, library, *, check=lambda: None):
        self._check_base(library)
        if name in library.procedures:
            return library.execute(name, args, check=check)
        graph = dict(self.entries).get(name)
        if graph is None:
            raise ValueError('Unknown configuration')
        return graph.execute(args, library, check=check)

    def admit(self, name, graph, evidence, library, *, check=lambda: None):
        self._check_base(library)
        if name in library.procedures or name in dict(self.entries):
            raise ValueError('A new name cannot replace an earlier configuration')
        evidence = list(evidence)
        if not evidence:
            raise ValueError('Independent promotion evidence is required')
        stats = {'promotion_cases': 0}
        for args, expected in evidence:
            check()
            result = graph.execute(args, library, check=check)
            add_cost(stats, result)
            stats['promotion_cases'] += 1
            if result.value != expected:
                raise ValueError('Candidate failed promotion evidence')
        return GraphCatalog(self.base_digest, self.entries + ((name, graph),)), stats

    def encoded(self):
        return encoded({'format': 'kavi-composed-catalog-1', 'base_digest': self.base_digest,
                        'entries': {name: graph.as_dict() for name, graph in self.entries}})

    @classmethod
    def decode(cls, raw):
        value = json.loads(raw)
        if set(value) != {'format', 'base_digest', 'entries'} or value['format'] != 'kavi-composed-catalog-1':
            raise ValueError('Unknown catalog format')
        return cls(value['base_digest'], tuple((name, ProgramGraph.decode(graph))
                   for name, graph in sorted(value['entries'].items())))


@dataclass(frozen=True)
class ArithmeticBridge:
    controller: Configuration
    base_digest: str
    choices: tuple[tuple[int, tuple[str, ...]], ...]

    def answer(self, tokens, args, library, *, check=lambda: None):
        if library.digest != self.base_digest:
            raise ValueError('Base library changed; review the connections again')
        outcome = self.controller.predict(tokens, check=check)
        choices = dict(self.choices).get(outcome, ()) if outcome is not None else ()
        if len(choices) != 1:
            return {'state': 'ambiguous' if len(choices) > 1 else 'unresolved',
                    'alternatives': len(choices)}
        result = library.execute(choices[0], args, check=check)
        response = {'state': 'answered', 'value': result.value}
        add_cost(response, result)
        return response

    def encoded(self):
        return encoded({'format': 'kavi-arithmetic-bridge-1', 'controller': self.controller.as_dict(),
                        'base_digest': self.base_digest, 'choices': self.choices})

    @classmethod
    def decode(cls, raw):
        value = json.loads(raw)
        if set(value) != {'format', 'controller', 'base_digest', 'choices'} or value['format'] != 'kavi-arithmetic-bridge-1':
            raise ValueError('Unknown bridge format')
        choices = tuple((key, tuple(names)) for key, names in value['choices'])
        if any(type(key) is not int or any(not isinstance(n, str) for n in names)
               for key, names in choices) or len({key for key, _ in choices}) != len(choices):
            raise ValueError('Invalid bridge connections')
        return cls(Configuration.decode(json.dumps(value['controller'])), value['base_digest'], choices)


def fit_bridge(controller, examples, library, *, operations=('add', 'subtract', 'multiply'),
               check=lambda: None):
    choices, stats = {}, {'candidate_executions': 0, 'controller_token_steps': 0}
    for tokens, args, expected in examples:
        outcome = controller.predict(tokens, check=check)
        stats['controller_token_steps'] += len(tokens)
        if outcome is None:
            raise ValueError('The controller cannot resolve a teaching input')
        candidates = choices.get(outcome, list(operations))
        retained = []
        for name in candidates:
            stats['candidate_executions'] += 1
            try:
                result = library.execute(name, args, check=check)
                add_cost(stats, result)
                if result.value == expected:
                    retained.append(name)
            except ValueError as error:
                add_cost(stats, getattr(error, 'execution', Execution()))
        if not retained:
            raise ValueError('No supplied procedure satisfies the feedback')
        choices[outcome] = retained
    return ArithmeticBridge(controller, library.digest,
                            tuple((key, tuple(names)) for key, names in sorted(choices.items()))), stats
