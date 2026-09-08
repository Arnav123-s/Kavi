"""Read WordNet dictionary senses without generated lessons or a neural model."""

from collections import defaultdict
from pathlib import Path
import re
import zipfile


class LexicalDatabase:
    def __init__(self,path):
        self.senses=defaultdict(list)
        self.definitions={}
        self.words={}
        self.license=''
        if not Path(path).exists():
            return
        with zipfile.ZipFile(path) as archive:
            self.license=archive.read('wordnet/LICENSE').decode('utf-8')
            for pos in ('noun','verb','adj','adv'):
                for line in archive.read('wordnet/data.'+pos).decode('utf-8').splitlines():
                    if not line or not line[0].isdigit():
                        continue
                    fields,gloss=line.split('|',1)
                    parts=fields.split()
                    count=int(parts[3],16)
                    words=[parts[4+2*i].replace('_',' ').removesuffix('(a)').removesuffix('(p)').removesuffix('(ip)') for i in range(count)]
                    key=pos+':'+parts[0]
                    self.words[key]=words
                    self.definitions[key]=gloss.strip()
                # WordNet's index preserves its sense ordering; data-file byte
                # order does not, and must not rank a rare meaning first.
                for line in archive.read('wordnet/index.'+pos).decode('utf-8').splitlines():
                    if not line or line.startswith(' '):
                        continue
                    parts=line.split()
                    n=int(parts[2]); p=int(parts[3])
                    offsets=parts[6+p:6+p+n]
                    for offset in offsets:
                        self.senses[parts[0].replace('_',' ')].append(pos+':'+offset)

    def lookup(self,term,limit=3):
        keys=self.senses.get(term.casefold(),[])
        return [{'sense':key,'words':self.words[key],'definition':self.definitions[key]} for key in keys[:limit]]

    def synonyms(self,term):
        # Bounded expansion only; ambiguous senses are not asserted equivalent.
        return set(w for s in self.lookup(term,limit=2) for w in s['words'])

    def question_term(self,text):
        match=re.fullmatch(r'\s*(?:(?:what is|what are|what\'s|define|explain|meaning of)\s+(?:an?\s+|the\s+)?)?([\w -]{2,70})[?.!]*\s*',text,re.I)
        return match[1].strip().casefold() if match else None
