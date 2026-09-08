"""Teach relevance and reusable English routes from human-written problems."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import traceback
import xml.etree.ElementTree as ET

from kavi.composable_configurations import Work,encoded
from kavi.english_configurations import EnglishReasoner,signature
from kavi.human_math_sources import asdiv,gsm,EXCLUDED
from kavi.published_english import teach
from kavi.published_learning import load_science
from scripts.configuration_run_support import ROOT,Run
from scripts.run_english_configurations import dataset as initial_dataset
from scripts.run_published_lessons import final_exam
from scripts.run_scientific_curriculum import practice,evaluate as science_evaluate


def evaluate(model,rows,registry,session):
    results=[];counts=Counter()
    for row in rows:
        session.check()
        work=Work(check=session.check,limit=1_000_000)
        try:
            answer=model.answer(row['text'],registry,work)
            correct=math.isclose(answer['value'],row['expected'],rel_tol=1e-8,abs_tol=1e-9)
            results.append({'id':row['id'],'correct':correct,'value':answer['value'],
                            'expected':row['expected'],'expression':answer['expression'],
                            'reused_program':answer.get('reused_program'),'algebra':row.get('algebra',False)})
        except (ValueError,ZeroDivisionError,OverflowError,InterruptedError) as error:
            if isinstance(error,InterruptedError) and str(error)!='Configuration work budget exhausted':
                raise
            results.append({'id':row['id'],'correct':False,'error':str(error),'algebra':row.get('algebra',False)})
        counts.update(work.counts)
    return {'correct':sum(r['correct'] for r in results),'total':len(results),'work':dict(counts),'rows':results}


def subsets(measurement,rows):
    by_id={r['id']:r for r in measurement['rows']}
    selected={
        'algebra':[r['id'] for r in rows if r.get('algebra')],
        'irrelevant_quantities':[r['id'] for r in rows if len(r['indices'])<len(r['input'].numbers)],
        'more_than_five_active':[r['id'] for r in rows if len(r['indices'])>5],
    }
    return {name:{'correct':sum(by_id[pid]['correct'] for pid in ids),'total':len(ids)} for name,ids in selected.items()}


def run(folder):
    session=Run(folder,'docs/PUBLISHED_ENGLISH_REPAIR_PROTOCOL.md',[
        'kavi/english_configurations.py','kavi/published_english.py',
        'kavi/human_math_sources.py','scripts/run_published_english.py'])
    try:
        as_rows,as_errors,as_excluded=asdiv()
        # Preserve all previously admitted source lessons if the new annotation
        # normalizer cannot represent them. Their published formulas are unchanged.
        before,_,_=initial_dataset()
        known={r['id'] for r in as_rows}
        recovered=[]
        for row in before:
            if row['id'] not in known:
                recovered.append(row['id'])
                as_rows.append({**row,'indices':list(range(len(row['input'].numbers))),'algebra':False})
        as_errors=[r for r in as_errors if r['id'] not in set(recovered)]
        gm_rows,gm_errors=gsm('train')
        forbidden=set()
        for p in ET.fromstring((ROOT/'private/english-reasoning-20260907/ASDiv.xml').read_bytes()).findall('.//Problem'):
            if any(d in p.attrib['Source'] for d in EXCLUDED):continue
            sig=signature(p.findtext('Body')+' '+p.findtext('Question'))
            if int(hashlib.sha256(sig.encode()).hexdigest()[:8],16)%10>=8:
                forbidden.add(sig)
        overlaps=[r['id'] for r in gm_rows if r['signature'] in forbidden]
        gm_rows=[r for r in gm_rows if r['id'] not in set(overlaps)]
        rows=as_rows+gm_rows
        parts={name:[r for r in rows if r['partition']==name] for name in ('train','development','test')}
        # The two sources use different hash cutoffs. Give training precedence
        # only for signatures duplicated between their non-final portions.
        train_sigs={r['signature'] for r in parts['train']}
        dev_overlap=[r['id'] for r in parts['development'] if r['signature'] in train_sigs]
        parts['development']=[r for r in parts['development'] if r['id'] not in set(dev_overlap)]
        assert not train_sigs & {r['signature'] for r in parts['test']}
        session.result['admission']={
            'asdiv_supported':len(as_rows),'asdiv_unsupported':len(as_errors),'asdiv_source_excluded':len(as_excluded),
            'gsm_training_file_supported':len(gm_rows),'gsm_training_file_unsupported':len(gm_errors),
            'cross_source_final_overlap_excluded':overlaps,'development_overlap_excluded':dev_overlap,
            'recovered_previous_admissions':recovered,
            'parts':{k:len(v) for k,v in parts.items()},
            'unsupported_reasons':dict(Counter(r['reason'] for r in as_errors+gm_errors))}
        session.result['partitions']={name:[{'id':r['id'],'input_sha256':hashlib.sha256(r['text'].encode()).hexdigest(),
            'signature_sha256':hashlib.sha256(r['signature'].encode()).hexdigest()} for r in group] for name,group in parts.items()}
        model=load_science(ROOT/'experiments/science-20260907-published-model.json',
                           ROOT/'experiments/library-20260907-compiled.json',extended=True)
        baseline=EnglishReasoner.load(ROOT/'runs/english-configurations-20260907/model.json')
        session.present('Teach relevance and reusable computations',
            'Real published questions teach which numbers matter and which existing calculation applies. Simple algebra annotations are included.',
            f"{len(parts['train'])} teaching questions; {len(parts['development'])} development questions",
            boxes=['Question','Learned relevance','Existing configuration','New construction if needed'],active=1,delay=3)
        candidates=[];development=[]
        for depth in (8,12,16):
            work=Work(check=session.check,limit=100_000_000)
            reasoner=teach(parts['train'],work,depth=depth)
            measured=evaluate(reasoner,parts['development'],model.registry,session)
            candidates.append(reasoner)
            development.append({'depth':depth,'learning_work':dict(work.counts),'bytes':len(encoded(reasoner.record())),
                                'program_definitions':len(reasoner.programs),'result':measured})
            session.result['development']=development
            session.present('Rebuild and compare the English configuration',
                'Each candidate is rebuilt from the published teaching evidence. Only development answers choose the candidate.',
                f"Depth {depth}: {measured['correct']}/{measured['total']}; {measured['work'].get('reused_program_answers',0)} direct program uses",delay=2)
        selected=max(range(len(candidates)),key=lambda i:(development[i]['result']['correct'],-development[i]['bytes']))
        reasoner=candidates[selected]
        raw=encoded(reasoner.record());(session.folder/'model.json').write_bytes(raw)
        session.result['artifact']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                                    'program_definitions':len(reasoner.programs)}
        session.result['selected_depth']=development[selected]['depth']
        session.present('Freeze before independent questions',
            'The official GSM8K test file is opened only after this model is saved. Its answers cannot select the model.',
            f"{len(raw):,} configuration bytes; {len(reasoner.programs)} reusable programs",active=2,delay=3)
        fresh,fresh_errors=gsm('test')
        test_overlap=[r['id'] for r in fresh if r['signature'] in train_sigs]
        fresh=[r for r in fresh if r['id'] not in set(test_overlap)]
        session.result['independent_admission']={'supported':len(fresh),'unsupported':len(fresh_errors),
            'training_overlap_excluded':test_overlap,
            'full_denominator':len(fresh)+len(fresh_errors),
            'reasons':dict(Counter(r['reason'] for r in fresh_errors))}
        session.result['independent_test']=evaluate(reasoner,fresh,model.registry,session)
        session.result['independent_subsets']=subsets(session.result['independent_test'],fresh)
        session.result['initial_model_independent_test']=evaluate(baseline,fresh,model.registry,session)
        selector=reasoner.program_router
        reasoner.program_router=None
        session.result['composition_every_time']=evaluate(reasoner,fresh,model.registry,session)
        reasoner.program_router=selector
        session.result['asdiv_followup']=evaluate(reasoner,parts['test'],model.registry,session)
        session.result['asdiv_subsets']=subsets(session.result['asdiv_followup'],parts['test'])
        session.result['earlier_science_retention']=science_evaluate(model,final_exam()[:4]+practice(),Work(check=session.check))
        assert session.result['earlier_science_retention']['correct']==17
        assert hashlib.sha256((session.folder/'model.json').read_bytes()).hexdigest()==session.result['artifact']['sha256']
        score=session.result['independent_test']
        session.present('Independent questions completed',
            'These scores measure English calculation transfer. They do not establish general language or graduate-level subject understanding.',
            f"{score['correct']}/{score['total']} supported fresh questions; {score['correct']}/{session.result['independent_admission']['full_denominator']} including unsupported types",
            active=3,delay=3)
        session.finish()
    except Exception as error:
        session.result['error']=str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
