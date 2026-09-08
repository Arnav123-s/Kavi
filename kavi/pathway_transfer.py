"""Use an older acquired route graph as structure for further correction."""

from collections import defaultdict
from copy import deepcopy

from .english_configurations import ConnectionTree


def refine(teacher, examples, work, *, depth=4, min_leaf=1):
    """Retain teacher decisions and learn refinements at their destination ports.

    Examples carry genuine source relations, not pseudo-labels from the
    teacher. The refinement algorithm is supplied; the resulting predicates
    are learned. Unvisited destinations retain the teacher's behavior.
    """
    if not examples:
        raise ValueError('No correction lessons')
    groups = defaultdict(list)
    for values, label in examples:
        index = 0
        while 'feature' in teacher.nodes[index]:
            node = teacher.nodes[index]
            work.add('teacher_path_visits')
            index = node['yes'] if node['feature'] in values else node['no']
        groups[index].append((values, label))
    refinements = {}
    for index, lessons in sorted(groups.items()):
        # Retain a destination already agreeing with every source relation.
        # Mixed or disagreeing feedback teaches new local discriminations.
        if all(label == teacher.nodes[index]['ports'][0] for _, label in lessons):
            work.add('retained_teacher_destinations')
            continue
        refinements[index] = ConnectionTree().teach(lessons, work, depth=depth, min_leaf=min_leaf)
        work.add('refined_teacher_destinations')
    nodes = []
    def append(graph, index, inherited):
        if inherited and index in refinements:
            return append(refinements[index].nodes, 0, False)
        node = deepcopy(graph[index])
        target = len(nodes)
        nodes.append(node)
        work.add('transfer_node_copies')
        if 'feature' in node:
            node['yes'] = append(graph, node['yes'], inherited)
            node['no'] = append(graph, node['no'], inherited)
        return target
    append(teacher.nodes, 0, True)
    return ConnectionTree(nodes)
