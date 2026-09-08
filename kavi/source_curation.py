"""Source-body extraction and corpus checks before conversational use."""

from html.parser import HTMLParser
import re


class BodyParagraphs(HTMLParser):
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[]
        self.kind=None
        self.parts=[]
        self.heading=''
        self.rows=[]

    def flush(self):
        value=re.sub(r'\s+',' ',''.join(self.parts)).strip()
        if self.kind in ('h1','h2','h3'):
            self.heading=value.rstrip('¶')
        elif self.kind and len(value)>40:
            self.rows.append({'heading':self.heading,'text':value})
        self.parts=[]
        self.kind=None

    def handle_starttag(self,tag,attributes):
        attrs=dict(attributes)
        excluded=any(x[1] for x in self.stack) or tag in ('script','style','nav','footer','header','aside','form','noscript','svg') or attrs.get('role')=='navigation'
        if tag not in self.VOID:
            self.stack.append((tag,excluded))
        if not excluded and tag in ('p','h1','h2','h3'):
            self.flush()
            self.kind=tag
        if tag=='br' and self.kind:
            self.parts.append(' ')

    def handle_endtag(self,tag):
        if tag in self.VOID:
            return
        if tag in ('p','h1','h2','h3'):
            self.flush()
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:]
                break

    def handle_data(self,data):
        if self.kind and not any(x[1] for x in self.stack):
            self.parts.append(data)


def curate_html(raw, source):
    # The locally acquired pages declare UTF-8. Honor the actual document's
    # declaration instead of a conflicting or missing HTTP charset.
    text=raw.decode('utf-8',errors='strict')
    if source['id'].startswith('usgs-') and '/faqs/' in source['url']:
        start=text.find('class="node-main')
        end=text.find('<div class="usgs-tabs-wrapper',start)
        if start<0 or end<0:
            raise ValueError('USGS main article boundary was not found')
        text='<div '+text[start:end]
    parser=BodyParagraphs()
    parser.feed(text)
    parser.flush()
    rows=[]
    for row in parser.rows:
        if source['id'].startswith('nhgri-') and row['heading'] not in ('Definition','Narration'):
            continue
        if any(s in row['text'].casefold() for s in ('official websites use','secure .gov','share sensitive information',
              'website feedback','website is','sign up','subscribe','privacy policy','all rights reserved','learn more:',
              'see:','previous topic','next topic','the python software foundation is a non-profit')):
            continue
        for sentence in re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-ÖØ-Þ])',row['text']):
            if 40<=len(sentence)<=1800:
                rows.append(dict(row,text=sentence))
    return rows


def deduplicate(records):
    # Repeated site-wide boilerplate should not become apparent knowledge.
    sources_by_text={}
    for source in records:
        for row in source['passages']:
            sources_by_text.setdefault(row['text'],set()).add(source['id'])
    rejected={t for t,ids in sources_by_text.items() if len(ids)>=3}
    for source in records:
        seen=set()
        source['passages']=[r for r in source['passages'] if r['text'] not in rejected and not
            (r['text'] in seen or seen.add(r['text']))]
    return sum(len(ids) for t,ids in sources_by_text.items() if t in rejected)
