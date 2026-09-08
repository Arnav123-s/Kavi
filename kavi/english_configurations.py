"""Learn language-conditioned connections and construct arithmetic programs.

Training supplies published problem/formula pairs. Inference sees only text.
No stored question, answer, nearest-neighbour search or source passage is used.
"""

import ast
from collections import Counter,defaultdict
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
import re
import unicodedata

from .composable_configurations import Configuration,Work,encoded


OPS=('+','-','r-','*','/','r/')
NUMBER_WORDS=dict(zip('zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty'.split(),range(21)))
FUNCTION_WORDS=set('a an the is are was were be been being i you he she it they we his her their our my your in on at to of for from with and or but if then how what which who that this these those there here some any can could would should do does did has have had will may'.split())
WORD=re.compile(r'\d+(?:,\d{3})*(?:\.\d+)?|[A-Za-z]+(?:\x27[A-Za-z]+)?|[?.!,;:$%()]')


def stem(word):
    word=word.casefold().replace("'s",'')
    if len(word)>5 and word.endswith('ing'):return word[:-3]
    if len(word)>4 and word.endswith('ed'):return word[:-2]
    if len(word)>4 and word.endswith('s') and not word.endswith('ss'):return word[:-1]
    return word


@dataclass
class Input:
    text: str
    words: list
    positions: list
    numbers: list
    question: list


def read_input(text):
    if not isinstance(text,str) or len(text)>4000:raise ValueError('Question exceeds 4,000 characters')
    words=WORD.findall(unicodedata.normalize('NFKC',text).replace('’',"'"))
    if len(words)>220:raise ValueError('Question exceeds 220 tokens')
    positions=[]; numbers=[]
    for i,word in enumerate(words):
        if re.fullmatch(r'\d+(?:,\d{3})*(?:\.\d+)?',word):
            value=float(word.replace(',',''))
        elif word.casefold() in NUMBER_WORDS:
            value=float(NUMBER_WORDS[word.casefold()])
        else:continue
        if not math.isfinite(value) or abs(value)>1e12:raise ValueError('Quantity exceeds its numerical bound')
        positions.append(i); numbers.append(value)
    words=[stem(w) for w in words]
    qstart=max((i for i,w in enumerate(words) if w in ('how','what','find','calculate','determine')),default=0)
    return Input(text,words,positions,numbers,words[qstart:])


def signature(text):
    # Group literal templates and number variants before data splitting.
    # Capitalized personal-name-like tokens share a placeholder. No answers
    # or formula operators participate in this grouping.
    raw=WORD.findall(unicodedata.normalize('NFKC',text))
    fixed=[]
    starts={'A','An','The','How','What','If','When','There','Each','In','On','It','He','She','They','We','You','At','After','Before','During','For','One','Two','Three'}
    for word in raw:
        if word[0].isdigit() or word.casefold() in NUMBER_WORDS:fixed.append('#')
        elif word[0].isupper() and word not in starts:fixed.append('@')
        else:fixed.append(stem(word))
    return ' '.join(fixed)


def features(inp,i,j):
    a,b=inp.positions[i],inp.positions[j]
    words=inp.words
    result={'number_count='+str(len(inp.numbers)), 'pair='+str(i)+','+str(j)}
    for token in words:
        if token.isalpha():result.add('word='+token)
    for token in inp.question:
        if token.isalpha():result.add('question='+token)
    for k in range(len(words)-1):
        if words[k].isalpha() and words[k+1].isalpha():result.add('phrase='+words[k]+' '+words[k+1])
    for prefix,position in (('first',a),('second',b)):
        for offset in range(-4,5):
            q=position+offset
            if offset and 0<=q<len(words) and words[q].isalpha():
                result.add(prefix+':'+str(offset)+'='+words[q])
        local=[w for w in words[max(0,position-5):position+6] if w.isalpha()]
        result.update(prefix+'near='+w for w in local)
    result.update('between='+w for w in words[a+1:b] if w.isalpha())
    if inp.numbers[i]<inp.numbers[j]:result.add('first_smaller')
    if inp.numbers[i]==inp.numbers[j]:result.add('equal_values')
    left=[w for w in words[a+1:a+4] if w.isalpha() and w not in FUNCTION_WORDS]
    right=[w for w in words[b+1:b+4] if w.isalpha() and w not in FUNCTION_WORDS]
    if set(left)&set(right):result.add('shared_following_word')
    return frozenset(result)


def annotation(text,formula):
    """Translate the author's formula into connections between input quantities."""
    inp=read_input(text)
    if not 2<=len(inp.numbers)<=5:raise ValueError('quantity-count')
    expression=formula.split('=')[0].replace('×','*').replace('÷','/').replace('^','**').replace(',','')
    tree=ast.parse(expression,mode='eval').body
    used=set()
    def walk(node):
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            found=[i for i,v in enumerate(inp.numbers) if i not in used and math.isclose(v,node.value,rel_tol=1e-10,abs_tol=1e-12)]
            if not found:raise ValueError('implicit-constant-or-repeated-quantity')
            used.add(found[0]);return found[0]
        if isinstance(node,ast.BinOp) and type(node.op) in (ast.Add,ast.Sub,ast.Mult,ast.Div):
            return ({ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/'}[type(node.op)],walk(node.left),walk(node.right))
        raise ValueError('formula-outside-four-operation-grammar')
    program=walk(tree)
    if used!=set(range(len(inp.numbers))):raise ValueError('irrelevant-or-unrepresented-quantity')
    labels={}
    def pairs(node):
        if type(node) is int:return [node]
        op,l,r=node
        left,right=pairs(l),pairs(r)
        for i in left:
            for j in right:
                labels[tuple(sorted((i,j)))]=('r'+op if i>j and op in ('-','/') else op)
        return left+right
    pairs(program)
    return inp,program,labels


def numeric(program,numbers):
    if type(program) is int:return numbers[program]
    op,a,b=program
    x,y=numeric(a,numbers),numeric(b,numbers)
    value=x+y if op=='+' else x-y if op=='-' else x*y if op=='*' else x/y
    if not math.isfinite(value) or abs(value)>1e15:raise ValueError('Numerical bound exceeded')
    return value


class ConnectionTree:
    """Discrete learned predicates route activation to operation evidence."""
    def __init__(self,nodes=None):self.nodes=nodes or []

    def teach(self,examples,work,*,depth=12,min_leaf=3):
        self.nodes=[]
        x=[row[0] for row in examples]; y=[OPS.index(row[1]) for row in examples]
        def counts(ids):return Counter(y[i] for i in ids)
        def purity(c,n):return sum(v*v for v in c.values())/n if n else 0
        def build(ids,level):
            work.add('training_nodes')
            total=counts(ids)
            index=len(self.nodes)
            self.nodes.append({'counts':[total[k] for k in range(len(OPS))]})
            if level>=depth or len(total)==1 or len(ids)<2*min_leaf:return index
            by_feature=defaultdict(Counter)
            for i in ids:
                for f in x[i]:by_feature[f][y[i]]+=1
            work.add('feature_observations',sum(len(x[i]) for i in ids))
            baseline=purity(total,len(ids))
            best=None;best_gain=1e-9
            for feature,yes in sorted(by_feature.items()):
                work.add('candidate_splits')
                n=sum(yes.values()); m=len(ids)-n
                if min(n,m)<min_leaf:continue
                no={k:total[k]-yes[k] for k in total}
                gain=purity(yes,n)+purity(no,m)-baseline
                if gain>best_gain:
                    best_gain=gain;best=feature
            if best is None:return index
            yes=[i for i in ids if best in x[i]]
            no=[i for i in ids if best not in x[i]]
            self.nodes[index].update(feature=best,yes=build(yes,level+1),no=build(no,level+1))
            return index
        if not examples:raise ValueError('No usable supervised connections')
        build(list(range(len(x))),0)
        # Class frequencies exist only during teaching. The deployed object
        # retains branch connections and an ordering of operation ports.
        for node in self.nodes:
            frequency=node.pop('counts')
            if 'feature' not in node:
                node['ports']=sorted(OPS,key=lambda op:(-frequency[OPS.index(op)],OPS.index(op)))
        return self

    def activate(self,feats,work):
        index=0;trace=[]
        while 'feature' in self.nodes[index]:
            node=self.nodes[index];active=node['feature'] in feats
            work.add('connection_activations')
            trace.append({'node':index,'condition':node['feature'],'active':active})
            index=node['yes'] if active else node['no']
        ports=self.nodes[index]['ports']
        # Fixed rank costs belong to the search controller, not learned
        # numerical weights or stored example frequencies.
        return {op:math.exp(-rank) for rank,op in enumerate(ports)},trace


@dataclass
class Candidate:
    program: object
    value: float
    score: float


def compose(inp,router,work,*,beam=6):
    n=len(inp.numbers)
    if not 2<=n<=5:raise ValueError('English reasoning currently supports two to five explicit quantities')
    evidence={};active=[]
    for i,j in itertools.combinations(range(n),2):
        preferences,trace=router.activate(features(inp,i,j),work)
        evidence[i,j]=preferences
        active.append({'quantities':[i,j],'connections':trace,'operation_preference':preferences})
    memo={1<<i:[Candidate(i,inp.numbers[i],0.)] for i in range(n)}
    for size in range(2,n+1):
        for chosen in itertools.combinations(range(n),size):
            mask=sum(1<<i for i in chosen);first=1<<chosen[0]
            candidates=[]
            sub=(mask-1)&mask
            while sub:
                other=mask^sub
                if other and sub&first:
                    left_indices=[i for i in chosen if sub&(1<<i)]
                    right_indices=[j for j in chosen if other&(1<<j)]
                    for op in OPS:
                        score=0.
                        for i in left_indices:
                            for j in right_indices:
                                label=op
                                if i>j and op in ('-','/','r-','r/'):
                                    label=op[1:] if op.startswith('r') else 'r'+op
                                score+=math.log(evidence[tuple(sorted((i,j)))][label])
                        for a,b in itertools.product(memo[sub],memo[other]):
                            work.add('candidate_configurations')
                            operation=op.removeprefix('r')
                            aa,bb=(b,a) if op.startswith('r') else (a,b)
                            program=(operation,aa.program,bb.program)
                            try:
                                value=numeric((operation,0,1),(aa.value,bb.value))
                            except (ValueError,OverflowError,ZeroDivisionError):
                                work.add('invalid_configurations');continue
                            candidates.append(Candidate(program,value,a.score+b.score+score))
                sub=(sub-1)&mask
            candidates.sort(key=lambda c:(-c.score,str(c.program)))
            unique=[];seen=set()
            for candidate in candidates:
                key=json.dumps(candidate.program)
                if key not in seen:
                    seen.add(key);unique.append(candidate)
                if len(unique)>=beam:break
            memo[mask]=unique
    return memo[(1<<n)-1],active


def configuration(program,arity):
    calls=[];shared={}
    def build(node):
        if type(node) is int:return node
        op,a,b=node
        refs=(build(a),build(b))
        name={'+':'science_sum','-':'science_difference','*':'science_work','/':'science_ratio'}[op]
        key=(name,refs)
        if key not in shared:
            calls.append(key);shared[key]=arity+len(calls)-1
        return shared[key]
    output=build(program)
    return Configuration(arity,tuple(calls),output)


def render(program,numbers):
    if type(program) is int:return format(numbers[program],'.10g')
    op,a,b=program
    return '('+render(a,numbers)+' '+op+' '+render(b,numbers)+')'


class EnglishReasoner:
    def __init__(self,router):self.router=router

    def answer(self,text,registry,work,beam=6):
        inp=read_input(text)
        candidates,active=compose(inp,self.router,work,beam=beam)
        if not candidates:raise ValueError('No executable candidate within the grammar')
        best=candidates[0]
        graph=configuration(best.program,len(inp.numbers))
        trial=registry.copy();trial.install('question_configuration',graph)
        value=trial.execute('question_configuration',tuple(inp.numbers),work)
        if not math.isclose(value,best.value,rel_tol=1e-9,abs_tol=1e-10):raise ValueError('Constructed and executed configurations disagree')
        alternate=next((c for c in candidates[1:] if not math.isclose(c.value,value,rel_tol=1e-9,abs_tol=1e-10)),None)
        return {'state':'tentative','value':value,'expression':render(best.program,inp.numbers),
            'program':best.program,'configuration':graph.record(),'activations':active,
            'score':best.score,'alternative':{'expression':render(alternate.program,inp.numbers),'value':alternate.value,'score':alternate.score} if alternate else None,
            'status':'A learned language route ranked this computed answer; no answer oracle verified the interpretation.'}

    def record(self):return {'format':'kavi-english-connections-1','nodes':self.router.nodes}

    @classmethod
    def load(cls,path):
        from pathlib import Path
        data=json.loads(Path(path).read_text(encoding='utf-8'))
        if data.get('format')!='kavi-english-connections-1':raise ValueError('Unknown English connection format')
        return cls(ConnectionTree(data['nodes']))
