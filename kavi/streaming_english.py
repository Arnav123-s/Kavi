"""Consume English tokens into current feature activity and acquired operations.

The supplied feature semantics match the earlier English experiment. Learned
predicate connections act on the evolving activity. No input-token history is
kept by the stream state. This is not a general semantic or physics learner.
"""

from collections import deque
import itertools
import json
import math
from pathlib import Path
import re
import unicodedata

from .english_configurations import (
    ConnectionTree,FUNCTION_WORDS,NUMBER_WORDS,WORD,compose,configuration,render,stem,
)
from .signal_configurations import SignalExecution,SignalGraph


class InputActivity:
    def __init__(self,vocabulary,work,*,max_quantities=5):
        self.vocabulary=frozenset(vocabulary)
        self.work=work
        self.max_quantities=max_quantities
        self.numbers=[]
        self.quantities=[]
        self.recent=deque(maxlen=5)
        self.global_features=set()
        self.question_features=set()
        self.between={}
        self.position=0
        self.complete=False

    def _feature(self,destination,key):
        if key in self.vocabulary:destination.add(key)

    def consume(self,raw):
        if self.complete:raise ValueError('The input turn is already complete')
        if self.position>=220:raise ValueError('Question exceeds 220 tokens')
        self.work.add('stream_token_updates')
        token=stem(raw)
        number=None
        if re.fullmatch(r'\d+(?:,\d{3})*(?:\.\d+)?',raw):
            number=float(raw.replace(',',''))
        elif raw.casefold() in NUMBER_WORDS:
            number=float(NUMBER_WORDS[raw.casefold()])
        if number is not None and (not math.isfinite(number) or abs(number)>1e12):
            raise ValueError('Quantity exceeds its numerical bound')
        if number is not None and len(self.numbers)>=self.max_quantities:
            raise ValueError('Input exceeds this streaming quantity interface')
        for q in self.quantities:
            distance=self.position-q['position']
            if distance<=5:q['after'][distance]=token
        if number is not None:
            index=len(self.numbers)
            for i,q in enumerate(self.quantities):
                self.between[i,index]=frozenset(q['since'])
            self.numbers.append(number)
            self.quantities.append({'position':self.position,'token':token,
                'before':{pos-self.position:word for pos,word in self.recent},
                'after':{},'since':set()})
        if token in ('how','what','find','calculate','determine'):
            self.question_features.clear()
        if token.isalpha():
            self._feature(self.global_features,'word='+token)
            self._feature(self.question_features,'question='+token)
            if self.recent and self.recent[-1][1].isalpha():
                self._feature(self.global_features,'phrase='+self.recent[-1][1]+' '+token)
            for q in self.quantities:
                if q['position']<self.position:
                    self._feature(q['since'],'between='+token)
        self.recent.append((self.position,token))
        self.position+=1

    def close(self):
        self.complete=True

    def features(self,i,j):
        self.work.add('stream_feature_reads')
        result=set(self.global_features)|self.question_features
        result.update(('number_count='+str(len(self.numbers)),'pair='+str(i)+','+str(j)))
        for prefix,index in (('first',i),('second',j)):
            q=self.quantities[index]
            context={**q['before'],0:q['token'],**q['after']}
            for offset,word in context.items():
                if word.isalpha():
                    if offset and abs(offset)<=4:result.add(prefix+':'+str(offset)+'='+word)
                    result.add(prefix+'near='+word)
        result.update(self.between.get((i,j),()))
        if self.numbers[i]<self.numbers[j]:result.add('first_smaller')
        if self.numbers[i]==self.numbers[j]:result.add('equal_values')
        def following(index):
            return {word for offset,word in self.quantities[index]['after'].items()
                    if offset<=3 and word.isalpha() and word not in FUNCTION_WORDS}
        if following(i)&following(j):result.add('shared_following_word')
        return frozenset(result & self.vocabulary)

    def state_counts(self):
        return {'tokens_consumed':self.position,'quantity_values':len(self.numbers),
            'recent_tokens':len(self.recent),
            'local_token_slots':sum(len(q['before'])+len(q['after'])+1 for q in self.quantities),
            'active_feature_bits':len(self.global_features)+len(self.question_features)
                +sum(len(v) for v in self.between.values())+sum(len(q['since']) for q in self.quantities),
            'input_complete':self.complete,'retained_full_text':False,'retained_token_history':False}


class StreamingEnglishReasoner:
    def __init__(self,router):
        self.router=router
        self.vocabulary=frozenset(n['feature'] for n in router.nodes if 'feature' in n)

    def begin(self,work):
        return InputActivity(self.vocabulary,work)

    def answer(self,text,registry,work,beam=6,observe=None):
        if not isinstance(text,str) or len(text)>4000:raise ValueError('Question exceeds 4,000 characters')
        state=self.begin(work)
        active_routes={}
        for match in WORD.finditer(unicodedata.normalize('NFKC',text).replace('’',"'")):
            state.consume(match[0])
            for i,j in itertools.combinations(range(len(state.numbers)),2):
                ports,_=self.router.activate(state.features(i,j),work)
                active_routes[i,j]=max(ports,key=ports.get)
            if observe is not None:
                observe({'token':match[0],'tokens_consumed':state.position,
                         'active_routes':dict(active_routes),'answer_released':False})
        state.close()
        candidates,activity=compose(state,self.router,work,beam=beam,
            feature_reader=lambda inp,i,j:inp.features(i,j))
        if not candidates:raise ValueError('No executable candidate in the acquired grammar')
        best=candidates[0]
        graph=configuration(best.program,len(state.numbers))
        trial=registry.copy();trial.install('streamed_question',graph)
        connected=SignalGraph.from_registry(trial,'streamed_question',work)
        execution=SignalExecution(connected,trial.invoke,work,registry=trial)
        for port,value in enumerate(state.numbers):execution.feed(port,value)
        execution.finish_input()
        result=execution.settle()
        if not result['output_available']:raise ValueError('The constructed calculation did not complete')
        if not math.isclose(result['output'],best.value,rel_tol=1e-9,abs_tol=1e-10):
            raise ValueError('Search and signal execution disagree')
        alternate=next((c for c in candidates[1:] if not math.isclose(c.value,best.value,rel_tol=1e-9,abs_tol=1e-10)),None)
        return {'state':'tentative','value':result['output'],'program':best.program,
            'expression':render(best.program,state.numbers),'activations':activity,
            'alternative':{'expression':render(alternate.program,state.numbers),'value':alternate.value,
                           'score':alternate.score} if alternate else None,
            'input_activity':state.state_counts(),'signal_activity':result,
            'status':'Acquired predicates interpreted completed input; the proposed meaning is unverified.'}

    def record(self):
        return {'format':'kavi-streaming-english-1','feature_semantics':'english-connections-1',
                'nodes':self.router.nodes}

    @classmethod
    def load(cls,path):
        record=json.loads(Path(path).read_text(encoding='utf-8'))
        if record.get('format') not in ('kavi-streaming-english-1','kavi-english-connections-1'):
            raise ValueError('Unknown streaming configuration')
        return cls(ConnectionTree(record['nodes']))
