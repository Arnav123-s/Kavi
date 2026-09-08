"""Measure exact sharing of acquired structures; perform no teaching."""

import argparse
import hashlib
import json
from pathlib import Path
import time

from kavi.composable_configurations import Work,encoded
from kavi.shared_english_configurations import share_configuration,verify_representation

ROOT=Path(__file__).resolve().parents[1]


def run(destination):
    destination=Path(destination)
    destination.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();cpu=time.process_time()
    path=ROOT/'experiments/english-20260907-expanded-model.json'
    original=json.loads(path.read_text(encoding='utf-8'))
    work=Work(limit=1_000_000)
    unshared=share_configuration(original,work,share=False)
    shared=share_configuration(original,work)
    preserved=verify_representation(original,shared,work)
    if not preserved:raise ValueError('Sharing changed an acquired computation')
    body=encoded(shared)
    (destination/'model.json').write_bytes(body)
    result={'author':'Arnav123-s','date':'2026-09-07','state':'completed',
        'new_training':False,'method':'Identical ordered substructures only',
        'original_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'original_bytes':path.stat().st_size,'same_format_unshared_bytes':len(encoded(unshared)),
        'shared_bytes':len(body),'shared_sha256':hashlib.sha256(body).hexdigest(),
        'predicate_nodes_before':len(unshared['nodes']),'predicate_nodes_after':len(shared['nodes']),
        'program_nodes_before':len(unshared['program_nodes']),
        'program_nodes_after':len(shared['program_nodes']),
        'program_roots':len(shared['programs']),
        'all_predicates_and_programs_preserved':preserved,
        'work':work.counts,'wall_seconds':time.perf_counter()-started,
        'cpu_seconds':time.process_time()-cpu,
        'peak_memory_bytes':None,
        'memory_note':'Peak process memory was not measured for this short transformation.',
        'source_hashes':{p:hashlib.sha256((ROOT/p).read_text(encoding='utf-8').encode()).hexdigest()
            for p in ['kavi/shared_english_configurations.py','scripts/check_shared_english.py']},
        'claim':'Exact representational preservation under the unchanged interpreter; no new semantic accuracy result.'}
    (destination/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    run(parser.parse_args().output)
