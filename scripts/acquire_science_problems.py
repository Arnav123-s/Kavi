"""Acquire original published scientific questions; keep source bodies local."""

import hashlib
import json
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
DESTINATION=ROOT/'private/science-problems-20260907'
FILES=('fund_sol.json','matter_sol.json','calculus_sol.json','stat_sol.json',
       'class.json','atkins.json','diff.json')


def read(url,limit):
    request=Request(url,headers={'User-Agent':'Kavi-source-acquisition'})
    with urlopen(request,timeout=30) as response:
        body=response.read(limit+1)
    if len(body)>limit:raise ValueError('Source exceeds acquisition limit')
    return body


def main():
    DESTINATION.mkdir(parents=True,exist_ok=True)
    metadata=json.loads(read('https://api.github.com/repos/mandyyyyii/scibench/commits/main',2_000_000))
    revision=metadata['sha']
    record={'source':'https://github.com/mandyyyyii/scibench','revision':revision,
            'purpose':'Original textbook problems and reference solutions; generated model outputs excluded.',
            'files':{}}
    for name in FILES+('LICENSE',):
        relative=name if name=='LICENSE' else 'dataset/original/'+name
        url='https://raw.githubusercontent.com/mandyyyyii/scibench/'+revision+'/'+relative
        body=read(url,5_000_000)
        target=DESTINATION/name
        if target.exists() and target.read_bytes()!=body:
            raise ValueError('An existing source snapshot differs; use a new destination')
        target.write_bytes(body)
        record['files'][name]={'url':url,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),
                              'role':'license' if name=='LICENSE' else 'teaching' if name.endswith('_sol.json') else 'reserved_evaluation'}
    (DESTINATION/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,indent=2))


if __name__=='__main__':main()
