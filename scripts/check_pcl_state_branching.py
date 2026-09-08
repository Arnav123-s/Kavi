"""Read-only structural diagnostics; no curriculum or candidate fitting."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import time

from kavi.composable_configurations import Work
from kavi.phase.model import PhaseConfiguration
from kavi.phase.runtime import PhaseActivity


def inspect(path):
    raw = path.read_bytes()
    circuit = PhaseConfiguration.from_record(json.loads(raw)['circuit'])
    alphabet = sorted({event for event, _, _ in circuit.impulses})
    if len(alphabet) > 6:
        raise ValueError('Diagnostic limited to six event symbols')
    work = Work(limit=1_000_000)
    states = set()
    permutations = 0
    for sequence in itertools.permutations(alphabet):
        activity = PhaseActivity(circuit, work)
        for event in sequence:
            activity.accept(event)
        states.add(activity.phases)
        permutations += 1
    return {'artifact': path.name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'bytes': len(raw), 'couplings': len(circuit.couplings),
            'permutations_checked': permutations, 'distinct_final_states': len(states),
            'uncoupled_commutative_transitions': not circuit.couplings,
            'work': work.counts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    start, cpu = time.perf_counter(), time.process_time()
    results = [inspect(args.run_dir / f'regions-{seed}.json') for seed in (7, 19, 41)]
    print(json.dumps({'kind': 'structural-diagnostic-not-training', 'models': results,
                      'wall_seconds': time.perf_counter()-start,
                      'cpu_seconds': time.process_time()-cpu}, indent=2))


if __name__ == '__main__':
    main()
