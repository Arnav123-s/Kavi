"""Original question and option text drive one shared acquired event graph."""

import re
import unicodedata
from itertools import chain

from .english_configurations import stem
from .event_learning import EventConfiguration
from .event_transfer import ENTRY
from .adaptive_events import AdaptiveActivity

WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?|\d+(?:\.\d+)?|[^\w\s]", re.UNICODE)
REJECT, SUPPORT = 6, 7


def words(text):
    if not isinstance(text, str) or len(text) > 12000:
        raise ValueError('Text exceeds the course character bound')
    tokens = [stem(token) for token in WORD.findall(unicodedata.normalize('NFKC', text))]
    if len(tokens) > 600:
        raise ValueError('Text exceeds the course token bound')
    return tokens


def events(question, option, vocabulary):
    # Boundaries describe the supplied exercise interface, not a subject label
    # or inferred intent. All subjects use the same input entry and graph.
    for index, text in enumerate((question, option)):
        for token in words(text):
            yield token if token in vocabulary else '<other>'
        yield '<option>' if index == 0 else '<choice-end>'


class TextChoice:
    def __init__(self, graph, vocabulary, embedding):
        self.graph = graph
        self.vocabulary = frozenset(vocabulary)
        self.embedding = tuple(embedding)

    def answer(self, question, options, work, *, adaptive=False):
        if len(options) != 4 or any(not isinstance(option, str) or not option for option in options):
            raise ValueError('Four original nonempty options are required')
        labels, old_visits, steps = [], 0, 0
        maximum_candidates, proposed_links = 1, 0
        old = set(self.embedding)
        for option in options:
            state = 0
            activity = AdaptiveActivity(self.graph, work, beam=16, maximum_links=4) if adaptive else None
            for token in chain((ENTRY,), events(question, option, self.vocabulary)):
                work.add('choice_event_steps')
                steps += 1
                state = self.graph.transitions[state].get(token, -1) if state >= 0 else -1
                old_visits += state in old
                if activity is not None:
                    activity.feed(token)
            if activity is None:
                labels.append(self.graph.outputs[state] if state >= 0 else None)
            else:
                activity.close()
                proposals = [(candidate, label) for candidate, label in activity.proposals() if label in (REJECT, SUPPORT)]
                labels.append(proposals[0][1] if proposals else None)
                proposed_links += len(proposals[0][0].links) if proposals else 0
                maximum_candidates = max(maximum_candidates, activity.maximum_active)
        supported = [i for i, label in enumerate(labels) if label == SUPPORT]
        # An incomplete route is not a rejection. Release only after every
        # option finishes and exactly one is supported, with all others rejected.
        answer = supported[0] if len(supported) == 1 and all(label in (REJECT, SUPPORT) for label in labels) else None
        return {'answer': answer, 'state': 'answered' if answer is not None else 'unresolved',
                'option_ports': labels, 'old_state_visits': old_visits, 'events': steps,
                'candidate_states_at_once': 1, 'option_results_retained': 4,
                'adaptive': adaptive, 'maximum_candidates': maximum_candidates,
                'selected_provisional_links': proposed_links,
                'token_history_retained': False}

    def record(self):
        return {'format': 'kavi-text-choice-1', 'graph': self.graph.record(),
                'vocabulary': sorted(self.vocabulary), 'embedding': list(self.embedding),
                'encoding': 'original-question-option-events-1'}

    @classmethod
    def from_record(cls, record):
        if record['format'] != 'kavi-text-choice-1':
            raise ValueError('Unknown text-choice configuration')
        return cls(EventConfiguration(**record['graph']), record['vocabulary'], record['embedding'])
