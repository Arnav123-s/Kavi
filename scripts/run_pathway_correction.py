"""Correct an underspecified arithmetic lesson, then test independent inputs."""

from dataclasses import asdict
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from kavi.procedure_core import ProcedureLibrary, Limits, describe
from kavi.procedure_search import ProgramExample, ProgramSearch
from kavi.trial_resources import memory_reading


def main():
    output = Path(sys.argv[1]).resolve()
    if not output.is_relative_to(ROOT / "runs") or output.exists():
        raise ValueError("Use a new output file below runs.")
    base = ProcedureLibrary.load(ROOT / 'experiments/library-20260907-compiled.json').closure('multiply')
    started = time.monotonic()
    limits = Limits(max_calls=3000, max_gates=100000, max_iterations=32)

    def check():
        if (output.parent / "STOP").exists():
            raise InterruptedError("Owner requested stop")
        if time.monotonic()-started > 30:
            raise InterruptedError("30-second wall limit")
        while (output.parent / "PAUSE").exists():
            if (output.parent / "STOP").exists() or time.monotonic()-started > 30:
                raise InterruptedError("Stopped while paused or wall limit")
            time.sleep(.05)

    def learn(inputs):
        search = ProgramSearch(base, max_nodes=2, max_candidates=3000, max_candidate_cases=40000,
            max_seconds=5, max_cache_entries=8000, limits=limits, check=check)
        expr = search.learn(1, [ProgramExample((x,),x*x) for x in inputs])
        return expr, asdict(search.stats)

    print('Initial lesson: 0 squared is 0; 1 squared is 1. More than one rule fits.', flush=True)
    before, before_stats = learn([0,1])
    predicted = base.execute_expr(before,(2,),limits=limits,check=check).value
    print(f'Correction question: square of 2. Kavi answered {predicted}; teacher supplies 4.',flush=True)
    after, after_stats = learn([0,1,2])
    print('A replacement rule has been found. Testing fresh inputs without further teaching.',flush=True)
    rows=[]
    for x in [3,4,5,6,7,8,9,10,11,12,17,23]:
        old=base.execute_expr(before,(x,),limits=limits,check=check).value
        new=base.execute_expr(after,(x,),limits=limits,check=check).value
        rows.append({'input':x,'target':x*x,'before':old,'after':new,
                     'before_correct':old==x*x,'after_correct':new==x*x})
    retention=[base.execute_expr(after,(x,),limits=limits,check=check).value==x*x for x in [0,1]]
    result={'protocol':'Deterministic, engineer-selected square lesson. Initial training 0,1; correction input 2 becomes training; final tests 3..12,17,23. Both candidates use unchanged supplied grammar. No semantic understanding of the word wrong is tested.',
            'source_digest':base.digest,'before':{'body':before,'description':describe(before),'stats':before_stats},
            'after':{'body':after,'description':describe(after),'stats':after_stats},
            'correction':{'input':2,'predicted':predicted,'target':4},'held_out':rows,'retention':retention,
            'seconds':time.monotonic()-started,'memory':memory_reading(),
            'scope':'Isolated re-synthesis from corrected teaching evidence; no main-library promotion, global rewrite, learned search policy or general intelligence claim.'}
    output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(f"Fresh answers: {sum(x['after_correct'] for x in rows)}/{len(rows)} correct after correction. Earlier valid examples retained: {sum(retention)}/2.",flush=True)


if __name__=='__main__':
    main()
