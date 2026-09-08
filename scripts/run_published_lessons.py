"""Frozen textbook examination, published corrections and a fresh question set."""

import argparse
import hashlib
import json
from pathlib import Path
import traceback

from kavi.composable_configurations import Configuration, Work, encoded
from kavi.published_learning import load_science, extend_kernels, learn, NEW_RELATIONS
from scripts.configuration_run_support import ROOT, Run
from scripts.run_scientific_curriculum import evaluate, practice


def item(name, givens, target, expected):
    return {'id':name,'givens':givens,'target':target,'expected':expected}


def first_exam():
    return [
        item('7-d6a',{'mass':1500.,'speed':40*.44704},'kinetic_energy',.5*1500*(40*.44704)**2),
        item('7-d6b',{'mass':1500.,'speed':80*.44704},'kinetic_energy',.5*1500*(80*.44704)**2),
        item('7-d7',{'reference_energy':13.4,'mass_factor':3.77,'slower_factor':2.34},'relative_kinetic_energy',13.4*3.77/2.34**2),
        item('7-d8a',{'mass':.8,'speed':240.},'kinetic_energy',23040.),
        item('7-d8b-energy',{'mass':80.,'speed':2.4},'kinetic_energy',230.4),
        item('7-d8b-ratio',{'first_mass':.8,'first_speed':240.,'second_mass':80.,'second_speed':2.4},'kinetic_ratio',100.),
        item('7-d9',{'mass':60.,'specific_heat':4200.,'delta_temperature':6.,'heat_power':200.,'seconds_per_minute':60.},'minutes',126.),
        item('7-d10b',{'power_factor':2.},'speed_factor',2**(1/3)),
    ]


def final_exam():
    return [
        item('7-m1',{'mass':.000110,'gravity':9.8,'height':3.10,'heat_loss':.0011},'speed',(2*(.000110*9.8*3.1-.0011)/.000110)**.5),
        item('7-m2',{'power':25.,'duration':31*24*3600.,'price_per_kWh':.15,'joules_per_kWh':3600000.},'cost',2.79),
        item('7-m3',{'mass':44.,'gravity':9.8,'height':11.,'duration':23.},'power',44*9.8*11/23),
        item('7-m4',{'mass':1150.,'gravity':9.8,'height':25.,'power':3920.},'duration',1150*9.8*25/3920),
        item('7-m5-bound-only',{'descent':35.,'rise':23.,'weight_fraction':2/3},'radius_upper_bound',72.),
    ]


def run(folder):
    session=Run(folder,'docs/PUBLISHED_LESSONS_PROTOCOL.md',[
        'kavi/published_learning.py','kavi/science_course.py','kavi/composable_configurations.py',
        'kavi/equation_kernels.py','scripts/run_published_lessons.py'])
    result=session.result
    work=lambda:Work(check=session.check)
    try:
        frozen=ROOT/'runs/scientific-curriculum-20260907/science-model.json'
        digest=lambda:hashlib.sha256(frozen.read_bytes()).hexdigest()
        assert digest()=='c65368f1eef2b6d32ede1edbeef71addd7229e302597fa0a1b5247e154bf2f17'
        model=load_science(frozen,ROOT/'experiments/library-20260907-compiled.json')
        result['initial_model_sha256']=digest()
        session.present('Different textbook: first examination','These are published questions that did not influence the saved model. Unknown answers count as failures.',active=2)
        result['first_exam']=evaluate(model,first_exam(),work())
        result['first_exam']['complete_problems']={'correct':0,'total':5,'unsupported':'Qualitative subparts and new quantitative relations'}
        assert digest()==result['initial_model_sha256']
        session.present('The examination found missing connections','Existing calculations do not automatically acquire the roles of speed, power and kinetic energy.',f"{result['first_exam']['correct']}/8 numerical targets",delay=3)
        extend_kernels(model.registry)
        records=[]
        result['teaching']=records
        # Every numerical lesson below is a worked quantity from an identified
        # published question. Intermediates and physical roles are annotated.
        kinetic=[((1500.,40*.44704),.5*1500*(40*.44704)**2),
                 ((1500.,80*.44704),.5*1500*(80*.44704)**2),
                 ((.8,240.),23040.),((80.,2.4),230.4)]
        paper_energy=.0045*9.8-.037
        lessons=[
            ('kinetic',kinetic,('science_rest_energy','half','science_work','science_ratio'),2,2,['7-d6','7-d8']),
            ('relative',[((13.4,3.77,2.34),13.4*3.77/2.34**2)],('science_work','science_mass_equivalent'),3,2,['7-d7']),
            ('ratio',[((60*4200*6.,200.),7560.),((7560.,60.),126.),((23040.,230.4),100.)],('science_ratio','science_work','science_sum'),2,2,['7-d9','7-d8b']),
            ('boat',[((2.,),2**(1/3))],('cube_root','square_root','half','double'),1,2,['7-d10b']),
            ('lift',[((80.,9.8,60.),47040.),((40.,9.8,120.),47040.),((.0045,9.8,1.),.0441)],('science_heat','science_thermal_inverse'),3,2,['7-a1','7-m6']),
            ('remaining',[((.0441,.037),paper_energy)],('science_difference','science_sum','science_ratio'),2,2,['7-m6a']),
            ('speed',[((paper_energy,.0045),(2*paper_energy/.0045)**.5),((23040.,.8),240.),((230.4,80.),2.4)],('science_ratio','double','square_root'),2,3,['7-m6b','7-d8']),
        ]
        for name,examples,ops,arity,depth,ids in lessons:
            w=work()
            graph=learn(model,'published_'+name,examples,ops,w,arity=arity,depth=depth)
            records.append({'skill':name,'source_problems':ids,'lessons':examples,'operations':ops,'depth':depth,
                            'work':w.counts,'configuration':graph.record()})
            session.present('Teach '+name.replace('_',' '),'The learner tries finite arrangements of available calculations. Only real published problem quantities supply the examples.',f"{len(examples)} worked quantities; {w.counts['candidate_proposals']} candidates",delay=1.5)
        # Bind quantities explicitly; these semantic connections are supplied.
        model.relations.extend(NEW_RELATIONS)
        result['corrected_practice']=evaluate(model,first_exam(),work())
        result['old_practice_retention']=evaluate(model,practice(),work())
        old=json.loads(frozen.read_text(encoding='utf-8'))['registry']['definitions']
        result['old_definition_retention']={'unchanged':sum(model.registry.definitions[n].record()==
             Configuration.decode(c).record() for n,c in old.items()),'total':len(old)}
        raw=encoded(model.record())
        (session.folder/'model.json').write_bytes(raw)
        result['frozen_model']={'file':'model.json','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        session.present('Freeze the corrected model','The next five questions were withheld from all fitting. One asks for a symbolic inequality, which the scalar engine cannot represent.',f"Practice {result['corrected_practice']['correct']}/8; earlier practice {result['old_practice_retention']['correct']}/13",active=1,delay=3)
        result['final_exam']=evaluate(model,final_exam(),work())
        result['final_exam']['complete_problems']={'correct':sum(r['correct'] for r in result['final_exam']['rows'][:4]),'total':5,
            'unsupported':'7-m5 requires an inequality and justification, beyond the scalar interface'}
        assert hashlib.sha256((session.folder/'model.json').read_bytes()).hexdigest()==result['frozen_model']['sha256']
        session.present('Fresh published questions finished','Corrected practice and fresh-question performance are reported separately. Unsupported answers remain visible.',f"{result['final_exam']['correct']}/5 numerical targets; {result['final_exam']['complete_problems']['correct']}/5 complete annotated problems",delay=3)
        session.finish()
    except Exception as error:
        result['error']=str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
