"""Finite, attributable passage retrieval; independent of program acquisition."""

from collections import Counter
from html.parser import HTMLParser
import math
import re
import unicodedata


STOP = set('a an the is are was were be been being what which who whom why how when where does do did can could would should will of in on at to for from with and or by as it its this that these those i me my you your tell explain about please more'.split())


def tokens(text):
    words=re.findall(r'[^\W_]+',unicodedata.normalize('NFKC',text).casefold())
    return [w[:-1] if len(w)>4 and w.endswith('s') and not w.endswith('ss') else w
            for w in words if w not in STOP and len(w)>1]


class PassageHTML(HTMLParser):
    """Extract prose, discarding active content and common navigation containers."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.parts=[]
        self.rows=[]
        self.heading=''
        self.kind=None

    def flush(self):
        text=re.sub(r'\s+',' ',''.join(self.parts)).strip()
        if self.kind in ('h1','h2','h3') and text:
            self.heading=text
        elif self.kind and len(text)>=55 and len(text.split())>=9:
            self.rows.append({'heading':self.heading,'text':text})
        self.parts=[]
        self.kind=None

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        excluded=tag in ('script','style','nav','footer','header','aside','form','noscript') or attrs.get('role')=='navigation'
        excluded=excluded or any(self.stack)
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'):
            self.stack.append(excluded)
        if not excluded and tag in ('p','h1','h2','h3'):
            self.flush()
            self.kind=tag
        if tag=='br' and self.kind:
            self.parts.append(' ')

    def handle_endtag(self,tag):
        if tag in ('p','h1','h2','h3'):
            self.flush()
        if self.stack:
            self.stack.pop()

    def handle_data(self,data):
        if self.kind and not any(self.stack):
            self.parts.append(data)

    def passages(self):
        self.flush()
        seen=set()
        rows=[]
        for row in self.rows:
            if row['text'] in seen or any(s in row['text'].casefold() for s in
                    ('sign up for','subscribe to','all rights reserved','privacy policy','skip to main','share this page')):
                continue
            seen.add(row['text'])
            # Whole sentences are retained; these are source passages, not
            # generated summaries or generated question-answer pairs.
            for sentence in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])',row['text']):
                if 45 <= len(sentence) <= 1800:
                    rows.append({'heading':row['heading'],'text':sentence})
        return rows


class SourceLibrary:
    def __init__(self, records):
        self.records=records
        self.entries=[]
        for source in records:
            for passage in source.get('passages',[]):
                words=tokens(passage['text'])
                if words:
                    self.entries.append((source,passage,Counter(words),len(words)))
        self.df=Counter(t for _,_,counts,_ in self.entries for t in counts)
        self.mean_length=sum(n for *_,n in self.entries)/max(1,len(self.entries))

    def search(self, query, limit=2):
        terms=set(tokens(query))
        if not terms:
            return []
        rows=[]
        for source,passage,counts,length in self.entries:
            metadata=set(tokens(source['title']+' '+passage['heading']))
            matched=terms.intersection(counts.keys()|metadata)
            if len(matched)/len(terms)<.5:
                continue
            score=0.
            for term in matched:
                tf=counts.get(term,0)
                idf=math.log(1+(len(self.entries)-self.df[term]+.5)/(self.df[term]+.5))
                score+=idf*(tf*2.2/(tf+1.2*(.25+.75*length/self.mean_length)) if tf else 0)
                score+=.8*idf*(term in metadata)
            if not terms.intersection(counts):
                continue
            rows.append({'score':score,'coverage':len(matched)/len(terms),'source':source,'passage':passage})
        rows.sort(key=lambda r:r['score'],reverse=True)
        unique=[]
        for row in rows:
            if row['source']['id'] not in {r['source']['id'] for r in unique}:
                unique.append(row)
            if len(unique)==limit:
                break
        return unique


def excerpt(text, query, words=24):
    pieces=text.split()
    if len(pieces)<=words:
        return text
    desired=set(tokens(query))
    # Select one contiguous span, preserving the source's actual words.
    start=max(range(len(pieces)-words+1),key=lambda i:len(desired.intersection(tokens(' '.join(pieces[i:i+words])))))
    return ('… ' if start else '')+' '.join(pieces[start:start+words])+(' …' if start+words<len(pieces) else '')
