"""Learn new routes by first aligning them with an acquired event graph."""

from collections import deque
import random

from .event_learning import EventConfiguration, merge, prefix

ENTRY = '<source-question>'


def preserves(base, successor, embedding, work):
    """A finite simulation certificate for every defined earlier execution."""
    if len(embedding) != len(base.outputs) or embedding[0] != 0:
        return False
    for state, target in enumerate(embedding):
        work.add('transfer_preservation_states')
        if not 0 <= target < len(successor.outputs) or base.outputs[state] != successor.outputs[target]:
            return False
        for event, child in base.transitions[state].items():
            work.add('transfer_preservation_edges')
            if successor.transitions[target].get(event) != embedding[child]:
                return False
    return True


def graft(base, examples, work, *, reuse=True, seed=7, max_states=18000, max_merges=12000):
    """Try old states before new states, subject to exact earlier-path preservation.

    The comparison arm retains the same old graph and entry interface but forbids
    merges into its states. No prior lesson strings are required for preservation.
    New teaching constraints are external training workspace, not inference data.
    """
    if ENTRY in base.transitions[0]:
        raise ValueError('The reserved teaching entry already exists')
    expanded = prefix(examples, work, max_states-len(base.outputs))
    offset = len(base.outputs)
    edges = [dict(row) for row in base.transitions]
    edges[0][ENTRY] = offset
    edges.extend({token: child+offset for token, child in row.items()} for row in expanded.transitions)
    model = EventConfiguration(edges, list(base.outputs)+list(expanded.outputs))
    embedding = list(range(offset))
    red, rng = set(embedding), random.Random(seed)
    stats = {'seed': seed, 'reuse_enabled': reuse, 'prefix_states': len(expanded.outputs),
             'old_states': offset, 'proposals': 0, 'accepted': 0, 'rejected': 0,
             'old_state_merges': 0, 'preservation_rejections': 0}
    while True:
        work.add('transfer_frontier_steps')
        blue = sorted({child for state in red for child in model.transitions[state].values() if child not in red})
        if not blue:
            break
        frontier = blue[0]
        old = set(embedding)
        old_choices = sorted(old) if reuse else []
        new_choices = sorted(red-old)
        rng.shuffle(old_choices)
        rng.shuffle(new_choices)
        for established in old_choices+new_choices:
            if stats['proposals'] >= max_merges:
                raise ValueError('Transfer merge-proposal ceiling reached')
            stats['proposals'] += 1
            result = merge(model, established, frontier, work)
            if result is None:
                stats['rejected'] += 1
                continue
            candidate, mapping = result
            new_embedding = [mapping[state] for state in embedding]
            if not preserves(base, candidate, new_embedding, work):
                stats['rejected'] += 1
                stats['preservation_rejections'] += 1
                continue
            if established in old:
                stats['old_state_merges'] += 1
            model, embedding = candidate, new_embedding
            red = {mapping[state] for state in red}
            stats['accepted'] += 1
            break
        else:
            red.add(frontier)
    if not preserves(base, model, embedding, work):
        raise ValueError('Earlier-path simulation failed')
    for sequence, label in examples:
        if model.predict((ENTRY,)+sequence, work) != label:
            raise ValueError('A transfer candidate lost a teaching constraint')
    # Count graph nodes reachable from the new entry which are also images of
    # old nodes. This is structural reuse, not evidence of shared meaning.
    seen, queue = set(), deque([model.transitions[0][ENTRY]])
    while queue:
        state = queue.popleft()
        if state in seen:
            continue
        work.add('transfer_reachability_states')
        seen.add(state)
        queue.extend(model.transitions[state].values())
    stats.update(states=len(model.outputs), edges=sum(map(len, model.transitions)),
        shared_reachable_states=len(seen & set(embedding)), exact_old_simulation=True)
    return model, embedding, stats
