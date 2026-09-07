"""Finite curriculum with correction, retention and sealed final assessment."""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kavi.circuit_runtime import write_json
from kavi.foundation_curriculum import LESSONS, FRONTIER, banks, target, language_packet
from kavi.grounded_language import LanguageModel
from kavi.procedure_core import ProcedureLibrary, Procedure, Limits, describe, expression
from kavi.procedure_search import ProgramSearch, ProgramExample, SearchExhausted
from kavi.trial_resources import memory_reading


def run(run_dir,call_only=False,teacher_hints=False):
    run_dir=run_dir.resolve()
    if not run_dir.is_relative_to(ROOT/'runs') or run_dir.exists():
        raise ValueError('Choose a new directory below runs')
    run_dir.mkdir(parents=True)
    started,cpu=time.monotonic(),time.process_time()
    previous=json.loads((ROOT/'experiments/2026-09-07-pathway-growth.json').read_text(encoding='utf-8'))
    base=ProcedureLibrary.from_dict(previous['arms']['cumulative']['library'])
    limits=Limits(max_calls=5000,max_gates=200000,max_iterations=256)
    result={'schema':'kavi.foundation-curriculum.v1','state':'running','base_digest':base.digest,
            'call_only_repair':call_only,'teacher_operation_hints':teacher_hints,
            'final_input_range':[20,26] if teacher_hints else [13,19] if call_only else [6,12],
            'base':base.to_dict(),'seeds':[17,41],'arms':[],'frontier':FRONTIER,
            'protocol':'4 initial examples; disjoint correction bank, at most 2 added counterexamples; final bank never used for selection. Eight tasks, two seeds, fixed and cumulative libraries. No final-based promotion.',
            'limits':{'seconds':300,'working_set_mib':512,'search_seconds':3,'candidates':4000,'candidate_cases':100000,'nodes':3,'execution':asdict(limits)},
            'source_hashes':{name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in
                 ['kavi/foundation_curriculum.py','kavi/procedure_core.py','kavi/procedure_search.py','kavi/grounded_language.py','scripts/run_foundation_curriculum.py']}}
    last_memory=0
    finished=0
    progress=[]

    def emit(message,phase='Teaching'):
        write_json(run_dir/'status.json',{'state':'running','phase':phase,'message':message,'finished':finished,'total':32,'rows':progress})
        print(message,flush=True)
        with (run_dir/'events.txt').open('a',encoding='utf-8') as out: out.write(message+'\n')

    def check():
        nonlocal last_memory
        if (run_dir/'STOP').exists(): raise InterruptedError('Owner requested stop')
        if time.monotonic()-started>300: raise InterruptedError('Five-minute wall limit reached')
        while (run_dir/'PAUSE').exists():
            if (run_dir/'STOP').exists() or time.monotonic()-started>300:
                raise InterruptedError('Stopped or wall limit reached while paused')
            time.sleep(.05)
        if time.monotonic()-last_memory>.3:
            last_memory=time.monotonic()
            if (memory_reading().get('working_set_bytes') or 0)>512*1024**2:
                raise InterruptedError('Process working-set limit reached')

    def evaluate(lib,body,cases,oracle):
        rows=[]
        for xs in cases:
            check()
            expected=oracle(xs)
            try:
                value=lib.execute_expr(body,tuple(xs),limits=limits,check=check)
                rows.append({'inputs':xs,'expected':expected,'value':value.value,'correct':value.value==expected,
                             'calls':value.calls,'gates':value.gates,'iterations':value.iterations})
            except ValueError as error:
                partial=getattr(error,'execution',None)
                rows.append({'inputs':xs,'expected':expected,'correct':False,'error':str(error),
                             'partial':asdict(partial) if partial else None})
        return {'correct':sum(x['correct'] for x in rows),'total':len(rows),'rows':rows}

    try:
        emit('Beginning a foundation curriculum. No master-level capability is assumed.')
        for seed in (17,41):
            for arm in ('fixed','cumulative'):
                lib=ProcedureLibrary.from_dict(base.to_dict())
                row={'seed':seed,'arm':arm,'lessons':[],'initial_bytes':len(lib.encoded())}
                result['arms'].append(row)
                for lesson in LESSONS:
                    check()
                    emit(f"{lesson.title}. {'Reusing new lessons' if arm=='cumulative' else 'Using the fixed starting library'}; trial {seed}.")
                    train,correction,_=banks(lesson,seed)
                    teaching=list(train)
                    record={'name':lesson.name,'initial_inputs':train,'attempts':[],'body':None,'corrections':[]}
                    row['lessons'].append(record)
                    hints={'cube':('multiply','square'),'sum_squares':('add','square'),
                           'shifted_square':('add','square'),'scaled_square':('multiply','square'),
                           'affine':('add','multiply'),'quadratic_offset':('add','multiply','square'),
                           'cubic_sum':('add','multiply','square'),'combined_fourth':('add','fourth')}[lesson.name]
                    if lesson.name=='quadratic_offset' and 'scaled_square' in lib.procedures: hints=('add','scaled_square')
                    if lesson.name=='cubic_sum' and 'cube' in lib.procedures: hints=('add','cube')
                    if teacher_hints: record['supplied_operation_hint']=hints
                    for attempt in range(3):
                        search=ProgramSearch(lib,max_nodes=3,max_candidates=4000,max_candidate_cases=100000,
                            max_seconds=3,max_cache_entries=12000,limits=limits,check=check,
                            allowed_tags=('call',) if call_only else ('call','repeat','range'),
                            allowed_names=hints if teacher_hints else None)
                        try:
                            body=search.learn(lesson.arity,[ProgramExample(xs,target(lesson.name,xs)) for xs in teaching])
                        except SearchExhausted as error:
                            record['attempts'].append({'stats':asdict(search.stats),'failure':str(error)})
                            emit(f"Search limit reached for {lesson.title.lower()}. Keeping this result as incomplete.")
                            break
                        record['attempts'].append({'stats':asdict(search.stats),'description':describe(body)})
                        feedback=evaluate(lib,body,correction,lambda xs:target(lesson.name,xs))
                        record['attempts'][-1]['correction_bank']=feedback
                        wrong=next((x for x in feedback['rows'] if not x['correct']),None)
                        if wrong is None:
                            record['body']=body
                            record['description']=describe(body)
                            if arm=='cumulative': lib.add(Procedure(lesson.name,lesson.arity,'naturals',body=body))
                            emit(f"A configuration fits teaching and correction checks for {lesson.title.lower()}. Fresh tests come later.")
                            break
                        if attempt<2:
                            xs=tuple(wrong['inputs'])
                            teaching.append(xs)
                            record['corrections'].append(wrong)
                            emit(f"A practice answer was wrong. Teaching the corrected result and searching again ({attempt+1}/2).")
                        else:
                            record['failure']='Correction limit reached'
                    finished+=1
                    progress.append({'trial':seed,'arm':arm,'lesson':lesson.title,'status':'Provisional' if record['body'] else 'Not acquired'})
                    write_json(run_dir/'checkpoint.json',result)
                row['library']=lib.to_dict()
                row['final_bytes']=len(lib.encoded())
        # Teach language only from authored annotations. Final prompts are not supplied to teach().
        emit('Learning sentence patterns for calculations and argument structure. This is not yet passage comprehension.','Language')
        language=LanguageModel()
        teaching,language_final=language_packet()
        language.teach(teaching,check=check)
        (run_dir/'language.json').write_bytes(language.encoded())
        result['language']={'rules':len(language.rules),'bytes':len(language.encoded()),'training':language.training_stats,'final':[]}
        # No learning, repairs or selection below this boundary.
        for row in result['arms']:
            lib=ProcedureLibrary.from_dict(row['library'])
            emit(f"Fresh evaluation: {row['arm']} library, trial {row['seed']}. No answers are fed back.",'Independent tests')
            for lesson,record in zip(LESSONS,row['lessons']):
                _,_,held=banks(lesson,row['seed'])
                if call_only: held=[tuple(x+(14 if teacher_hints else 7) for x in xs) for xs in held]
                if record['body']:
                    record['final']=evaluate(lib,record['body'],held,lambda xs:target(lesson.name,xs))
                    # The same evidence is evaluated after all later learning: retained acquired skills.
                    record['retained_teaching']=evaluate(lib,record['body'],record['initial_inputs'],lambda xs:target(lesson.name,xs))
                state=next(x for x in progress if x['trial']==row['seed'] and x['arm']==row['arm'] and x['lesson']==lesson.title)
                state['status']=(f"{record['final']['correct']}/{record['final']['total']} fresh tests" if 'final' in record else 'Not acquired')
            row['retention']={}
            for name in base.procedures:
                proc=base.procedures[name]
                cases=[(a,b) for a in range(10) for b in range(10)] if proc.arity==2 else [(a,) for a in range(6,24)]
                body=('call',name,*(('arg',i) for i in range(proc.arity)))
                row['retention'][name]=evaluate(lib,body,cases,
                    lambda xs,n=name: (xs[0]+xs[1] if n=='add' else xs[0]*xs[1] if n=='multiply' else xs[0]**{'square':2,'fourth':4,'eighth':8}[n]))
        # Report every language route on every final arm; never select a library using final scores.
        for case in language_final:
            parsed=language.interpret(case['text'],check=check)
            entry={'text':case['text'],'expected_meaning':case['target'],'observed':parsed,
                   'parse_correct':parsed.get('meaning')==case['target']}
            if case['target']['kind']=='calculation':
                entry['executions']=[]
                for row in result['arms']:
                    lib=ProcedureLibrary.from_dict(row['library'])
                    response=language.answer(case['text'],lib,check=check)
                    entry['executions'].append({'seed':row['seed'],'arm':row['arm'],'state':response['state'],
                        'value':response.get('value'),'correct':response.get('value')==case['expected']})
            result['language']['final'].append(entry)
        result['language']['unseen_wording']=[{'text':t,'observed':language.interpret(t,check=check)} for t in
            ['raise eleven to the third power','explain why the narrator may be unreliable','is this argument valid because its conclusion is true']]
        # Save all versions; there is no final-score-based champion selection.
        for row in result['arms']:
            write_json(run_dir/f"library-{row['arm']}-{row['seed']}.json",row['library'])
        result['state']='completed'
    except Exception as error:
        result['state']='stopped' if isinstance(error,InterruptedError) else 'failed'
        result['error']=str(error)
    finally:
        result.update(seconds=time.monotonic()-started,cpu_seconds=time.process_time()-cpu,memory=memory_reading())
        write_json(run_dir/'results.json',result)
        write_json(run_dir/'status.json',{'state':result['state'],'phase':'Finished','finished':finished,'total':32,
            'message':'Evidence saved. Review gaps before advancing the curriculum.','rows':progress})
        print('Run '+result['state'],flush=True)
    return 0 if result['state']=='completed' else 1


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['run','live'])
    parser.add_argument('--run-dir',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='live':
        from scripts.foundation_window import show
        show(args.run_dir)
        return 0
    return run(args.run_dir)


if __name__=='__main__': raise SystemExit(main())
