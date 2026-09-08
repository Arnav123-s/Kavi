"""Event-driven execution of interacting configurations with current-state latches.

The interpreter supplies propagation and hold semantics. A compiled acquired
program supplies its connections. Arbitrary semantic routing is not learned here.
"""

from collections import deque
from dataclasses import dataclass
import hashlib

from kavi.composable_configurations import StaleConfiguration, encoded


class _Hold:
    pass


HOLD = _Hold()


@dataclass(frozen=True)
class SignalGraph:
    arity: int
    calls: tuple
    output: int
    seeds: tuple = ()
    dependencies: tuple = ()
    substrate: str | None = None
    trigger_refs: tuple = ()

    def __post_init__(self):
        size = self.arity + len(self.calls)
        if type(self.arity) is not int or self.arity < 0 or not 0 <= self.output < size:
            raise ValueError('Invalid signal interface')
        for name, refs in self.calls:
            if not isinstance(name,str) or any(type(r) is not int or not 0 <= r < size for r in refs):
                raise ValueError('Invalid signal connection')
        for ref,_ in self.seeds:
            if type(ref) is not int or not 0 <= ref < size:
                raise ValueError('Invalid seed connection')
        if self.trigger_refs and len(self.trigger_refs)!=len(self.calls):
            raise ValueError('Trigger interfaces must match configuration calls')
        for index,refs in enumerate(self.trigger_refs):
            if refs is not None and any(ref not in self.calls[index][1] for ref in refs):
                raise ValueError('A trigger must reference a call input')

    @classmethod
    def from_registry(cls, registry, name, work):
        expanded = registry.expand(name,work)
        return cls(expanded.arity,expanded.calls,expanded.output,
                   dependencies=expanded.dependencies,substrate=expanded.substrate)

    def verify(self,registry,work):
        if self.substrate is None:
            return
        if registry is None or registry.substrate != self.substrate:
            raise StaleConfiguration('The signal graph requires its unchanged substrate')
        work.add('signal_guard_dependencies',len(self.dependencies))
        for name,digest in self.dependencies:
            current=registry.definitions.get(name)
            if current is None:
                raise StaleConfiguration('A signal dependency disappeared')
            raw=encoded(current.record())
            work.add('signal_guard_bytes',len(raw))
            if hashlib.sha256(raw).hexdigest()!=digest:
                raise StaleConfiguration('A signal dependency changed; compile a new invocation')


class SignalExecution:
    """One invocation's latest port values and pending activations; no step log."""

    def __init__(self, graph, invoke, work, observe=None, *, registry=None):
        self.graph, self.invoke, self.work = graph, invoke, work
        self.registry = registry
        graph.verify(registry,work)
        self.observe = observe
        self.input_complete = False
        self.input_ports = set()
        self.failure = None
        self.values = {}
        self.revisions = {}
        self.signatures = {}
        self.pending = deque()
        self.queued = set()
        self.dependents = {}
        self.phase = ['waiting'] * len(graph.calls)
        self.invocations = 0
        for index,(_,refs) in enumerate(graph.calls):
            for ref in set(refs):
                self.dependents.setdefault(ref,[]).append(index)
            if not refs:
                self._queue(index)
        for ref,value in graph.seeds:
            self._store(ref,value)

    def _queue(self,index):
        if index not in self.queued:
            self.pending.append(index)
            self.queued.add(index)
            self.phase[index] = 'ready'

    def _store(self,ref,value):
        self.values[ref] = value
        self.revisions[ref] = self.revisions.get(ref,0)+1
        for dependent in self.dependents.get(ref,()):
            self._queue(dependent)

    def feed(self,port,value):
        if self.input_complete:
            raise ValueError('Input is complete; start a new invocation')
        if type(port) is not int or not 0 <= port < self.graph.arity:
            raise ValueError('Unknown external input port')
        self.graph.verify(self.registry,self.work)
        self.work.add('signal_inputs')
        self.input_ports.add(port)
        self._store(port,value)

    def finish_input(self):
        """Close this input turn. Settlement and complete ports are also required."""
        self.graph.verify(self.registry,self.work)
        self.work.add('signal_input_boundaries')
        self.input_complete = True

    def accept(self,port,value):
        """Consume one event before the caller submits the next event."""
        self.feed(port,value)
        return self.settle()

    def step(self):
        if self.failure is not None:
            raise RuntimeError('This invocation failed; start a new invocation')
        try:
            return self._step()
        except Exception as error:
            self.failure=type(error).__name__+': '+str(error)
            raise

    def _step(self):
        self.graph.verify(self.registry,self.work)
        self.work.add('signal_scheduler_steps')
        if not self.pending:
            return False
        index = self.pending.popleft()
        self.queued.remove(index)
        name,refs = self.graph.calls[index]
        if any(ref not in self.values for ref in refs):
            self.phase[index] = 'waiting'
            return True
        triggers=self.graph.trigger_refs[index] if self.graph.trigger_refs else None
        signature = tuple(self.revisions[ref] for ref in (refs if triggers is None else triggers))
        if self.signatures.get(index) == signature:
            self.phase[index] = 'held'
            return True
        self.signatures[index] = signature
        self.phase[index] = 'moving'
        self.work.add('signal_configuration_calls')
        value = self.invoke(name,tuple(self.values[ref] for ref in refs),self.work)
        self.invocations += 1
        if value is HOLD:
            self.phase[index] = 'held'
        else:
            self.phase[index] = 'held'
            self._store(self.graph.arity+index,value)
        if self.observe is not None:
            self.observe({'node':index,'configuration':name,'phase':self.phase[index],
                          'emitted':value is not HOLD,'value':None if value is HOLD else value})
        return True

    def settle(self):
        while self.pending:
            self.step()
        return self.status()

    def status(self):
        self.graph.verify(self.registry,self.work)
        complete_ports = len(self.input_ports)==self.graph.arity
        available = (self.failure is None and self.input_complete and complete_ports and not self.pending
                     and self.graph.output in self.values and self.values[self.graph.output] is not None)
        return {'input_complete':self.input_complete,'complete_ports':complete_ports,
                'settled':not self.pending,'output_available':available,
                'output':self.values.get(self.graph.output) if available else None,
                'failure':self.failure,
                'phases':tuple(self.phase),'live_values':len(self.values),
                'pending_activations':len(self.pending),'configuration_calls':self.invocations}


def recurrent_execution(model,work,observe=None):
    """Execute an acquired finite-state graph with one current state and token.

    The transition is triggered by a new token revision. Its feedback state is
    an argument, so revising that state does not consume the same token again.
    """
    columns={token:i for i,token in enumerate(model.alphabet)}
    def invoke(name,args,work):
        work.add('recurrent_signal_kernel_calls')
        if name=='transition':
            token,state=args
            column=columns.get(token)
            if column is None or state<0:return -1
            return model.transitions[state][column]
        state=args[0]
        return model.outputs[state] if state>=0 else None
    graph=SignalGraph(1,(('transition',(0,1)),('readout',(1,))),2,
                      seeds=((1,0),),trigger_refs=((0,),None))
    return SignalExecution(graph,invoke,work,observe)
