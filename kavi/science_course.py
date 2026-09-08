"""Structured scientific lessons and dependency-directed quantitative inference."""

from dataclasses import dataclass
import hashlib
import math

from .composable_configurations import Configuration, Unresolved, encoded, fit


@dataclass(frozen=True)
class Relation:
    target: str
    inputs: tuple
    configuration: str
    guard: str | None = None

    def record(self):
        return {'target':self.target,'inputs':self.inputs,'configuration':self.configuration,'guard':self.guard}


def precise(a, b):
    return isinstance(a,(int,float)) and math.isfinite(a) and abs(a-b) <= max(1e-300,abs(b)*1e-8)


class ScienceModel:
    def __init__(self, registry, relations=()):
        self.registry = registry
        self.relations = list(relations)

    def answer(self, givens, target, work):
        values, trace = dict(givens), []
        def resolve(role, visiting):
            work.add('binding_visits')
            if role in values:
                return values[role]
            if role in visiting or len(visiting) >= 16:
                raise Unresolved('Unresolved dependency: '+role)
            for relation in self.relations:
                work.add('relation_matches')
                if relation.target != role or (relation.guard and givens.get(relation.guard) is not True):
                    continue
                try:
                    args = tuple(resolve(item, visiting+(role,)) for item in relation.inputs)
                    output = self.registry.execute(relation.configuration,args,work)
                except (Unresolved, ValueError, TypeError, ZeroDivisionError):
                    continue
                values[role] = output
                trace.append({'target':role,'configuration':relation.configuration,'args':args,'value':output})
                return output
            raise Unresolved('No acquired configuration can resolve '+role)
        try:
            value = resolve(target,())
            return {'state':'answered','value':value,'trace':trace}
        except Unresolved as error:
            return {'state':'unresolved','reason':str(error),'trace':trace}

    def record(self):
        return {'format':'kavi-structured-science-1','registry':self.registry.record(),
                'relations':[r.record() for r in self.relations]}


OPERATIONS = ('real_add','real_subtract','real_multiply','real_divide')
SPECS = {
    'sum': (2, lambda a:a[0]+a[1], 'arithmetic'),
    'difference': (2, lambda a:a[0]-a[1], 'arithmetic'),
    'work': (2, lambda a:a[0]*a[1], 'joule-1850'),
    'ratio': (2, lambda a:a[0]/a[1], 'arithmetic'),
    'heat': (3, lambda a:a[0]*a[1]*a[2], 'fourier-1822'),
    'thermal_inverse': (3, lambda a:a[0]/(a[1]*a[2]), 'fourier-1822'),
    'rest_energy': (2, lambda a:a[0]*a[1]**2, 'einstein-1905'),
    'mass_equivalent': (2, lambda a:a[0]/a[1]**2, 'einstein-1905'),
    'identity': (1, lambda a:a[0], 'joule-1850'),
}


RELATIONS = (
    Relation('delta_temperature',('final_temperature','initial_temperature'),'science_difference'),
    Relation('heat',('mass','specific_heat','delta_temperature'),'science_heat'),
    Relation('work',('force','distance'),'science_work'),
    Relation('heat',('work',),'science_identity','full_thermalization'),
    Relation('delta_temperature',('heat','mass','specific_heat'),'science_thermal_inverse'),
    Relation('specific_heat',('heat','mass','delta_temperature'),'science_thermal_inverse'),
    Relation('mass',('heat','specific_heat','delta_temperature'),'science_thermal_inverse'),
    Relation('final_temperature',('initial_temperature','delta_temperature'),'science_sum'),
    Relation('heat_power',('heat','duration'),'science_ratio'),
    Relation('energy',('mass','light_speed'),'science_rest_energy'),
    Relation('mass_equivalent',('energy','light_speed'),'science_mass_equivalent'),
    Relation('energy_MeV',('energy','joules_per_MeV'),'science_ratio'),
)


def teach(model, name, lessons, work):
    arity = SPECS[name][0]
    selected = fit(model.registry,'science_'+name,lessons,OPERATIONS,work,arity=arity)
    if selected is None:
        raise ValueError('No configuration fits the scientific lessons: '+name)
    model.registry.install('science_'+name,selected)
    return selected


def consolidate(model):
    """Exact structural sharing of definitions, without behavioral guessing."""
    known, shares = {}, []
    for name in sorted(n for n in model.registry.definitions if n.startswith('science_')):
        config = model.registry.definitions[name]
        key = hashlib.sha256(encoded(config.record())).hexdigest()
        if key in known:
            target = known[key]
            model.registry.install(name,Configuration(config.arity,((target,tuple(range(config.arity))),),config.arity))
            shares.append({'configuration':name,'shares':target})
        else:
            known[key] = name
    return shares
