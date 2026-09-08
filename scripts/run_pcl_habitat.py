"""Teach a boundary from original mathematical roles, then replace it atomically."""

import argparse
import hashlib
from pathlib import Path
import traceback

from kavi.composable_configurations import Work,encoded
from kavi.phase.model import PhaseConfiguration
from kavi.phase.layers import CircuitTemplate,CircuitGeneration
from kavi.phase.habitat import Habitat,WorldGeneration,teach_world
from scripts.configuration_run_support import ROOT,Run
from scripts.pcl_discrete_source import packet,DIGEST,DATA
from scripts.run_pcl_discrete import score


def run(folder):
    files=['scripts/run_pcl_habitat.py','kavi/phase/habitat.py','kavi/phase/model.py',
           'kavi/phase/layers.py','kavi/phase/runtime.py','kavi/phase/learning.py',
           'kavi/phase/selection.py','kavi/phase/logic.py','scripts/pcl_discrete_source.py',
           'scripts/run_pcl_discrete.py','scripts/configuration_run_support.py']
    session=Run(folder,'docs/PCL_LEARNED_HABITAT_PROTOCOL.md',files)
    try:
        banks=packet()
        session.result.update(source_sha256=DIGEST,source_bytes=(DATA/'logic.html').stat().st_size,arms={})
        alphabet=sorted({e for seq,_ in banks['first'] for e in seq})
        session.present('Learning the boundary as well as the circuit',
            'The habitat starts empty. Repeated structural contexts will determine roles; role names are not supplied.',
            'First: 8 AND/OR cases. Next: only 10 new cases.',
            boxes=['Original lessons','Infer roles and boundary','Rebuild inner circuit','Check old abilities'])
        finished={}
        for seed in (7,19,41):
            inner=CircuitGeneration(CircuitTemplate((3,5,7,11),max_couplings=6),
                  PhaseConfiguration((3,5,7,11),tuple((e,i%4,1) for i,e in enumerate(alphabet))))
            world=WorldGeneration(Habitat(),inner)
            arm={'stages':[]};session.result['arms'][str(seed)]=arm
            for name,lessons in [('initial',banks['first']),('additional',banks['training'][8:])]:
                work=Work(check=session.check,limit=10_000_000)
                stage={'name':name,'new_source_cases':len(lessons)}
                session.present('Reconstructing the two learned layers',
                    'Earlier obligations come from the old template and circuit. New source cases can require new roles.',
                    f'Seed {seed}, {name}: {len(lessons)} source cases',active=2,delay=.5)
                try:
                    world,stage['selection']=teach_world(world,lessons,work,candidates=256,seed=seed)
                except InterruptedError as error:
                    if str(error)!='Configuration work budget exhausted':raise
                    stage['failure']=str(error)
                stage['learning_work']=dict(work.counts)
                checks=Work(check=session.check)
                stage['new_correct']=sum(world.predict(seq,checks)==port for seq,port in lessons)
                stage['old_source_correct']=sum(world.predict(seq,checks)==port for seq,port in banks['first'])
                language=set(world.habitat.language(checks))
                expected={seq for seq,_ in (banks['first'] if name=='initial' else banks['training'])}
                stage.update(habitat=world.habitat.record(),boundary_size=len(language),
                             source_boundary_equal=language==expected,check_work=dict(checks.counts),
                             habitat_bytes=len(encoded(world.habitat.record())),
                             inner_bytes=len(encoded(world.inner.record())),world_bytes=len(encoded(world.record())))
                arm['stages'].append(stage)
                session.present('Boundary and earlier answers checked',
                    'A role is a group discovered from matching contexts. It does not yet mean a person, object or place.',
                    f'Seed {seed}: {len(world.habitat.roles)} roles, {len(world.habitat.patterns)} arrangements; '
                    f'{stage["old_source_correct"]}/8 earlier source answers',active=3,delay=.5)
            finished[seed]=world
        session.present('All learning stopped; compatibility regression',
            'These compound questions were published earlier. Repeating them checks preservation, not new generalization.',active=3)
        for seed,world in finished.items():
            work=Work(check=session.check)
            arm=session.result['arms'][str(seed)]
            before=encoded(world.record())
            arm['source_correct']=sum(world.predict(seq,work)==port for seq,port in banks['training'])
            arm['source_total']=len(banks['training'])
            arm['compound_regression']=score(world,banks['final'],work)
            assert before==encoded(world.record())
            arm['frozen_unchanged']=True;arm['final_work']=dict(work.counts)
            arm['artifact']={'file':f'world-{seed}.json','bytes':len(before),
                             'sha256':hashlib.sha256(before).hexdigest()}
            (session.folder/f'world-{seed}.json').write_bytes(before)
        session.finish(message='The learned-boundary experiment is complete. No learning or automatic restart remains active.')
    except Exception as error:
        session.result['error']=str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error));raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-dir',type=Path,required=True);run(parser.parse_args().run_dir)
