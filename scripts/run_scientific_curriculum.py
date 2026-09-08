"""Teach source-derived quantitative rules, correct practice, then freeze."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import traceback

from kavi.composable_configurations import Configuration, Work, encoded
from kavi.equation_kernels import make_registry
from kavi.procedure_core import ProcedureLibrary
from kavi.science_course import ScienceModel, RELATIONS, SPECS, consolidate, precise, teach
from scripts.configuration_run_support import ROOT, Run


def practice():
    items = [
        ('UP2-1.61',{'mass':80000.,'specific_heat':4186.,'delta_temperature':1.5},'heat',502320000.),
        ('UP2-1.62',{'mass':.05,'specific_heat':840.,'initial_temperature':22.,'final_temperature':95.},'heat',3066.),
    ]
    for suffix, c in [('a',4186.),('b',880.),('c',452.),('d',139.)]:
        items.append(('UP2-1.63'+suffix,{'heat':4186.,'mass':1.,'specific_heat':c,'initial_temperature':20.},
                      'final_temperature',20+4186/c))
    items.extend([
        ('UP2-1.64',{'force':40.,'distance':1.5,'mass':.1,'specific_heat':3500.,'full_thermalization':True},'delta_temperature',60/350),
        ('UP2-1.65-numeric',{'mass':.25,'heat':4350.,'initial_temperature':20.,'final_temperature':65.},'specific_heat',4350/(.25*45)),
    ])
    for number, mass in [(59,9.11e-31),(60,1.67e-27)]:
        givens = {'mass':mass,'light_speed':3e8,'joules_per_MeV':1.602176634e-13}
        items.extend([(f'UP3-5.{number}-J',givens,'energy',mass*9e16),
                      (f'UP3-5.{number}-MeV',givens,'energy_MeV',mass*9e16/1.602176634e-13)])
    items.append(('UP3-5.63a',{'energy':1e44,'light_speed':3e8},'mass_equivalent',1e44/9e16))
    return [{'id':i,'givens':g,'target':t,'expected':e} for i,g,t,e in items]


def evaluate(model, items, work):
    rows = []
    for item in items:
        response = model.answer(item['givens'],item['target'],work)
        rows.append({**item,'response':response,'correct':response['state']=='answered' and precise(response['value'],item['expected'])})
    return {'correct':sum(r['correct'] for r in rows),'total':len(rows),'rows':rows,'work':work.counts}


def run(folder):
    session = Run(folder,'docs/SCIENTIFIC_CURRICULUM_PROTOCOL.md',[
        'kavi/science_course.py','kavi/composable_configurations.py','kavi/equation_kernels.py',
        'scripts/run_scientific_curriculum.py','scripts/configuration_run_support.py'])
    work = lambda: Work(check=session.check)
    result = session.result
    try:
        previous = ROOT/'runs/configuration-lab-20260907/configurations.json'
        data = json.loads(previous.read_text(encoding='utf-8'))
        registry = make_registry(ProcedureLibrary.load(ROOT/'experiments/library-20260907-compiled.json'))
        assert registry.substrate == data['substrate']
        registry.definitions = {n:Configuration.decode(v) for n,v in data['definitions'].items()}
        model = ScienceModel(registry,RELATIONS)
        result['initial_artifact_sha256'] = hashlib.sha256(previous.read_bytes()).hexdigest()
        result['sources'] = [
            {'author':'Fourier','year':1822,'language':'French','role':'heat capacity and conduction'},
            {'author':'Joule','year':1850,'language':'English','role':'work converted to heat'},
            {'author':'Einstein','year':1905,'language':'German','role':'mass-energy relation'},
            {'author':'Schrödinger','year':1926,'language':'German','role':'interpretation of retained evolution kernel'},
        ]
        lessons, learning = {}, []
        result['learning'] = learning
        session.present('Original scientific works', 'The teaching notes come from French, English and German originals. Numerical examples teach configurations; quantity meanings and units are supplied.',
            boxes=['Original source','Annotated lesson','Learned calculation','Practice question'],active=1,delay=3)
        for index,(name,(arity,teacher,source)) in enumerate(SPECS.items()):
            if name in ('heat','thermal_inverse','rest_energy','mass_equivalent'):
                args = (2.,)*arity
                examples = [(args,teacher(args))]
            else:
                inputs = [(2.,3.),(5.,2.),(7.,4.),(1.,6.)] if arity==2 else [(2.,),(5.,),(7.,),(11.,)]
                examples = [(args,teacher(args)) for args in inputs]
            lessons[name] = examples
            w = work()
            graph = teach(model,name,examples,w)
            learning.append({'round':0,'name':name,'source':source,'lesson_count':len(examples),
                             'work':w.counts,'graph':graph.record()})
        result['practice_before'] = evaluate(model,practice(),work())
        before = result['practice_before']
        session.present('First textbook practice', 'The first scientific lessons are intentionally incomplete. This score shows what still needs correction.',
            f"{before['correct']}/{before['total']} numerical targets correct",delay=3)
        for index,(name,(arity,teacher,source)) in enumerate(SPECS.items()):
            rng = random.Random(95100+index)
            examples = [(tuple(rng.uniform(.25,12) for _ in range(arity))) for _ in range(16)]
            lessons[name] += [(args,teacher(args)) for args in examples]
            w = work()
            graph = teach(model,name,lessons[name],w)
            learning.append({'round':1,'name':name,'source':source,'lesson_count':len(lessons[name]),
                             'work':w.counts,'graph':graph.record()})
            session.present('Clarify '+name.replace('_',' '), 'Varied examples distinguish a reusable relationship from a coincidental answer. All earlier valid examples remain in the lesson set.',
                f"{len(lessons[name])} examples; {w.counts['candidate_proposals']} arrangements checked",delay=.8)
        result['practice_after'] = evaluate(model,practice(),work())
        after = result['practice_after']
        if after['correct'] != after['total']:
            # Correct intermediate computations only where the independent source
            # interpretation supplies their teacher; keep the failed pass intact.
            touched = set()
            for row in after['rows']:
                if not row['correct']:
                    for step in row['response']['trace']:
                        name = step['configuration'].removeprefix('science_')
                        if name in SPECS:
                            args = tuple(step['args'])
                            lessons[name].append((args,SPECS[name][1](args)))
                            touched.add(name)
            for name in sorted(touched):
                w = work()
                graph = teach(model,name,lessons[name],w)
                learning.append({'round':2,'name':name,'lesson_count':len(lessons[name]),'work':w.counts,'graph':graph.record()})
            result['practice_repair'] = evaluate(model,practice(),work())
            after = result['practice_repair']
        session.present('Repeat the corrected practice', 'Practice may influence learning. The final textbook will be different and will not be used to change the model.',
            f"{after['correct']}/{after['total']} numerical targets correct",delay=3)

        result['transfer'] = {}
        tests = {}
        for index,(name,(arity,teacher,source)) in enumerate(SPECS.items()):
            rng = random.Random(95200+index)
            cases = [tuple(rng.uniform(20,1000) for _ in range(arity)) for _ in range(128)]
            tests[name] = [(args,teacher(args)) for args in cases]
            w = work()
            correct = sum(precise(registry.execute('science_'+name,args,w),expected) for args,expected in tests[name])
            result['transfer'][name] = {'correct':correct,'total':128,'work':w.counts}
        before_bytes = len(encoded(model.record()))
        result['structural_sharing'] = consolidate(model)
        after_bytes = len(encoded(model.record()))
        rw = work()
        retained = sum(precise(registry.execute('science_'+name,args,rw),expected) for name,cases in tests.items() for args,expected in cases)
        result['after_sharing'] = {'correct':retained,'total':1152,'work':rw.counts,
                                  'bytes_before':before_bytes,'bytes_after':after_bytes}
        result['practice_after_sharing'] = evaluate(model,practice(),work())
        ow = work()
        old_count = 0
        for a in range(16):
            for b in range(16):
                old_count += registry.execute('middle',(a,b),ow) == (a+b)**2
        result['old_composition_retention'] = {'correct':old_count,'total':256,'work':ow.counts}
        assert old_count == 256
        raw = encoded(model.record())
        (session.folder/'science-model.json').write_bytes(raw)
        result['frozen_model'] = {'file':'science-model.json','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        (session.folder/'lessons.json').write_text(json.dumps(lessons,indent=2),encoding='utf-8')
        (session.folder/'synthetic-examination.json').write_text(json.dumps(tests,indent=2),encoding='utf-8')
        result['textbook_exam_opened'] = False
        session.present('Freeze before the independent textbook', 'Training has finished. The saved fingerprint will be checked before and after the separate textbook examination.',
            f'{retained}/1152 new numerical inputs; {old_count}/256 earlier compositions',
            boxes=['Corrected lessons','Frozen model','Different textbook','No further teaching'],active=1,delay=3)
        session.finish()
    except Exception as error:
        result['error'] = str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
