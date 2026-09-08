"""Read real problem annotations for structural language teaching."""

import ast
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .english_configurations import read_input,signature,numeric
from .published_english import annotate,bind_expression,project,op

ROOT=Path(__file__).resolve().parents[1]
EXCLUDED=('commoncoresheets.com','dadsworksheets.com','math-aids.com','mathworksheets4kids.com')


def answer_number(text):
    if ';' in text:raise ValueError('multiple-answers')
    match=re.match(r'\s*(-?\d+(?:,\d{3})*(?:\.\d+)?)',text)
    if not match:raise ValueError('non-scalar-answer')
    return float(match[1].replace(',',''))


def row(pid,source,text,formula,answer,partition):
    inp,indices,program,labels,algebra=annotate(text,formula)
    expected=answer_number(answer)
    if not math.isclose(numeric(program,project(inp,indices).numbers),expected,rel_tol=1e-6,abs_tol=1e-7):
        raise ValueError('annotation-answer-disagreement')
    return {'id':pid,'source':source,'text':text,'input':inp,'indices':indices,
            'program':program,'labels':labels,'algebra':algebra,'expected':expected,
            'partition':partition,'signature':signature(text)}


def asdiv():
    raw=(ROOT/'private/english-reasoning-20260907/ASDiv.xml').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='ef8904068482919ac48c8eeaaf6df344b8a308ba66d048c2d4d87eab82dc4929'
    accepted=[];unsupported=[];excluded=[]
    for p in ET.fromstring(raw).findall('.//Problem'):
        if any(d in p.attrib['Source'] for d in EXCLUDED):
            excluded.append(p.attrib['ID']);continue
        text=p.findtext('Body')+' '+p.findtext('Question')
        bucket=int(hashlib.sha256(signature(text).encode()).hexdigest()[:8],16)%10
        partition='train' if bucket<6 else 'development' if bucket<8 else 'test'
        try:
            accepted.append(row(p.attrib['ID'],p.attrib['Source'],text,p.findtext('Formula'),p.findtext('Answer'),partition))
        except (ValueError,SyntaxError,TypeError,ZeroDivisionError,OverflowError) as error:
            unsupported.append({'id':p.attrib['ID'],'partition':partition,'reason':str(error)})
    return accepted,unsupported,excluded


def worked_expression(text, solution):
    inp=read_input(text)
    if not 2<=len(inp.numbers)<=8:raise ValueError('input-quantity-count')
    known={float(v):{json.dumps(('c',v)):('c',v)} for v in inp.numbers}
    def resolve(node):
        if isinstance(node,ast.Constant) and type(node.value) in (int,float):
            matches={key:expr for value,choices in known.items()
                     if math.isclose(value,node.value,rel_tol=1e-10,abs_tol=1e-12)
                     for key,expr in choices.items()}
            if len(matches)>1:raise ValueError('ambiguous-intermediate-binding')
            return next(iter(matches.values())) if matches else ('c',node.value)
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
            child=resolve(node.operand)
            return ('c',-child[1]) if child[0]=='c' else ('neg',child)
        if isinstance(node,ast.BinOp) and type(node.op) in (ast.Add,ast.Sub,ast.Mult,ast.Div):
            return op({ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.Div:'/'}[type(node.op)],resolve(node.left),resolve(node.right))
        raise ValueError('unsupported-worked-step')
    for annotation in re.findall(r'<<([^<>]+)>>',solution):
        try:
            expression,result=annotation.replace(',','').split('=')
            value=float(result)
            symbolic=resolve(ast.parse(expression.strip(),mode='eval').body)
            known.setdefault(value,{})[json.dumps(symbolic)]=symbolic
        except (ValueError,SyntaxError,TypeError):
            continue
    expected=answer_number(solution.split('####')[-1].replace(',',''))
    choices={key:expr for value,items in known.items() if math.isclose(value,expected,rel_tol=1e-10,abs_tol=1e-12)
             for key,expr in items.items()}
    successful={}
    for expression in choices.values():
        try:
            indices,program,labels=bind_expression(inp,expression)
            if math.isclose(numeric(program,project(inp,indices).numbers),expected,rel_tol=1e-6,abs_tol=1e-7):
                successful[json.dumps([indices,program])]=(indices,program,labels)
        except (ValueError,ZeroDivisionError,OverflowError):
            continue
    if len(successful)!=1:raise ValueError('no-unique-supported-worked-program')
    return inp,*next(iter(successful.values())),expected


def gsm(split):
    assert split in ('train','test')
    raw=(ROOT/'private/human-math-20260907'/f'{split}.jsonl').read_bytes()
    digest={'train':'17f347dc51477c50d4efb83959dbb7c56297aba886e5544ee2aaed3024813465',
            'test':'3730d312f6e3440559ace48831e51066acaca737f6eabec99bccb9e4b3c39d14'}[split]
    assert hashlib.sha256(raw).hexdigest()==digest
    accepted=[];unsupported=[]
    for index,line in enumerate(raw.splitlines()):
        data=json.loads(line);text=data['question']
        bucket=int(hashlib.sha256(signature(text).encode()).hexdigest()[:8],16)%10
        partition='test' if split=='test' else 'development' if bucket>=8 else 'train'
        pid=f'gsm-{split}-{index}'
        try:
            inp,indices,program,labels,expected=worked_expression(text,data['answer'])
            accepted.append({'id':pid,'source':'GSM8K human base','text':text,'input':inp,'indices':indices,
                'program':program,'labels':labels,'algebra':False,'expected':expected,
                'partition':partition,'signature':signature(text)})
        except (ValueError,SyntaxError,TypeError,ZeroDivisionError,OverflowError) as error:
            unsupported.append({'id':pid,'partition':partition,'reason':str(error)})
    return accepted,unsupported
