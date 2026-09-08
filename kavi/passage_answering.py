"""Inspectably ranked source sentences for short explanatory answers."""

import re

from .source_library import SourceLibrary,tokens


class PassageAnswerer(SourceLibrary):
    def search(self,query,limit=1):
        terms=set(tokens(query))
        if not terms:return []
        definition=bool(re.match(r'\s*(what (?:is|are)|what\'s|define|meaning of)\b',query,re.I))
        causal=bool(re.search(r'\b(why|cause|causes|how)\b',query,re.I))
        rows=[]
        for source,passage,counts,length in self.entries:
            body=passage['text']
            if body.endswith('?') or re.search(r'\b(?:there is a lot|much we don.t know|most familiar|learn more|read more)\b',body,re.I):
                continue
            metadata=set(tokens(source['title']+' '+passage['heading']))
            matched=terms.intersection(counts.keys()|metadata)
            coverage=len(matched)/len(terms)
            if coverage<.5 or not terms.intersection(counts):continue
            bodywords=set(counts)
            score=5*coverage+3*len(terms.intersection(bodywords))+.025*min(length,60)
            if definition:
                score+=5*len(terms.intersection(tokens(source['title'])))
                score+=7*(passage['heading']=='Definition')
                score+=3*bool(re.search(r'\b(is|are|refers to|means|consists of|carries)\b',body,re.I))
                score+=4*bool(re.search(r'\b(is|are|refers to|means|carries)\b',' '.join(body.split()[:12]),re.I))
            if causal:
                score+=5*bool(re.search(r'\b(because|caused by|responsible for|due to|causing|causes|by a)\b',body,re.I))
            rows.append({'score':score,'coverage':coverage,'source':source,'passage':passage})
        rows.sort(key=lambda r:r['score'],reverse=True)
        return rows[:limit]
