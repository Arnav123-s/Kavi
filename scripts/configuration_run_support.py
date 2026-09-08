"""Controls and private evidence for finite visible experiments."""

import hashlib
import json
from pathlib import Path
import sys
import time

from kavi.circuit_runtime import write_json
from kavi.trial_resources import memory_reading

ROOT = Path(__file__).resolve().parents[1]


def safe(value):
    if isinstance(value, complex):
        return {'real': value.real, 'imag': value.imag}
    if isinstance(value, dict):
        return {k: safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [safe(v) for v in value]
    return value


class Run:
    def __init__(self, folder, protocol, sources):
        self.folder = folder.resolve()
        if self.folder.exists() or not self.folder.is_relative_to(ROOT / 'runs'):
            raise ValueError('A fresh directory inside runs is required')
        self.folder.mkdir(parents=True)
        self.start, self.cpu = time.monotonic(), time.process_time()
        self.next_check = self.pacing = 0.
        self.status = {'state': 'running', 'phase': 'Preparing', 'message': '', 'rows': []}
        self.result = {'author': 'Arnav123-s', 'state': 'running', 'protocol': protocol,
            'python': sys.version.split()[0], 'limits': {'seconds': 300, 'worker_bytes': 512*1024**2},
            'source_hashes': {name: hashlib.sha256((ROOT/name).read_text(encoding='utf-8').encode('utf-8')).hexdigest()
                              for name in [protocol, *sources]}}

    def check(self):
        now = time.monotonic()
        if now < self.next_check:
            return
        self.next_check = now + .05
        if (self.folder/'STOP').exists() or now-self.start >= 300:
            raise InterruptedError('Stopped or five-minute budget exhausted')
        if (memory_reading().get('working_set_bytes') or 0) > 512*1024**2:
            raise InterruptedError('Worker memory ceiling exceeded')
        if (self.folder/'PAUSE').exists():
            write_json(self.folder/'status.json', dict(self.status, state='paused'))
            while (self.folder/'PAUSE').exists():
                if (self.folder/'STOP').exists() or time.monotonic()-self.start >= 300:
                    raise InterruptedError('Stopped while paused')
                time.sleep(.05)
            write_json(self.folder/'status.json', self.status)

    def present(self, phase, message, evidence='', *, boxes=None, active=2, detail='', delay=1.5):
        self.check()
        if evidence:
            self.status['rows'].append({'lesson': phase, 'status': evidence})
        self.status.update(phase=phase, message=message, active=active, detail=detail)
        if boxes:
            self.status['boxes'] = boxes
        self.save()
        with (self.folder/'transcript.txt').open('a', encoding='utf-8') as handle:
            handle.write(phase + ': ' + message + '\n' + evidence + '\n')
        before = time.monotonic()
        while time.monotonic()-before < delay:
            self.check()
            time.sleep(.05)
        self.pacing += time.monotonic()-before

    def save(self):
        write_json(self.folder/'status.json', safe(self.status))
        write_json(self.folder/'results.json', safe(self.result))

    def finish(self, state='completed', message='The results are saved. Teaching has stopped.'):
        self.result.update(state=state, wall_seconds=time.monotonic()-self.start,
            cpu_seconds=time.process_time()-self.cpu, display_pacing_seconds=self.pacing,
            worker_memory=memory_reading())
        self.status.update(state=state, phase='Finished' if state == 'completed' else 'Stopped', message=message)
        self.save()
        census = {p.name: p.stat().st_size for p in self.folder.iterdir() if p.is_file()}
        write_json(self.folder/'storage.json', {'files': census, 'bytes_excluding_this_census': sum(census.values())})
