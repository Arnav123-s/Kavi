"""Build an audited source index from downloaded bodies and inspected passages."""

import hashlib
import json
from pathlib import Path
import re

from kavi.source_curation import curate_html, deduplicate
from scripts.configuration_run_support import ROOT, Run


def main():
    session=Run(ROOT/'runs/curated-sources-20260907','docs/PUBLISHED_LESSONS_PROTOCOL.md',
                ['kavi/source_curation.py','kavi/source_library.py','scripts/curate_conversation_sources.py'])
    previous=ROOT/'runs/source-library-20260907'
    original=json.loads((previous/'library.json').read_text(encoding='utf-8'))['sources']
    records=[]
    rejected=[]
    for source in original:
        try:
            passages=curate_html((previous/(source['id']+'.html')).read_bytes(),source)
            if not passages: raise ValueError('No eligible source prose')
            records.append({**source,'passages':passages})
        except Exception as error:
            rejected.append({'id':source['id'],'error':str(error)})
    for source in json.loads((ROOT/'private/inspected-source-passages-20260907.json').read_text(encoding='utf-8')):
        raw='\n'.join(source['paragraphs']).encode('utf-8')
        passages=[{'heading':source['title'],'text':s} for p in source['paragraphs']
                  for s in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])',p) if len(s)>30]
        records.append({k:v for k,v in source.items() if k!='paragraphs'}|
                       {'passages':passages,'sha256':hashlib.sha256(raw).hexdigest(),'selected_text_bytes':len(raw)})
    discarded=deduplicate(records)
    raw=json.dumps({'format':'kavi-source-library-1','sources':records},ensure_ascii=False,separators=(',',':')).encode('utf-8')
    (session.folder/'library.json').write_bytes(raw)
    manifest=[{k:v for k,v in s.items() if k!='passages'}|{'passages':len(s['passages'])} for s in records]
    session.result.update(source_count=len(records),passage_count=sum(len(s['passages']) for s in records),
        sources=manifest,rejected=rejected,duplicated_site_passages_removed=discarded,
        library_bytes=len(raw),library_sha256=hashlib.sha256(raw).hexdigest(),
        checks={'no_empty_sources':all(s['passages'] for s in records),'no_replacement_characters':'\ufffd' not in raw.decode('utf-8'),
                'no_textbook_questions':all('lightandmatter' not in s['url'] and 'openstax' not in s['url'] for s in records)})
    session.finish(message='The curated source library is ready for conversation.')


if __name__=='__main__':
    main()
