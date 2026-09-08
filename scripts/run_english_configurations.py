"""Teach language-conditioned program construction on published English problems."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import traceback
import xml.etree.ElementTree as ET

from kavi.composable_configurations import Work,encoded
from kavi.english_configurations import (ConnectionTree,EnglishReasoner,annotation,features,signature,numeric,OPS,compose,read_input)
from kavi.published_learning import load_science
from scripts.configuration_run_support import ROOT,Run


EXCLUDED=('commoncoresheets.com','dadsworksheets.com','math-aids.com','mathworksheets4kids.com')


def dataset():
    path=ROOT/'private/english-reasoning-20260907/ASDiv.xml'
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!='ef8904068482919ac48c8eeaaf6df344b8a308ba66d048c2d4d87eab82dc4929':
        raise ValueError('The admitted corpus changed')
    accepted=[];excluded=[];unsupported=[]
    for problem in ET.fromstring(raw).findall('.//Problem'):
        source=problem.attrib['Source'];pid=problem.attrib['ID']
        if any(domain in source for domain in EXCLUDED):
            excluded.append(pid);continue
        text=(problem.findtext('Body')+' '+problem.findtext('Question')).strip()
        formula=problem.findtext('Formula')
        sig=signature(text)
        bucket=int(hashlib.sha256(sig.encode()).hexdigest()[:8],16)%10
        partition='train' if bucket<6 else 'development' if bucket<8 else 'test'
        try:
            inp,program,labels=annotation(text,formula)
            expected=numeric(program,inp.numbers)
            # Independently require the numeric answer field to agree. This
            # check admits annotations; inference never receives that field.
            import re
            match=re.match(r'\s*(-?\d+(?:,\d{3})*(?:\.\d+)?)',problem.findtext('Answer'))
            if match is None:raise ValueError('non-scalar-answer')
            answer=float(match[1].replace(',',''))
            import math
            if not math.isclose(expected,answer,rel_tol=1e-6,abs_tol=1e-7):raise ValueError('annotation-answer-disagreement-or-fraction')
            accepted.append({'id':pid,'source':source,'text':text,'signature':sig,'partition':partition,
                'input':inp,'program':program,'labels':labels,'expected':expected})
        except (ValueError,SyntaxError,TypeError,ZeroDivisionError,OverflowError) as error:
            unsupported.append({'id':pid,'partition':partition,'reason':str(error)})
    return accepted,excluded,unsupported


def evaluate(reasoner,rows,registry,work,*,beam=6):
    import math
    results=[]
    for row in rows:
        try:
            response=reasoner.answer(row['text'],registry,work,beam=beam)
            correct=math.isclose(response['value'],row['expected'],rel_tol=1e-8,abs_tol=1e-9)
            results.append({'id':row['id'],'correct':correct,'expected':row['expected'],'value':response['value'],
                'expression':response['expression'],'program':response['program'],
                'alternative':response['alternative']})
        except (ValueError,ZeroDivisionError,OverflowError) as error:
            results.append({'id':row['id'],'correct':False,'error':str(error)})
    return {'correct':sum(r['correct'] for r in results),'total':len(results),'work':dict(work.counts),'rows':results}


def run(folder):
    session=Run(folder,'docs/ENGLISH_CONFIGURATION_PROTOCOL.md',[
        'kavi/english_configurations.py','scripts/run_english_configurations.py'])
    try:
        rows,excluded,unsupported=dataset()
        parts={name:[r for r in rows if r['partition']==name] for name in ('train','development','test')}
        session.result['dataset']={'total':2305,'excluded_sources':len(excluded),'supported':len(rows),
            'unsupported':len(unsupported),'unsupported_reasons':dict(Counter(r['reason'] for r in unsupported)),
            'partitions':{k:len(v) for k,v in parts.items()},'unsupported_partitions':dict(Counter(r['partition'] for r in unsupported))}
        manifest={name:[{'id':r['id'],'input_sha256':hashlib.sha256(r['text'].encode()).hexdigest(),
            'signature_sha256':hashlib.sha256(r['signature'].encode()).hexdigest()} for r in group] for name,group in parts.items()}
        session.result['partitions']=manifest
        for a,b in (('train','development'),('train','test'),('development','test')):
            assert not set(r['signature'] for r in parts[a])&set(r['signature'] for r in parts[b])
        (session.folder/'admission.json').write_text(json.dumps({'excluded':excluded,'unsupported':unsupported},indent=2),encoding='utf-8')
        registry=load_science(ROOT/'runs/published-lessons-20260907/model.json',ROOT/'experiments/library-20260907-compiled.json',extended=True).registry
        examples=[(features(r['input'],i,j),label) for r in parts['train'] for (i,j),label in r['labels'].items()]
        session.present('Learn English connections','Each published question teaches which quantities belong together and which operation connects them. The saved model will contain only routing structure.',
            f"{len(parts['train'])} teaching questions; {len(examples)} annotated connections",boxes=['English input','Active connections','Candidate configurations','Computed answer'],active=1,delay=3)
        models=[];development=[]
        for depth in (8,12,16):
            training=Work(check=session.check,limit=20000000)
            model=EnglishReasoner(ConnectionTree().teach(examples,training,depth=depth))
            w=Work(check=session.check,limit=20000000)
            measured=evaluate(model,parts['development'],registry,w)
            development.append({'depth':depth,'nodes':len(model.router.nodes),'bytes':len(encoded(model.record())),
                'training_work':training.counts,'result':measured})
            models.append(model)
            session.present('Compare learned configurations','Only the development questions choose the configuration size. The final questions remain outside selection.',
                f"Depth {depth}: {measured['correct']}/{measured['total']} development answers",delay=2)
        chosen=max(range(3),key=lambda i:(development[i]['result']['correct'],-development[i]['bytes']))
        model=models[chosen]
        session.result.update(development=development,selected_depth=development[chosen]['depth'])
        raw=encoded(model.record());(session.folder/'model.json').write_bytes(raw)
        session.result['artifact']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        session.present('Freeze the English configuration','Teaching examples and worked answers are not inside this artifact. New questions must activate connections and construct their own calculation.',
            f"{len(model.router.nodes)} nodes; {len(raw):,} bytes",active=2,delay=3)
        session.result['training_score']=evaluate(model,parts['train'],registry,Work(check=session.check,limit=20000000))
        session.result['test']=evaluate(model,parts['test'],registry,Work(check=session.check,limit=20000000))
        session.result['narrow_search']=evaluate(model,parts['test'],registry,Work(check=session.check,limit=20000000),beam=1)
        blind=EnglishReasoner(ConnectionTree([{'ports':list(OPS)}]))
        session.result['language_blind']=evaluate(blind,parts['test'],registry,Work(check=session.check,limit=20000000))
        train_programs={json.dumps(r['program']) for r in parts['train']}
        novel={r['id'] for r in parts['test'] if json.dumps(r['program']) not in train_programs}
        session.result['unseen_program_shapes']={'total':len(novel),'correct':sum(r['correct'] for r in session.result['test']['rows'] if r['id'] in novel)}
        assert hashlib.sha256((session.folder/'model.json').read_bytes()).hexdigest()==session.result['artifact']['sha256']
        session.result['retained_fields']=sorted(set(key for n in model.router.nodes for key in n))
        assert not ({'counts','examples','answers','questions'}&set(session.result['retained_fields']))
        answer=session.result['test']
        session.present('Unseen English questions completed','The reported score counts the first computed answer. Wrong interpretations and unsupported problem types remain in the report.',
            f"{answer['correct']}/{answer['total']} supported test questions; language-blind {session.result['language_blind']['correct']}/{answer['total']}",active=3,delay=3)
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
