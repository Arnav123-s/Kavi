"""Construct temporary event-graph extensions while input is arriving."""

from copy import deepcopy
from dataclasses import dataclass
import hashlib

from .composable_configurations import encoded
from .event_learning import EventConfiguration


@dataclass(frozen=True)
class Blueprint:
    state: int
    links: tuple = ()


class AdaptiveActivity:
    def __init__(self, graph, work, *, beam=16, maximum_links=4):
        self.graph = graph
        self.fingerprint = hashlib.sha256(encoded(graph.record())).hexdigest()
        self.beam, self.maximum_links = beam, maximum_links
        self.active = [Blueprint(0)]
        self.closed = False
        self.maximum_active = 1
        self.events = 0
        self.work = work

    def feed(self, event):
        if self.closed:
            raise ValueError('Input is complete')
        choices = []
        for hypothesis in self.active:
            self.work.add('adaptive_blueprint_steps')
            links = {(state, token):target for state, token, target in hypothesis.links}
            target = links.get((hypothesis.state, event), self.graph.transitions[hypothesis.state].get(event))
            if target is not None:
                choices.append(Blueprint(target, hypothesis.links))
            elif len(hypothesis.links) < self.maximum_links:
                # A known route is followed directly. A missing connection
                # opens bounded candidates: hold, reuse an existing target
                # for this event, then another established state.
                existing = {row[event] for row in self.graph.transitions if event in row}
                order = [hypothesis.state] + sorted(existing-{hypothesis.state})
                order += [state for state in range(len(self.graph.outputs)) if state not in order]
                for target in order:
                    self.work.add('adaptive_link_proposals')
                    patch = hypothesis.links+((hypothesis.state, event, target),)
                    choices.append(Blueprint(target, patch))
        # Stable tie-breaking is supplied, not learned certainty. Prefer a
        # candidate with fewer new connections, retaining proposal order.
        choices.sort(key=lambda item:len(item.links))
        seen = set()
        self.active = []
        for item in choices:
            if item not in seen:
                self.active.append(item)
                seen.add(item)
            if len(self.active) >= self.beam:
                break
        self.events += 1
        self.maximum_active = max(self.maximum_active, len(self.active))

    def close(self):
        self.closed = True

    def proposals(self):
        if not self.closed:
            raise ValueError('A proposed answer requires completed input')
        return [(item, self.graph.outputs[item.state]) for item in self.active
            if self.graph.outputs[item.state] is not None]

    def commit(self, candidate, current_graph):
        if not self.closed or candidate not in self.active:
            raise ValueError('Only a completed live candidate can be accepted')
        if hashlib.sha256(encoded(current_graph.record())).hexdigest() != self.fingerprint:
            raise ValueError('The parent configuration changed')
        edges = deepcopy(current_graph.transitions)
        for state, token, target in candidate.links:
            if token in current_graph.transitions[state]:
                raise ValueError('An extension cannot replace a defined connection')
            edges[state][token] = target
        successor = EventConfiguration(edges, list(current_graph.outputs))
        # Every old transition and output is identical. By induction on
        # events, every previously defined execution remains identical.
        assert successor.outputs == current_graph.outputs
        assert all(all(successor.transitions[i][token] == target for token, target in row.items())
            for i, row in enumerate(current_graph.transitions))
        return successor
