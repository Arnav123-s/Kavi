"""Acquire the published, manually annotated ASDiv English problem corpus."""

import hashlib
import json
from pathlib import Path
from urllib.request import Request,urlopen
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'private/english-reasoning-20260907'
    folder.mkdir(parents=True,exist_ok=True)
    url='https://raw.githubusercontent.com/chaochun/nlu-asdiv-dataset/master/dataset/ASDiv.xml'
    with urlopen(Request(url,headers={'User-Agent':'Kavi research/1.0'}),timeout=20) as response:
        raw=response.read(4000001)
    if len(raw)>4000000:raise ValueError('Corpus exceeds its four MB budget')
    root=ET.fromstring(raw)
    (folder/'ASDiv.xml').write_bytes(raw)
    record={'title':'ASDiv V1.0','authors':['Shen-Yun Miao','Chao-Chun Liang','Keh-Yih Su'],
        'url':url,'paper':'https://aclanthology.org/2020.acl-main.92/','license':'CC BY-NC 4.0',
        'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'problems':len(root.findall('.//Problem')),
        'construction':'Published website problems, edited for diversity and manually annotated by the dataset authors; no newly generated questions are added here.',
        'retrieved':'2026-09-07'}
    (folder/'source.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    from collections import Counter
    print(json.dumps(record))
    print(Counter(p.attrib.get('Source') for p in root.findall('.//Problem')))


if __name__=='__main__':main()
