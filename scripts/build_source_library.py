"""Acquire an explicitly curated corpus of actual institutional source passages."""

import argparse
import hashlib
import json
from pathlib import Path
import traceback
from urllib.request import Request, urlopen

from kavi.source_library import PassageHTML
from scripts.configuration_run_support import ROOT, Run


def sources():
    rows=[]
    def add(name,title,url,author,language='English',translator=None):
        rows.append(dict(id=name,title=title,url=url,author=author,language=language,translator=translator))
    for path,title in [('universe/black-holes/','Black holes'),('universe/stars/','Stars'),
            ('universe/overview/forces/','Fundamental forces and gravity'),('universe/overview/dark-matter-dark-energy/','Dark matter and dark energy'),
            ('sun/facts/','Sun facts'),('earth/facts/','Earth facts'),('moon/facts/','Moon facts'),
            ('mars/facts/','Mars facts'),('solar-system/planets/','The planets'),
            ('climate-change/causes/','Causes of climate change')]:
        add('nasa-'+path.split('/')[0]+'-'+str(len(rows)),title,'https://science.nasa.gov/'+path,'NASA')
    for path,title in [('Deoxyribonucleic-Acid','DNA'),('Gene','Gene'),('Genome','Genome'),
            ('Mutation','Mutation'),('Evolution','Evolution'),('Chromosome','Chromosome'),
            ('RNA-Ribonucleic-Acid','RNA'),('Protein','Protein'),('Cell','Cell')]:
        add('nhgri-'+path.lower(),title,'https://www.genome.gov/genetics-glossary/'+path,'National Human Genome Research Institute')
    for path,title in [('what-earthquake-and-what-causes-them-happen','What causes earthquakes?'),
            ('can-you-predict-earthquakes','Can earthquakes be predicted?'),
            ('what-are-plate-tectonics','Plate tectonics')]:
        add('usgs-'+str(len(rows)),title,'https://www.usgs.gov/faqs/'+path,'U.S. Geological Survey')
    add('usgs-water','The water cycle','https://www.usgs.gov/special-topics/water-science-school/science/water-cycle','U.S. Geological Survey')
    add('declaration','Declaration of Independence','https://www.archives.gov/founding-docs/declaration-transcript','Continental Congress; National Archives edition')
    add('plato-apology','Apology: Socrates and wisdom','https://classics.mit.edu/Plato/apology.html','Plato','English','Benjamin Jowett')
    add('aristotle-ethics','Nicomachean Ethics, Book I','https://classics.mit.edu/Aristotle/nicomachaen.1.i.html','Aristotle','English','W. D. Ross')
    add('python-intro','Introduction to Python','https://docs.python.org/3/tutorial/introduction.html','Python Software Foundation')
    add('python-control','Python control flow and functions','https://docs.python.org/3/tutorial/controlflow.html','Python Software Foundation')
    add('python-data','Python data structures','https://docs.python.org/3/tutorial/datastructures.html','Python Software Foundation')
    return rows


def run(folder):
    session=Run(folder,'docs/PUBLISHED_LESSONS_PROTOCOL.md',['kavi/source_library.py','scripts/build_source_library.py'])
    records=[]
    failures=[]
    try:
        for source in sources():
            session.present('Read '+source['title'],'Real source paragraphs are being indexed for cited answers. This is document retrieval, separate from learning calculation rules.',active=1,delay=.1)
            try:
                request=Request(source['url'],headers={'User-Agent':'Kavi source library/1.0 (educational research)'})
                with urlopen(request,timeout=12) as response:
                    raw=response.read(4_000_001)
                    encoding=response.headers.get_content_charset() or 'utf-8'
                    final_url=response.url
                if len(raw)>4_000_000:
                    raise ValueError('Source exceeds the four MB response budget')
                parser=PassageHTML()
                parser.feed(raw.decode(encoding,errors='replace'))
                passages=parser.passages()
                if len(passages)<2:
                    raise ValueError('Insufficient expository passages after extraction')
                (session.folder/(source['id']+'.html')).write_bytes(raw)
                record=dict(source,final_url=final_url,retrieved='2026-09-07',raw_bytes=len(raw),
                            sha256=hashlib.sha256(raw).hexdigest(),passages=passages)
                records.append(record)
                session.present('Added '+source['title'],'The original wording and source address are retained locally.',f'{len(passages)} source passages',delay=.1)
            except Exception as error:
                if isinstance(error,InterruptedError):
                    raise
                failures.append(dict(source,error=str(error)))
                session.present('Source unavailable','The retrieval failure is recorded; no replacement text is invented.',source['title'],delay=.1)
        raw=json.dumps({'format':'kavi-source-library-1','sources':records},ensure_ascii=False,separators=(',',':')).encode('utf-8')
        (session.folder/'library.json').write_bytes(raw)
        session.result.update(sources=[{k:v for k,v in r.items() if k!='passages'}|{'passages':len(r['passages'])} for r in records],
             failures=failures,source_count=len(records),passage_count=sum(len(r['passages']) for r in records),
             library_bytes=len(raw),library_sha256=hashlib.sha256(raw).hexdigest())
        session.finish(message='Source reading is complete. The conversation library is ready.')
    except Exception as error:
        session.result['error']=str(error)
        (session.folder/'failure.txt').write_text(traceback.format_exc(),encoding='utf-8')
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
