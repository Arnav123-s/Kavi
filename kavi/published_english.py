"""Extend published-question teaching with relevance and linear-equation annotations.

Equation isolation is a supplied annotation procedure. The answerer receives
question text only; it does not run this procedure or see the source formula.
"""

import ast
from collections import Counter, defaultdict
import hashlib
import itertools
import json
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from .english_configurations import (
    Input, ConnectionTree, EnglishReasoner, annotation, features, numeric,
    read_input, signature, OPS,
)


class PredicateTree:
    def __init__(self, labels=('keep', 'drop'), nodes=None):
        self.labels = tuple(labels)
        self.nodes = [] if nodes is None else nodes

    def teach(self, examples, work, depth=12, min_leaf=3):
        self.nodes = []
        def purity(counts, n):
            return sum(v*v for v in counts.values()) / n if n else 0.
        def build(ids, level):
            work.add('predicate_nodes')
            counts = Counter(examples[i][1] for i in ids)
            index = len(self.nodes)
            ports = sorted((label for label in self.labels if counts[label]),
                           key=lambda label:(-counts[label], self.labels.index(label)))
            self.nodes.append({'ports':ports})
            if level >= depth or len(counts) <= 1 or len(ids) < min_leaf*2:
                return index
            observed = defaultdict(Counter)
            for i in ids:
                for feature in examples[i][0]:
                    observed[feature][examples[i][1]] += 1
            work.add('predicate_observations', sum(len(examples[i][0]) for i in ids))
            best, gain = None, 1e-9
            for feature, yes in sorted(observed.items()):
                work.add('predicate_candidates')
                n = sum(yes.values())
                if min(n, len(ids)-n) < min_leaf:
                    continue
                no = {label:counts[label]-yes[label] for label in counts}
                value = purity(yes,n)+purity(no,len(ids)-n)-purity(counts,len(ids))
                if value > gain:
                    best, gain = feature, value
            if best is not None:
                yes = [i for i in ids if best in examples[i][0]]
                no = [i for i in ids if best not in examples[i][0]]
                self.nodes[index] = {'feature':best, 'yes':build(yes,level+1), 'no':build(no,level+1)}
            return index
        if not examples:
            raise ValueError('No admitted lessons')
        build(list(range(len(examples))),0)
        return self

    def activate(self, values, work):
        index, trace = 0, []
        while 'feature' in self.nodes[index]:
            node = self.nodes[index]
            active = node['feature'] in values
            work.add('relevance_connections')
            trace.append({'node':index,'condition':node['feature'],'active':active})
            index = node['yes'] if active else node['no']
        return self.nodes[index]['ports'], trace


def unary_features(inp, index):
    result = set(features(inp, index, index))
    local = inp.words[max(0, inp.positions[index]-3):inp.positions[index]+4]
    if set(local) & (set(inp.question)-{'how','what','many','much','the','a','of','is','in'}):
        result.add('local_word_in_question')
    return frozenset(result)


def project(inp, indices):
    return Input(inp.text,inp.words,[inp.positions[i] for i in indices],
                 [inp.numbers[i] for i in indices],inp.question)


ZERO, ONE = ('c',0), ('c',1)


def op(symbol, a, b):
    if symbol == '+':
        if a == ZERO:return b
        if b == ZERO:return a
        if isinstance(b,tuple) and b[0] == 'neg':return op('-',a,b[1])
    if symbol == '-':
        if b == ZERO:return a
        if a == ZERO:return ('neg',b)
        if isinstance(b,tuple) and b[0] == 'neg':return op('+',a,b[1])
    if symbol == '*':
        if a == ZERO or b == ZERO:return ZERO
        if a == ONE:return b
        if b == ONE:return a
    if symbol == '/' and b == ONE:return a
    return symbol,a,b


def formula_tree(formula):
    text = formula.split(';')[-1].replace('×','*').replace('÷','/').replace('−','-').replace(',','')
    if any(x in text for x in ('<','>','^')):
        raise ValueError('comparison-or-power')
    # Remove written unit annotations, without removing arithmetic parentheses.
    text = re.sub(r'\([A-Za-z][A-Za-z /]+\)', '', text)
    text = re.sub(r'(?<=\d)(?=[A-Za-z]\b)', '*', text)
    sides = text.split('=')
    if len(sides) != 2:
        raise ValueError('one-equation-required')
    left = ast.parse(sides[0].strip(),mode='eval').body
    unknowns = {n.id for n in ast.walk(left) if isinstance(n,ast.Name)}
    if not unknowns:
        def expression(node):
            if isinstance(node,ast.Constant) and type(node.value) in (int,float):
                return ('c',node.value)
            if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
                child = expression(node.operand)
                return ('c',-child[1]) if child[0]=='c' else ('neg',child)
            if isinstance(node,ast.BinOp) and type(node.op) in (ast.Add,ast.Sub,ast.Mult,ast.Div):
                return op({ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/'}[type(node.op)],
                          expression(node.left),expression(node.right))
            raise ValueError('unsupported-expression')
        return expression(left), False
    right_text = re.sub(r'\s+[A-Za-z][A-Za-z ]*$', '', sides[1].strip())
    right = ast.parse(right_text,mode='eval').body
    unknowns |= {n.id for n in ast.walk(right) if isinstance(n,ast.Name)}
    if len(unknowns) != 1:
        raise ValueError('one-unknown-required')
    name = next(iter(unknowns))
    def affine(node):
        if isinstance(node,ast.Name) and node.id == name:
            return ONE,ZERO
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            return ZERO,('c',node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
            a,b=affine(node.operand)
            return op('-',ZERO,a),op('-',ZERO,b)
        if not isinstance(node,ast.BinOp):
            raise ValueError('unsupported-linear-equation')
        a,b=affine(node.left);c,d=affine(node.right)
        if isinstance(node.op,(ast.Add,ast.Sub)):
            symbol='+' if isinstance(node.op,ast.Add) else '-'
            return op(symbol,a,c),op(symbol,b,d)
        if isinstance(node.op,ast.Mult):
            if a != ZERO and c != ZERO:raise ValueError('nonlinear-equation')
            return op('+',op('*',a,d),op('*',b,c)),op('*',b,d)
        if isinstance(node.op,ast.Div) and c == ZERO:
            return op('/',a,d),op('/',b,d)
        raise ValueError('unsupported-linear-equation')
    a,b=affine(left);c,d=affine(right)
    return op('/',op('-',d,b),op('-',a,c)), True


def bind_expression(inp, expression):
    used = set()
    def bind(node):
        if node[0] == 'c':
            found = [i for i,v in enumerate(inp.numbers)
                     if i not in used and math.isclose(v,node[1],rel_tol=1e-10,abs_tol=1e-12)]
            if not found:raise ValueError('implicit-or-repeated-quantity')
            used.add(found[0])
            return found[0]
        if node[0] == 'neg':raise ValueError('unbound-negative-sign')
        return node[0],bind(node[1]),bind(node[2])
    program = bind(expression)
    if not 2 <= len(used) <= 8:
        raise ValueError('active-quantity-count')
    indices = sorted(used)
    mapping = {old:new for new,old in enumerate(indices)}
    def remap(node):
        return mapping[node] if type(node) is int else (node[0],remap(node[1]),remap(node[2]))
    program = remap(program)
    labels = {}
    def visit(node):
        if type(node) is int:return [node]
        symbol,a,b=node
        left,right=visit(a),visit(b)
        for i in left:
            for j in right:
                labels[tuple(sorted((i,j)))]=('r'+symbol if i>j and symbol in ('-','/') else symbol)
        return left+right
    visit(program)
    return indices,program,labels


def annotate(text, formula):
    inp = read_input(text)
    if not 2 <= len(inp.numbers) <= 8:
        raise ValueError('input-quantity-count')
    expression, algebra = formula_tree(formula)
    indices,program,labels = bind_expression(inp,expression)
    return inp,indices,program,labels,algebra


class RelevanceReasoner:
    def __init__(self, gate, router, program_router=None, programs=None):
        self.gate, self.router = gate, router
        self.program_router = program_router
        self.programs = programs or {}

    def answer(self, text, registry, work, beam=6):
        inp = read_input(text)
        if not 2 <= len(inp.numbers) <= 8:
            raise ValueError('Input requires two to eight explicit quantities')
        indices, activity = [], []
        for i in range(len(inp.numbers)):
            ports,trace=self.gate.activate(unary_features(inp,i),work)
            if ports[0]=='keep':indices.append(i)
            activity.append({'quantity':i,'ports':ports,'connections':trace})
        if len(indices)<2:
            indices=list(range(min(2,len(inp.numbers))))
        selected=project(inp,indices)
        from .english_configurations import compose,configuration,render
        candidates,active=[],[]
        route_trace=[]
        if self.program_router is not None:
            ports,route_trace=self.program_router.activate(program_features(selected),work)
            # A unique route means the observed lessons at this leaf agreed.
            # It is not a correctness certificate for an unseen question.
            if len(ports)==1:
                entry=self.programs[ports[0]]
                if entry['arity']==len(indices):
                    program=tuples(entry['program'])
                    graph=configuration(program,len(indices))
                    trial=registry.copy();trial.install('question_configuration',graph)
                    try:
                        value=trial.execute('question_configuration',tuple(selected.numbers),work)
                        if not math.isfinite(value):raise ValueError('Nonfinite answer')
                        work.add('reused_program_answers')
                        return {'state':'tentative','value':value,'expression':render(program,selected.numbers),
                                'program':program,'configuration':graph.record(),'active_quantities':indices,
                                'relevance_activity':activity,'program_activity':route_trace,
                                'reused_program':ports[0],'alternative':None,
                                'status':'An existing acquired route executed without candidate construction; interpretation remains unverified.'}
                    except (ValueError,ZeroDivisionError,OverflowError):
                        work.add('unusable_existing_programs')
        work.add('composition_searches')
        candidates,active=compose(selected,self.router,work,beam=beam,max_quantities=8)
        if not candidates:raise ValueError('No executable configuration')
        best=candidates[0]
        graph=configuration(best.program,len(indices))
        trial=registry.copy();trial.install('question_configuration',graph)
        value=trial.execute('question_configuration',tuple(selected.numbers),work)
        alternate=next((c for c in candidates[1:] if not math.isclose(c.value,value,rel_tol=1e-9,abs_tol=1e-10)),None)
        return {'state':'tentative','value':value,'expression':render(best.program,selected.numbers),
                'program':best.program,'configuration':graph.record(),'active_quantities':indices,
                'relevance_activity':activity,'activations':active,
                'alternative':{'expression':render(alternate.program,selected.numbers),'value':alternate.value,
                               'score':alternate.score} if alternate else None,
                'status':'Learned relevance and operation connections; proposed interpretation is unverified.'}

    def record(self):
        return {'format':'kavi-relevant-english-1','relevance':self.gate.nodes,'operations':self.router.nodes,
                'program_router':self.program_router.nodes if self.program_router else None,'programs':self.programs}

    @classmethod
    def load(cls,path):
        data=json.loads(Path(path).read_text(encoding='utf-8'))
        if data.get('format') != 'kavi-relevant-english-1':raise ValueError('Unknown configuration format')
        router=PredicateTree(labels=tuple(data.get('programs',{})),nodes=data['program_router']) if data.get('program_router') else None
        return cls(PredicateTree(nodes=data['relevance']),ConnectionTree(data['operations']),router,data.get('programs',{}))


def tuples(value):
    return tuple(tuples(v) for v in value) if isinstance(value,list) else value


def program_features(inp):
    result=set()
    for i in range(len(inp.numbers)):
        result.update(unary_features(inp,i))
    result.add('active_arity='+str(len(inp.numbers)))
    return frozenset(result)


def teach(rows, work, *, depth=12, reuse=True):
    relevance=[];connections=[];routes=[];programs={}
    for row in rows:
        inp,indices=row['input'],row['indices']
        selected=project(inp,indices)
        relevance.extend((unary_features(inp,i),'keep' if i in indices else 'drop') for i in range(len(inp.numbers)))
        connections.extend((features(selected,i,j),label) for (i,j),label in row['labels'].items())
        body=json.dumps(row['program'],separators=(',',':'))
        name='p_'+hashlib.sha256(body.encode()).hexdigest()[:16]
        if name in programs:
            work.add('teaching_program_reuses')
        else:
            # The worked solution supplies this symbolic arrangement.
            # Variable arguments replace the actual teaching quantities.
            programs[name]={'arity':len(indices),'program':row['program']}
            work.add('new_program_definitions')
        routes.append((program_features(selected),name))
    gate=PredicateTree().teach(relevance,work,depth=depth)
    router=ConnectionTree().teach(connections,work,depth=depth)
    selector=PredicateTree(tuple(programs)).teach(routes,work,depth=depth) if reuse else None
    return RelevanceReasoner(gate,router,selector,programs)
