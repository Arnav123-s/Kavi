"""Current-state execution of finite phase circuits."""

class PhaseActivity:
    """One finite-state invocation. Unknown input prevents a stale answer."""

    def __init__(self, configuration, work):
        self.configuration, self.work = configuration, work
        self.phases = (0,) * len(configuration.moduli)
        self.closed = self.failed = False

    def accept(self, event):
        if self.closed or self.failed:
            raise ValueError('Invocation is closed or failed')
        c = self.configuration
        try:
            delta, recognized = [0] * len(self.phases), False
            for symbol, target, kick in c.impulses:
                self.work.add('phase_impulse_checks')
                if symbol == event:
                    delta[target] += kick
                    recognized = True
            if not recognized:
                self.failed = True
                return None
            state = tuple((p+d) % m for p, d, m in zip(self.phases, delta, c.moduli))
            for _ in range(c.ticks):
                self.work.add('phase_ticks')
                delta = [0] * len(state)
                for source, trigger, target, kick in c.couplings:
                    self.work.add('phase_coupling_checks')
                    if state[source] == trigger:
                        delta[target] += kick
                self.work.add('phase_updates', len(state))
                state = tuple((p+d) % m for p, d, m in zip(state, delta, c.moduli))
            self.phases = state
        except BaseException:
            self.failed = True
            raise
        # Phases are inspectable; an answer is released only by finish().
        return None

    def finish(self):
        if self.closed:
            raise ValueError('Invocation is already complete')
        self.closed = True
        if self.failed:
            return None
        for state, port in self.configuration.outputs:
            self.work.add('phase_readout_checks')
            if state == self.phases:
                return port
        return None
