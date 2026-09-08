"""Reuse finite configurations while learning from identified published problems."""

import hashlib
import itertools
import json
import math
from pathlib import Path

from .composable_configurations import Configuration, encoded, fit
from .equation_kernels import make_registry, scalar
from .procedure_core import ProcedureLibrary
from .science_course import Relation, ScienceModel, precise


def load_science(path, library_path, *, extended=False):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    registry = make_registry(ProcedureLibrary.load(library_path))
    if extended:
        extend_kernels(registry)
    if registry.substrate != data['registry']['substrate']:
        raise ValueError('The model and its supplied arithmetic substrate differ')
    registry.definitions = {n: Configuration.decode(v) for n, v in data['registry']['definitions'].items()}
    return ScienceModel(registry, [Relation(r['target'], tuple(r['inputs']), r['configuration'], r['guard'])
                                   for r in data['relations']])


def extend_kernels(registry):
    kernels = {'half': lambda a,w: scalar(a[0])/2,
               'double': lambda a,w: scalar(a[0])*2,
               'square_root': lambda a,w: math.sqrt(scalar(a[0])),
               'cube_root': lambda a,w: math.cbrt(scalar(a[0]))}
    registry.kernels.update(kernels)
    for name in kernels:
        registry.install(name, Configuration(1, kernel=name))
    registry.substrate = hashlib.sha256(registry.substrate.encode() +
        Path(__file__).read_text(encoding='utf-8').encode()).hexdigest()


def fit_three(registry, name, lessons, operations, work, arity=2):
    """Exhaustive depth-three extension, with every proposal charged."""
    best = None
    trial = registry.copy()
    def graphs(prefix):
        for ref in range(arity) if not prefix else (arity+len(prefix)-1,):
            yield Configuration(arity, prefix, ref)
        if len(prefix) == 3:
            return
        for op in operations:
            for refs in itertools.product(range(arity+len(prefix)), repeat=registry.definitions[op].arity):
                yield from graphs(prefix+((op,refs),))
    for graph in graphs(()):
        work.add('candidate_proposals')
        trial.install(name,graph)
        good = True
        for args, expected in lessons:
            work.add('candidate_examples')
            try:
                if not precise(trial.execute(name,args,work),expected):
                    good=False
                    break
            except (ValueError, TypeError, OverflowError, ZeroDivisionError):
                work.add('invalid_candidates')
                good=False
                break
        if good:
            work.add('consistent_candidates')
            if best is None or (len(graph.calls),encoded(graph.record())) < (len(best.calls),encoded(best.record())):
                best=graph
    if best is None:
        raise ValueError('No configuration fits these published lessons')
    return best


def learn(model, name, lessons, operations, work, *, arity=2, depth=2):
    graph = (fit_three(model.registry,name,lessons,operations,work,arity) if depth==3 else
             fit(model.registry,name,lessons,operations,work,arity=arity))
    if graph is None:
        raise ValueError('No configuration fits '+name)
    model.registry.install(name,graph)
    return graph


NEW_RELATIONS = (
    Relation('kinetic_energy',('mass','speed'),'published_kinetic'),
    Relation('relative_kinetic_energy',('reference_energy','mass_factor','slower_factor'),'published_relative'),
    Relation('kinetic_ratio',('first_energy','second_energy'),'published_ratio'),
    Relation('first_energy',('first_mass','first_speed'),'published_kinetic'),
    Relation('second_energy',('second_mass','second_speed'),'published_kinetic'),
    Relation('duration',('heat','heat_power'),'published_ratio'),
    Relation('duration',('work','power'),'published_ratio'),
    Relation('minutes',('duration','seconds_per_minute'),'published_ratio'),
    Relation('speed_factor',('power_factor',),'published_boat'),
    Relation('potential_energy',('mass','gravity','height'),'published_lift'),
    Relation('work',('potential_energy',),'science_identity'),
    Relation('power',('work','duration'),'published_ratio'),
    Relation('kinetic_energy',('potential_energy','heat_loss'),'published_remaining'),
    Relation('speed',('kinetic_energy','mass'),'published_speed'),
    Relation('electric_energy',('power','duration'),'science_work'),
    Relation('energy_kWh',('electric_energy','joules_per_kWh'),'published_ratio'),
    Relation('cost',('energy_kWh','price_per_kWh'),'science_work'),
)
