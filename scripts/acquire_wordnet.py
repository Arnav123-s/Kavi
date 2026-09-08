"""Download a licensed lexical database and verify its local representation."""

import hashlib
import json
from pathlib import Path
from urllib.request import Request,urlopen
import zipfile

from kavi.lexical_database import LexicalDatabase
from scripts.configuration_run_support import ROOT,Run


def run(folder):
    session=Run(folder,'docs/CONVERSATION.md',['kavi/lexical_database.py','scripts/acquire_wordnet.py'])
    try:
        url='https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip'
        session.present('Read the lexical database','Real dictionary senses and relationships broaden vocabulary. They remain dictionary knowledge, not evidence of general understanding.',delay=2)
        path=session.folder/'wordnet.zip'
        with urlopen(Request(url,headers={'User-Agent':'Kavi research/1.0'}),timeout=20) as response,path.open('wb') as output:
            size=0
            while True:
                session.check()
                chunk=response.read(262144)
                if not chunk:break
                size+=len(chunk)
                if size>20000000:raise ValueError('Dictionary exceeds the 20 MB download budget')
                output.write(chunk)
        with zipfile.ZipFile(path) as archive:
            if sum(i.file_size for i in archive.infolist())>60000000:raise ValueError('Expanded dictionary exceeds the 60 MB budget')
            license=archive.read('wordnet/LICENSE')
            (session.folder/'LICENSE').write_bytes(license)
        dictionary=LexicalDatabase(path)
        session.result.update(url=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),compressed_bytes=size,
            expanded_bytes=sum(i.file_size for i in archive.infolist()),
            lexical_entries=len(dictionary.senses),sense_count=len(dictionary.definitions),
            license_sha256=hashlib.sha256(license).hexdigest(),
            checks={'license_retained':bool(dictionary.license),'photosynthesis_has_definition':bool(dictionary.lookup('photosynthesis'))})
        session.present('Vocabulary loaded','The original definitions, multiple meanings and attribution are retained.',
            f'{len(dictionary.senses):,} entries; {len(dictionary.definitions):,} senses',delay=2)
        session.finish()
    except Exception as error:
        session.result['error']=str(error)
        session.finish('stopped' if isinstance(error,InterruptedError) else 'failed',str(error))
        raise


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    run(parser.parse_args().run_dir)
