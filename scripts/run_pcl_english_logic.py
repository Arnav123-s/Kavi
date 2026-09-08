"""Test harder original problems, then teach a bounded English-to-logic bridge."""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import traceback

from kavi.composable_configurations import Work,encoded
from kavi.phase import PhaseConfiguration,CircuitTemplate,CircuitGeneration,reconstruct
from kavi.phase.evaluation import evaluate
from kavi.phase.english_logic import FORMS,events,interpret
from kavi.phase.logic import evaluate_formula,gate_events
from kavi.phase.reasoning import models
from scripts.configuration_run_support import ROOT,Run
from scripts.pcl_discrete_source import packet,DATA
from scripts.pcl_english_logic_source import english,hard_cases,DIGEST
from scripts.run_pcl_discrete import score


def puzzles():
    holmes=[('or','T','S'), ('implies',('and','T','P'),('not','N')),
            ('implies','T',('or','P','S')), ('implies','S','P'), 'N']
    two=('or',('and',('and','A','B'),('not','C')),
         ('or',('and',('and','A','C'),('not','B')),('and',('and','B','C'),('not','A'))))
    third=('or',('and',('and',('not','A'),('not','B')),('not','C')),('or','A',('or','B','C')))
    trolls=[('iff','A',('implies',('not','A'),two)),('iff','B',('not','A')),('iff','C',third)]
    return [('holmes',holmes,('T','S','P','N'),[{'T':0,'S':1,'P':1,'N':1}]),
            ('trolls',trolls,('A','B','C'),[{'A':1,'B':0,'C':1}])]


def run(folder):
    files=['scripts/run_pcl_english_logic.py','scripts/pcl_english_logic_source.py',
           'curriculum/pcl-english-logic-annotations.json','kavi/phase/english_logic.py',
           'kavi/phase/reasoning.py','kavi/phase/logic.py','kavi/phase/runtime.py',
           'kavi/phase/model.py','kavi/phase/layers.py','kavi/phase/learning.py',
           'kavi/phase/selection.py','kavi/phase/evaluation.py',
           'scripts/pcl_discrete_source.py','scripts/run_pcl_discrete.py','scripts/configuration_run_support.py']
    session=Run(folder,'docs/PCL_ENGLISH_LOGIC_PROTOCOL.md',files)
    try:
        old=json.loads((ROOT/'experiments/2026-09-08-pcl-discrete.json').read_text())
        primitives=packet()['training']; truth=dict(primitives)
        training,final=english(); hard=hard_cases()
        session.result.update(english_source_sha256=DIGEST,hard_cases=len(hard),hard={},arms={})
        logic_models={}
        session.present('Harder logic comes first','The learned truth circuits are frozen. New source exercises and multi-premise puzzles will not retrain them.',
                        '36 new table cases and two original puzzles',boxes=['Frozen logic','Harder premises','English teaching','New English questions'])
        for seed in (7,19,41):
            name=f'couplings-6-seed-{seed}'
            raw=(ROOT/'runs/pcl-discrete-20260908'/f'{name}.json').read_bytes()
            if hashlib.sha256(raw).hexdigest()!=old['arms'][name]['artifact']['sha256']:
                raise ValueError('Prior learned circuit changed')
            model=PhaseConfiguration.from_record(json.loads(raw)['circuit']);logic_models[seed]=model
            work=Work(check=session.check)
            result={'tables':score(model,hard,work),'puzzles':{}}
            for label,premises,variables,expected in puzzles():
                found=models(model,premises,variables,work)
                result['puzzles'][label]={'correct':found['complete'] and found['solutions']==expected,**found}
            result['work']=dict(work.counts);result['input_sha256']=hashlib.sha256(raw).hexdigest()
            session.result['hard'][str(seed)]=result
            session.present('Harder frozen results', 'Every compound premise was evaluated through the learned truth circuit.',
                f'Seed {seed}: {result["tables"]["correct"]}/36 table cases; '+
                f'{sum(p["correct"] for p in result["puzzles"].values())}/2 puzzles',active=1,delay=.5)
        learned={}
        evidence=[(events(s,c),p) for s,c,p in training]
        alphabet=sorted({e for seq,_ in evidence for e in seq})
        for seed in (7,19,41):
            circuit=PhaseConfiguration((3,5,7,11),tuple((e,i%4,1) for i,e in enumerate(alphabet)))
            generation=CircuitGeneration(CircuitTemplate(circuit.moduli,max_couplings=6),circuit)
            arm={'stages':[]};session.result['arms'][str(seed)]=arm
            for count in (4,8):
                work=Work(check=session.check,limit=10_000_000)
                session.present('English phrases connected to discrete structure',
                    'The caller marks the clauses. Kavi learns which logical relationship the remaining words express.',
                    f'Seed {seed}: {count} original lessons; 256 whole proposals',active=2,delay=.5)
                generation,selection=reconstruct(generation,evidence[:count],evidence[:4] if count==8 else [],
                                                work,candidates=256,seed=seed,readout='exact')
                checks=Work(check=session.check)
                arm['stages'].append({'count':count,'selection':selection,
                    'teaching':evaluate(generation,evidence[:count],checks),
                    'protected':evaluate(generation,evidence[:4] if count==8 else [],checks),
                    'learning_work':dict(work.counts),'check_work':dict(checks.counts)})
            learned[seed]=generation
        session.present('English learning finished','Final sentences now test both familiar patterns and new connector formulations.',active=3)
        patterns={seq for seq,_ in evidence}
        for seed,generation in learned.items():
            arm=session.result['arms'][str(seed)]; work=Work(check=session.check)
            counts={name:{'total':0,'correct':0,'unresolved':0} for name in ('same_pattern','new_pattern')}
            behavior=unresolved=0
            for sentence,clauses,port in final:
                answer=interpret(generation.circuit,sentence,clauses,work)
                group=counts['same_pattern' if events(sentence,clauses) in patterns else 'new_pattern']
                group['total']+=1;group['correct']+=answer==FORMS[port];group['unresolved']+=answer is None
                for p,q in product((0,1),repeat=2):
                    values={'P':p,'Q':q};op,a,b=FORMS[port]
                    expected=truth[gate_events(op,(values[a],values[b]))]
                    actual=None if answer is None else evaluate_formula(logic_models[7],answer,values,work)
                    behavior+=actual==expected;unresolved+=actual is None
            arm.update(final=counts,valuation_checks={'total':32,'correct':behavior,'unresolved':unresolved,
                                                       'wrong':32-behavior-unresolved},work=dict(work.counts))
            raw=encoded(generation.record());(session.folder/f'english-{seed}.json').write_bytes(raw)
            arm['artifact']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
            session.present('English-to-logic result','Clause vocabulary is abstracted by supplied spans; new wording is scored separately.',
                f'Seed {seed}: {sum(v["correct"] for v in counts.values())}/8 interpretations; {behavior}/32 truth checks',active=3,delay=.5)
        session.result['controls']={'constant_forward_correct':sum(p==2 for _,_,p in final),'total':8,
                                    'untrained_correct':sum(interpret(PhaseConfiguration((3,5,7,11)),s,c,Work())==FORMS[p] for s,c,p in final)}
        retention={}
        for seed,model in logic_models.items():
            work=Work(check=session.check)
            retention[str(seed)]={'correct':sum(model.predict(seq,work)==p for seq,p in primitives),'total':18,'work':dict(work.counts)}
            raw=(ROOT/'runs/pcl-discrete-20260908'/f'couplings-6-seed-{seed}.json').read_bytes()
            assert hashlib.sha256(raw).hexdigest()==session.result['hard'][str(seed)]['input_sha256']
        session.result['logic_retention']=retention
        session.finish(message='Harder logic and the first English bridge are complete. Teaching has stopped.')
    except Exception as error:
        session.result['error']=str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error));raise


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-dir',type=Path,required=True);run(p.parse_args().run_dir)
