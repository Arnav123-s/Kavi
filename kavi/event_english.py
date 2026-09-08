"""Words directly change learned recurrent state coupled to quantity activity."""

import math
import re
import unicodedata

from .composable_configurations import Configuration
from .english_configurations import NUMBER_WORDS, OPS, WORD, stem
from .event_learning import EventConfiguration
from .signal_configurations import SignalExecution, SignalGraph


def events(text, vocabulary):
    if not isinstance(text, str) or len(text) > 4000:
        raise ValueError('Input exceeds the event-language character bound')
    quantities = 0
    tokens = 0
    for match in WORD.finditer(unicodedata.normalize('NFKC', text).replace('’', "'")):
        tokens += 1
        if tokens > 220:
            raise ValueError('Input exceeds the event-language token bound')
        raw = match[0]
        value = None
        if re.fullmatch(r'\d+(?:,\d{3})*(?:\.\d+)?', raw):
            value = float(raw.replace(',', ''))
        elif raw.casefold() in NUMBER_WORDS:
            value = float(NUMBER_WORDS[raw.casefold()])
        if value is not None:
            if not math.isfinite(value) or abs(value) > 1e12 or quantities >= 2:
                raise ValueError('This course requires two bounded explicit quantities')
            token = '<quantity'+str(quantities)+'>'
            quantities += 1
        else:
            token = stem(raw)
            if token.isalpha() and token not in vocabulary:
                token = '<other>'
        yield token, value
    if quantities != 2:
        raise ValueError('This course requires exactly two explicit quantities')
    yield '<end>', None


class EventEnglish:
    def __init__(self, graph, vocabulary):
        self.graph = graph
        self.vocabulary = frozenset(vocabulary)

    def execution(self, registry, work, observe=None):
        def invoke(name, args, work):
            work.add('event_component_calls')
            if name == 'quantities':
                (_, value), held = args
                return held+(value,) if value is not None else held
            if name == 'interpretation':
                (token, _), state = args
                work.add('event_transition_reads')
                return self.graph.transitions[state].get(token, -1) if state >= 0 else -1
            (token, _), quantities, state = args
            if token != '<end>' or state < 0 or len(quantities) != 2:
                return None
            port = self.graph.outputs[state]
            if port is None:
                return None
            relation = OPS[port]
            kernel = {'+':'science_sum', '-':'science_difference', '*':'science_work', '/':'science_ratio'}[relation.removeprefix('r')]
            # These are older acquired arithmetic configurations. Language
            # chooses their relation and orientation through learned states.
            a, b = quantities[::-1] if relation.startswith('r') else quantities
            return registry.execute(kernel, (a, b), work)
        graph = SignalGraph(1,
            (('quantities', (0, 1)), ('interpretation', (0, 2)), ('readout', (0, 1, 2))),
            3, seeds=((1, ()), (2, 0)), trigger_refs=((0,), (0,), None))
        return SignalExecution(graph, invoke, work, observe)

    def answer(self, text, registry, work, observe=None):
        execution = self.execution(registry, work)
        consumed = 0
        for event in events(text, self.vocabulary):
            status = execution.accept(0, event)
            consumed += 1
            if status['output_available']:
                raise ValueError('An answer escaped before input completion')
            if observe:
                observe({'event':event[0], 'current_state':execution.values[2],
                    'held_quantities':len(execution.values[1]), 'released':False})
        execution.finish_input()
        status = execution.settle()
        if not status['output_available']:
            return {'value':None, 'state':'unresolved', 'events':consumed,
                'live_values':len(execution.values), 'token_history_retained':False}
        return {'value':status['output'], 'state':'answered', 'events':consumed,
            'live_values':len(execution.values), 'token_history_retained':False}

    def record(self):
        return {'format':'kavi-event-english-1', 'vocabulary':sorted(self.vocabulary),
            'encoding':'frequent-words-and-two-quantity-ports-1', 'graph':self.graph.record()}

    @classmethod
    def from_record(cls, record):
        if record.get('format') != 'kavi-event-english-1':
            raise ValueError('Unknown event-language configuration')
        return cls(EventConfiguration(**record['graph']), record['vocabulary'])
