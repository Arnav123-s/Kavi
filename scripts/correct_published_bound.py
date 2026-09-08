"""Teach the final failed textbook family without revising its examination score."""

import hashlib

from kavi.composable_configurations import Work, encoded
from kavi.inequality_pathway import answer, record, teach_radius_bound
from kavi.published_learning import load_science
from scripts.configuration_run_support import ROOT, Run
from scripts.run_published_lessons import final_exam
from scripts.run_scientific_curriculum import evaluate, practice


def run(folder):
    session=Run(folder,'docs/PUBLISHED_BOUND_CORRECTION.md',
        ['kavi/inequality_pathway.py','scripts/correct_published_bound.py'])
    try:
        model=load_science(ROOT/'runs/published-lessons-20260907/model.json',
            ROOT/'experiments/library-20260907-compiled.json',extended=True)
        work=Work(check=session.check)
        session.present('Teach the last textbook mistake','The published coaster problem supplies a correction. The inequality premises and proof rule are explicitly supplied.',delay=3)
        session.result['lessons']=teach_radius_bound(model.registry,work)
        session.result['learning_work']=work.counts
        w=Work(check=session.check)
        response=answer(model.registry,35.,23.,2/3,w,positive_friction=True,starts_at_rest=True,crest=True)
        session.result['corrected_problem']=response
        session.result['corrected_problem']['correct']=abs(response['upper']-72)<1e-8
        session.result['retention']=evaluate(model,final_exam()[:4]+practice(),Work(check=session.check))
        raw=encoded(record(model.registry))
        (session.folder/'model.json').write_bytes(raw)
        session.result['artifact']={'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        session.result['new_unseen_inequality_questions']=0
        session.present('Correction retained','Kavi can now calculate this restricted upper bound and show the supplied derivation. A fresh symbolic-reasoning examination has not been run.',
                        f"r < {response['upper']:.8g} m; {session.result['retention']['correct']}/17 earlier targets retained",delay=3)
        session.finish()
    except Exception as error:
        session.result['error']=str(error)
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__=='__main__':
    import argparse
    from pathlib import Path
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
