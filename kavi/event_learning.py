"""Acquire sparse recurrent event transitions from corrected source sequences."""

from collections import deque
from dataclasses import dataclass
import random


@dataclass
class EventConfiguration:
    transitions: list
    outputs: list

    def predict(self, events, work):
        state = 0
        for event in events:
            work.add('event_transition_reads')
            state = self.transitions[state].get(event, -1)
            if state < 0:
                return None
        return self.outputs[state]

    def record(self):
        return {'transitions':self.transitions, 'outputs':self.outputs}


def prefix(examples, work, max_states):
    edges, outputs = [{}], [None]
    for events, label in sorted(examples, key=lambda row:(len(row[0]), row[0])):
        if type(label) is not int:
            raise ValueError('An event outcome must identify an output port')
        state = 0
        for event in events:
            work.add('event_prefix_steps')
            if event not in edges[state]:
                if len(edges) >= max_states:
                    raise ValueError('Event-state ceiling reached')
                edges[state][event] = len(edges)
                edges.append({})
                outputs.append(None)
            state = edges[state][event]
        if outputs[state] is not None and outputs[state] != label:
            raise ValueError('The input encoding collapsed contradictory source lessons')
        outputs[state] = label
    if not examples:
        raise ValueError('No event lessons')
    return EventConfiguration(edges, outputs)


def merge(model, left, right, work):
    parent = list(range(len(model.outputs)))
    edges = [dict(row) for row in model.transitions]
    outputs = list(model.outputs)
    work.add('event_copied_states', len(outputs))
    work.add('event_copied_edges', sum(map(len, edges)))
    def find(state):
        while state != parent[state]:
            parent[state] = parent[parent[state]]
            state = parent[state]
        return state
    pending = [(left, right)]
    while pending:
        work.add('event_merge_closure')
        a, b = (find(state) for state in pending.pop())
        if a == b:
            continue
        if outputs[a] is not None and outputs[b] is not None and outputs[a] != outputs[b]:
            return None
        parent[b] = a
        if outputs[a] is None:
            outputs[a] = outputs[b]
        for event, child in edges[b].items():
            work.add('event_merge_edge_checks')
            if event in edges[a]:
                pending.append((edges[a][event], child))
            else:
                edges[a][event] = child
    entry = find(0)
    numbering, queue = {entry:0}, deque([entry])
    new_edges, new_outputs = [], []
    while queue:
        state = queue.popleft()
        row = {}
        for event, child in sorted(edges[state].items()):
            work.add('event_canonical_edges')
            child = find(child)
            if child not in numbering:
                numbering[child] = len(numbering)
                queue.append(child)
            row[event] = numbering[child]
        new_edges.append(row)
        new_outputs.append(outputs[state])
    mapping = {state:numbering[find(state)] for state in range(len(outputs))}
    return EventConfiguration(new_edges, new_outputs), mapping


def learn(examples, work, *, seed=7, max_states=10000, max_merges=10000):
    """Supplied frontier-merging rule; learned states, links and output ports."""
    model = prefix(examples, work, max_states)
    initial_states = len(model.outputs)
    red, rng = {0}, random.Random(seed)
    proposed = accepted = rejected = 0
    while True:
        work.add('event_frontier_steps')
        blue = sorted({child for state in red for child in model.transitions[state].values() if child not in red})
        if not blue:
            break
        frontier = blue[0]
        candidates = sorted(red)
        rng.shuffle(candidates)
        for established in candidates:
            if proposed >= max_merges:
                raise ValueError('Event merge-proposal ceiling reached')
            proposed += 1
            result = merge(model, established, frontier, work)
            if result is None:
                rejected += 1
                continue
            model, mapping = result
            red = {mapping[state] for state in red}
            accepted += 1
            break
        else:
            red.add(frontier)
    for events, label in examples:
        if model.predict(events, work) != label:
            raise ValueError('A merged configuration lost a teaching constraint')
    return model, {'prefix_states':initial_states, 'states':len(model.outputs),
        'edges':sum(map(len, model.transitions)), 'proposals':proposed,
        'accepted':accepted, 'rejected':rejected, 'seed':seed}
