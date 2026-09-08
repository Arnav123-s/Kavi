"""Teach published English in small increments with finite retention checks."""

import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path
import traceback
import unicodedata

from kavi.composable_configurations import Work,encoded
from kavi.english_configurations import ConnectionTree,WORD,features
from kavi.human_math_sources import gsm
from kavi.published_learning import load_science
from kavi.streaming_english import StreamingEnglishReasoner
from scripts.configuration_run_support import ROOT,Run
from scripts.run_english_configurations import dataset


def evaluate(reasoner,rows,registry,session):
    counts=Counter();answers=[]
    for row in rows:
        work=Work(check=session.check,limit=1_000_000)
        try:
            result=reasoner.answer(row['text'],registry,work)
            answers.append({'id':row['id'],'correct':math.isclose(result['value'],row['expected'],rel_tol=1e-8,abs_tol=1e-9),
                            'value':result['value'],'program':result['program'],
                            'input_activity':result['input_activity']})
        except (ValueError,ZeroDivisionError,OverflowError,InterruptedError) as error:
            if isinstance(error,InterruptedError) and str(error)!='Configuration work budget exhausted':raise
            answers.append({'id':row['id'],'correct':False,'error':str(error)})
        counts.update(work.counts)
    return {'correct':sum(r['correct'] for r in answers),'total':len(answers),'rows':answers,'work':dict(counts)}


def ordered(rows):
    return sorted(rows,key=lambda r:(hashlib.sha256(r['signature'].encode()).hexdigest(),r['id']))


def run(folder):
    session=Run(folder,'docs/INCREMENTAL_ENGLISH_PROTOCOL.md',[
        'kavi/english_configurations.py','kavi/streaming_english.py','kavi/signal_configurations.py',
        'kavi/human_math_sources.py','scripts/run_incremental_english.py'])
    try:
        rows,excluded,unsupported=dataset()
        parts={p:[r for r in rows if r['partition']==p] for p in ('train','development','test')}
        forbidden={r['signature'] for r in parts['test']}
        # Include the earlier unsupported final signatures in the exclusion.
        from kavi.english_configurations import signature
        from kavi.human_math_sources import EXCLUDED
        import xml.etree.ElementTree as ET
        for p in ET.fromstring((ROOT/'private/english-reasoning-20260907/ASDiv.xml').read_bytes()).findall('.//Problem'):
            if any(d in p.attrib['Source'] for d in EXCLUDED):continue
            sig=signature(p.findtext('Body')+' '+p.findtext('Question'))
            if int(hashlib.sha256(sig.encode()).hexdigest()[:8],16)%10>=8:forbidden.add(sig)
        new,errors=gsm('train')
        eligible=[r for r in new if r['signature'] not in forbidden
                  and len(r['indices'])==len(r['input'].numbers) and len(r['indices'])<=5]
        simple=ordered([r for r in eligible if r['partition']=='train' and len(r['indices'])==2])
        two_step=ordered([r for r in eligible if r['partition']=='train' and len(r['indices'])==3])
        batches=[simple,two_step[:80],two_step[80:160]]
        teaching=list(parts['train'])
        training_signatures={r['signature'] for r in teaching+sum(batches,[])}
        development=parts['development']+ordered([r for r in eligible
            if r['partition']=='development' and len(r['indices'])==3
            and r['signature'] not in training_signatures])[:80]
        assert not training_signatures & {r['signature'] for r in development}
        registry=load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json',extended=True).registry
        current=StreamingEnglishReasoner.load(ROOT/'experiments/english-20260907-initial-model.json')
        verification=Work(check=session.check)
        pairs=0
        for row in parts['train']+parts['development']:
            state=current.begin(verification)
            for token in WORD.findall(unicodedata.normalize('NFKC',row['text']).replace('’',"'")):state.consume(token)
            for i,j in itertools.combinations(range(len(state.numbers)),2):
                assert state.features(i,j)==features(row['input'],i,j)&current.vocabulary,row['id']
                pairs+=1
        session.result['representation_check']={'questions':len(parts['train'])+len(parts['development']),
            'quantity_pairs':pairs,'all_acquired_features_agree':True,'work':verification.counts}
        session.result['source_admission']={'eligible_gsm':len(eligible),'batch_sizes':[len(b) for b in batches],
            'initial_teaching':len(teaching),'development':len(development),
            'asdiv_source_excluded':len(excluded),'gsm_annotation_failures':len(errors)}
        session.result['partitions']={'initial_training':[r['id'] for r in teaching],
            'batches':[[r['id'] for r in b] for b in batches],
            'development':[r['id'] for r in development],'followup':[r['id'] for r in parts['test']]}
        session.present('Current input activity verified',
            'Words update temporary features and learned connections. The earlier teaching and development inputs produce the same acquired predicates.',
            f'{pairs} quantity-pair feature checks passed',
            boxes=['Incoming words','Held activity','Learned route','Completed calculation'],active=1,delay=2)
        previous=evaluate(current,teaching,registry,session)
        current_dev=evaluate(current,development,registry,session)
        session.result['initial_training']=previous
        session.result['initial_development']=current_dev
        stages=[]
        for stage,batch in enumerate(batches,1):
            if not batch:continue
            required={r['id'] for r in previous['rows'] if r['correct']}
            teaching+=batch
            examples=[(features(r['input'],i,j),label) for r in teaching for (i,j),label in r['labels'].items()]
            baseline=evaluate(current,teaching,registry,session)
            new_ids={r['id'] for r in batch}
            before_correction=[r for r in baseline['rows'] if r['id'] in new_ids]
            choices=[(current,current_dev,baseline,len(encoded(current.record())),'keep')]
            candidates=[]
            session.present('Teach the next foundation increment',
                'Published worked examples correct arithmetic relationships. Every candidate must retain earlier correct teaching answers.',
                f'Increment {stage}: {len(batch)} added; {len(teaching)} total teaching questions',active=2,delay=2)
            for depth in (12,24,48):
                work=Work(check=session.check,limit=60_000_000)
                candidate=StreamingEnglishReasoner(ConnectionTree().teach(examples,work,depth=depth,min_leaf=1))
                measured=evaluate(candidate,teaching,registry,session)
                by_id={r['id']:r['correct'] for r in measured['rows']}
                lost=sorted(pid for pid in required if not by_id.get(pid,False))
                dev=evaluate(candidate,development,registry,session)
                size=len(encoded(candidate.record()))
                candidates.append({'depth':depth,'bytes':size,'nodes':len(candidate.router.nodes),
                    'learning_work':work.counts,'training':measured,'development':dev,
                    'earlier_correct_obligations':len(required),'regressions':lost,'admissible':not lost})
                if not lost:choices.append((candidate,dev,measured,size,depth))
                session.present('Check the rebuilt configuration',
                    'Corrections are checked against earlier valid answers before this candidate can replace the current configuration.',
                    f'Depth {depth}: {dev["correct"]}/{dev["total"]} development; {len(lost)} earlier teaching losses',active=2,delay=.5)
            current,current_dev,previous,size,selected=max(choices,key=lambda c:(c[1]['correct'],c[2]['correct'],-c[3]))
            stages.append({'stage':stage,'added':len(batch),'teaching_total':len(teaching),
                'new_questions_before_correction':before_correction,'precorrection_work':baseline['work'],
                'candidates':candidates,'selected':selected,'selected_bytes':size,
                'selected_training_correct':previous['correct'],
                'selected_development_correct':current_dev['correct'],
                'earlier_correct_obligations':len(required),'selected_regressions':0})
            session.result['stages']=stages
            session.save()
        raw=encoded(current.record());(session.folder/'model.json').write_bytes(raw)
        session.result['artifact']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        session.result['selected_development']=current_dev
        session.result['foundation_development_threshold_met']=current_dev['correct']>=.9*current_dev['total']
        session.present('Freeze the incrementally taught configuration',
            'The next check revisits the earlier test bank. Its answers did not choose a candidate in this course.',
            f'{len(raw):,} bytes; {current_dev["correct"]}/{current_dev["total"]} development',active=3,delay=2)
        final=evaluate(current,parts['test'],registry,session)
        old=json.loads((ROOT/'experiments/2026-09-07-published-english.json').read_text(encoding='utf-8'))['initial']['test']['rows']
        a={r['id']:r['correct'] for r in old};b={r['id']:r['correct'] for r in final['rows']}
        session.result['followup']=final
        session.result['followup_retention']={'earlier_correct':sum(a.values()),'current_correct':sum(b.values()),
            'lost':[pid for pid in a if a[pid] and not b[pid]],'gained':[pid for pid in a if not a[pid] and b[pid]],
            'same_questions':len(a)}
        demo=Work(check=session.check)
        def observe(event):
            if event['tokens_consumed']%4:return
            names={'+':'addition','-':'subtraction','r-':'reversed subtraction','*':'multiplication','/':'division','r/':'reversed division'}
            route=next(iter(event['active_routes'].values()),None)
            message='Input is still arriving. No answer has been released.'
            if route:message+=' The current first-pair route is '+names[route]+'.'
            session.present('Reading: '+event['token'],message,active=1,delay=.08)
        response=current.answer(teaching[0]['text'],registry,demo,observe=observe)
        session.result['demonstration']={'id':teaching[0]['id'],'value':response['value'],
            'input_activity':response['input_activity'],'signal_activity':response['signal_activity'],'work':demo.counts}
        session.present('Foundation course completed',
            'Later subject sources remain reserved. This result does not establish college, graduate or research-level mastery.',
            f'{final["correct"]}/{final["total"]} on the earlier test bank; {len(session.result["followup_retention"]["lost"])} earlier correct answers lost',active=3,delay=3)
        session.finish()
    except Exception as error:
        session.result['error']=str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
