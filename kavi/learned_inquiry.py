"""Learn which arithmetic relationship to ask a teacher to clarify.

The question decision is an acquired predicate graph. Question wording, the
relation interface and constrained composition are supplied. Teacher replies
are temporary input; neither replies nor past questions enter the artifact.
"""

import itertools
import json
import math
from pathlib import Path
import unicodedata

from .english_configurations import (
    ConnectionTree, OPS, WORD, compose, configuration, render,
)
from .published_english import PredicateTree
from .signal_configurations import SignalExecution, SignalGraph
from .streaming_english import InputActivity


def relations(program):
    result = {}
    def visit(node):
        if type(node) is int:
            return [node]
        symbol, left, right = node
        a, b = visit(left), visit(right)
        for i in a:
            for j in b:
                result[tuple(sorted((i, j)))] = (
                    'r'+symbol if i > j and symbol in ('-', '/') else symbol)
        return a+b
    visit(program)
    return result


def decision_features(input_features, pair, program, alternative, preferences):
    result = set(input_features)
    result.add('proposed_relation='+relations(program)[pair])
    result.add('preferred_relation='+max(preferences, key=preferences.get))
    if alternative is not None:
        other = relations(alternative)[pair]
        result.add('alternative_relation='+other)
        if other != relations(program)[pair]:
            result.add('alternative_changes_relation')
    return frozenset(result)


class ConstrainedRoutes:
    def __init__(self, router, replies):
        self.router, self.replies = router, replies

    def activate(self, features, work):
        preferences, trace = self.router.activate(features, work)
        for (i, j), relation in self.replies.items():
            if 'pair='+str(i)+','+str(j) in features:
                # An explicit teacher reply is an input constraint. This
                # ranking helps bounded search find a complying candidate;
                # Turn._compose also rejects every noncomplying result.
                work.add('teacher_relation_constraints')
                preferences = {op:1.0 if op == relation else math.exp(-100) for op in OPS}
        return preferences, trace


class Turn:
    def __init__(self, model, text, work):
        if not isinstance(text, str) or len(text) > 4000:
            raise ValueError('Question exceeds 4,000 characters')
        self.model = model
        vocabulary = {node['feature'] for node in model.language.nodes if 'feature' in node}
        vocabulary.update(node['feature'] for node in model.policy.nodes if 'feature' in node)
        self.activity = InputActivity(vocabulary, work)
        for match in WORD.finditer(unicodedata.normalize('NFKC', text).replace('’', "'")):
            self.activity.consume(match[0])
        self.activity.close()
        self.replies = {}
        self.pending = None
        self.asked = 0
        self._compose(work)

    def _compose(self, work):
        def read(state, i, j):
            return state.features(i, j) | {'pair='+str(i)+','+str(j)}
        candidates, active = compose(self.activity,
            ConstrainedRoutes(self.model.language, self.replies), work, feature_reader=read)
        valid = []
        for candidate in candidates:
            labels = relations(candidate.program)
            work.add('constraint_candidate_checks')
            if all(labels[pair] == reply for pair, reply in self.replies.items()):
                valid.append(candidate)
        if not valid:
            raise ValueError('No complying calculation within the current search budget')
        self.best = valid[0]
        self.alternative = next((candidate for candidate in valid[1:]
            if not math.isclose(candidate.value, self.best.value, rel_tol=1e-9, abs_tol=1e-10)), None)
        self.preferences = {tuple(item['quantities']):item['operation_preference'] for item in active}

    def features(self, pair):
        return decision_features(self.activity.features(*pair), pair, self.best.program,
            self.alternative.program if self.alternative else None, self.preferences[pair])

    def ask(self, work):
        if self.pending is not None:
            return self.pending
        if self.asked >= 1:
            return None
        for pair in itertools.combinations(range(len(self.activity.numbers)), 2):
            ports, _ = self.model.policy.activate(self.features(pair), work)
            if ports[0] == 'ask':
                return self.request(pair)
        return None

    def request(self, pair):
        """Open a relation question; also used by the always-ask control."""
        if self.pending is not None or self.asked >= 1:
            raise ValueError('The one-question allowance has already been used')
        pair = tuple(pair)
        if pair not in self.preferences:
            raise ValueError('This quantity relationship does not exist')
        i, j = pair
        a, b = (format(self.activity.numbers[k], '.10g') for k in pair)
        self.pending = {
            'pair':list(pair), 'options':list(OPS),
            'current_relation':relations(self.best.program)[pair],
            'text':f'Which operation joins the parts containing quantity {i+1} ({a}) '
                   f'and quantity {j+1} ({b}) in the worked calculation?',
            'wording':'supplied relation-question template',
        }
        return self.pending

    def clarify(self, relation, work):
        if self.pending is None:
            raise ValueError('There is no pending question')
        if relation not in self.pending['options']:
            raise ValueError('Teacher reply is outside the relation interface')
        pair = tuple(self.pending['pair'])
        self.replies[pair] = relation
        self.pending = None
        self.asked += 1
        self._compose(work)

    def answer(self, registry, work):
        if self.pending is not None:
            raise ValueError('An interpretation question is awaiting its reply')
        graph = configuration(self.best.program, len(self.activity.numbers))
        trial = registry.copy()
        trial.install('inquiry_calculation', graph)
        connected = SignalGraph.from_registry(trial, 'inquiry_calculation', work)
        execution = SignalExecution(connected, trial.invoke, work, registry=trial)
        for port, value in enumerate(self.activity.numbers):
            execution.feed(port, value)
        execution.finish_input()
        result = execution.settle()
        if not result['output_available']:
            raise ValueError('The clarified calculation did not complete')
        if not math.isclose(result['output'], self.best.value, rel_tol=1e-9, abs_tol=1e-10):
            raise ValueError('Proposed and executed calculations disagree')
        return {'value':result['output'], 'program':self.best.program,
            'expression':render(self.best.program, self.activity.numbers),
            'questions_asked':self.asked, 'input_activity':self.activity.state_counts()}


class InquiryModel:
    def __init__(self, language, policy=None):
        self.language = language
        self.policy = policy or PredicateTree(('answer', 'ask'), [{'ports':['answer']}])

    def begin(self, text, work):
        return Turn(self, text, work)

    def record(self):
        return {'format':'kavi-learned-inquiry-1', 'language':self.language.nodes,
            'policy':self.policy.nodes, 'question_limit':1,
            'feature_semantics':'english-connections-and-relation-contrasts-1'}

    @classmethod
    def load(cls, path):
        record = json.loads(Path(path).read_text(encoding='utf-8'))
        if record.get('format') != 'kavi-learned-inquiry-1' or record.get('question_limit') != 1:
            raise ValueError('Unknown inquiry configuration')
        return cls(ConnectionTree(record['language']),
            PredicateTree(('answer', 'ask'), record['policy']))
