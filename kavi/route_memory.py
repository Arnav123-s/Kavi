"""Retain executable routes, trying alternatives only after a route fails.

The caller supplies observed context features and teaching examples. This is
not task-intent recognition from an unlabelled number tuple.
"""

from dataclasses import asdict
import json
import time

from .procedure_core import Limits
from .procedure_search import ProgramSearch, SearchExhausted


class RouteMemory:
    def __init__(self, library, router):
        self.library = library
        self.router = router
        self.routes = []

    def acquire(self, features, arity, teaching, *, seconds=4, check=lambda: None):
        started = time.monotonic()
        limits = Limits(max_calls=5000, max_gates=200000, max_iterations=256)
        evidence = {'route_checks':0, 'route_calls':0, 'route_gates':0,
                    'attempts':[], 'reused':False, 'body':None}

        def guard():
            check()
            if time.monotonic()-started >= seconds:
                raise SearchExhausted('Total route acquisition time exhausted')

        # The most recent matching context is tried first. Other routes are
        # inspected only if it is absent or fails the supplied lesson evidence.
        matching = [r for r in reversed(self.routes) if r['features']==list(features)]
        others = [r for r in reversed(self.routes) if r not in matching and r['arity']==arity]
        try:
            for route in matching+others:
                guard()
                fits = True
                for example in teaching:
                    guard()
                    evidence['route_checks'] += 1
                    try:
                        observed = self.library.execute_expr(route['body'], example.inputs,
                                                             limits=limits,check=guard)
                        evidence['route_calls'] += observed.calls
                        evidence['route_gates'] += observed.gates
                        if observed.value != example.target:
                            fits = False
                            break
                    except ValueError as error:
                        partial = getattr(error, 'execution', None)
                        if partial:
                            evidence['route_calls'] += partial.calls
                            evidence['route_gates'] += partial.gates
                        fits = False
                        break
                if fits:
                    evidence.update(body=route['body'],reused=True)
                    return evidence
            used_candidates = used_cases = 0
            for phase in ('focused','broad'):
                guard()
                remaining = seconds-(time.monotonic()-started)
                if used_candidates>=8000 or used_cases>=160000:
                    break
                search = ProgramSearch(self.library,max_nodes=3,
                    max_candidates=min(2000,8000-used_candidates) if phase=='focused' else 8000-used_candidates,
                    max_candidate_cases=min(40000,160000-used_cases) if phase=='focused' else 160000-used_cases,
                    max_seconds=min(1,remaining) if phase=='focused' else remaining,
                    max_cache_entries=12000,limits=limits,check=guard,allowed_tags=('call',),
                    allowed_names=self.router.select(features) if phase=='focused' else None)
                attempt = {'phase':phase}
                try:
                    body = search.learn(arity,teaching)
                    if len(self.routes)>=64:
                        raise ValueError('Route-memory capacity reached')
                    self.routes.append({'features':list(features),'arity':arity,'body':body})
                    evidence['body'] = body
                except SearchExhausted as error:
                    attempt['failure'] = str(error)
                attempt['stats'] = asdict(search.stats)
                evidence['attempts'].append(attempt)
                used_candidates += search.stats.candidates
                used_cases += search.stats.candidate_cases
                if evidence['body'] is not None:
                    break
        except SearchExhausted as error:
            evidence['failure'] = str(error)
        finally:
            evidence['seconds'] = time.monotonic()-started
        return evidence

    def encoded(self):
        return (json.dumps({'schema':'kavi.route-memory.v1','routes':self.routes},
                           sort_keys=True,separators=(',',':'))+'\n').encode()
