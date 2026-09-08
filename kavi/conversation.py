"""Local conversational access to acquired calculations and attributable sources."""

import ast
from fractions import Fraction
import json
import math
from pathlib import Path
import re
import time

from .composable_configurations import Work
from .published_learning import load_science
from .source_library import excerpt
from .passage_answering import PassageAnswerer
from .lexical_database import LexicalDatabase
from .inequality_pathway import install as install_bound, answer as answer_bound


ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'experiments/science-20260907-published-model.json'
LOCAL_MODEL=ROOT/'runs/published-lessons-20260907/model.json'
SOURCES=ROOT/'runs/curated-sources-20260907/library.json'


class Arithmetic:
    def __init__(self,registry):
        self.registry=registry

    def answer(self,text,work):
        expression=text.strip().rstrip('?=').strip().lower()
        expression=re.sub(r'^(?:what is|what\'s|calculate|compute|evaluate|solve)\s+','',expression)
        expression=expression.replace('×','*').replace('÷','/').replace('^','**')
        for words, symbol in [('multiplied by','*'),('divided by','/'),('plus','+'),('minus','-'),('times','*')]:
            expression=re.sub(r'\b'+words+r'\b',symbol,expression)
        for word,value in dict(zero=0,one=1,two=2,three=3,four=4,five=5,six=6,seven=7,eight=8,nine=9,ten=10).items():
            expression=re.sub(r'\b'+word+r'\b',str(value),expression)
        if not re.fullmatch(r'[\d\s.+*/()%\-a-z_,]+',expression) or not re.search(r'\d',expression):
            return None
        try:
            tree=ast.parse(expression,mode='eval')
        except SyntaxError:
            return None
        if len(list(ast.walk(tree)))>128:
            raise ValueError('That expression exceeds the calculation limit')
        allowed=(ast.Expression,ast.Constant,ast.BinOp,ast.UnaryOp,ast.Call,ast.Name,ast.Load,
                 ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.Mod,ast.UAdd,ast.USub)
        if any(not isinstance(n,allowed) for n in ast.walk(tree)):
            return None
        def checked(value):
            if isinstance(value,complex) or not math.isfinite(value) or abs(value)>1e100:
                raise ValueError('Result exceeds the real-number calculation range')
            return value
        def apply(node,depth=0):
            work.add('expression_nodes')
            if depth>32:
                raise ValueError('Expression is nested too deeply')
            if isinstance(node,ast.Constant) and type(node.value) in (int,float):
                return checked(node.value)
            if isinstance(node,ast.Name) and node.id in ('pi','e'):
                return getattr(math,node.id)
            if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.UAdd,ast.USub)):
                value=apply(node.operand,depth+1)
                return value if isinstance(node.op,ast.UAdd) else -value
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and len(node.args)==1 and not node.keywords:
                value=apply(node.args[0],depth+1)
                if node.func.id in ('sqrt','sin','cos','tan','log','exp'):
                    work.add('supplied_math_calls')
                    return checked(getattr(math,node.func.id)(value))
                if node.func.id=='abs':
                    return abs(value)
                raise ValueError('That function is not supported')
            if not isinstance(node,ast.BinOp):
                raise ValueError('I could not interpret that calculation')
            a,b=apply(node.left,depth+1),apply(node.right,depth+1)
            if isinstance(node.op,(ast.Add,ast.Mult,ast.Sub)) and type(a) is int and type(b) is int and min(a,b)>=0:
                if isinstance(node.op,ast.Sub) and a<b:
                    return -self.registry.execute('subtract',(b,a),work)
                op='add' if isinstance(node.op,ast.Add) else 'multiply' if isinstance(node.op,ast.Mult) else 'subtract'
                return checked(self.registry.execute(op,(a,b),work))
            work.add('supplied_scalar_calls')
            if isinstance(node.op,ast.Add): return checked(a+b)
            if isinstance(node.op,ast.Sub): return checked(a-b)
            if isinstance(node.op,ast.Mult): return checked(a*b)
            if isinstance(node.op,ast.Div):
                return checked(Fraction(a,b) if isinstance(a,(int,Fraction)) and isinstance(b,(int,Fraction)) else a/b)
            if isinstance(node.op,ast.Mod): return checked(a%b)
            if isinstance(node.op,ast.Pow):
                if abs(b)>64: raise ValueError('Exponents are limited to magnitude 64')
                return checked(a**b)
            raise ValueError('Unsupported arithmetic operator')
        return apply(tree.body)


LABELS={
    'kinetic energy':'kinetic_energy','heating time':'minutes','specific heat':'specific_heat',
    'temperature rise':'delta_temperature','final temperature':'final_temperature','potential energy':'potential_energy',
    'rest energy':'energy','mass equivalent':'mass_equivalent','speed factor':'speed_factor',
    'heat':'heat','speed':'speed','power':'power','work':'work','duration':'duration','cost':'cost',
}
ALIASES={'initial temperature':'initial_temperature','final temperature':'final_temperature',
    'specific heat':'specific_heat','temperature rise':'delta_temperature','heat loss':'heat_loss',
    'light speed':'light_speed','heat power':'heat_power','power factor':'power_factor',
    'kinetic energy':'kinetic_energy','potential energy':'potential_energy','delta temperature':'delta_temperature'}
UNITS={'kinetic_energy':'J','heat':'J','work':'J','potential_energy':'J','energy':'J',
       'specific_heat':'J/(kg·K)','delta_temperature':'K','final_temperature':'°C',
       'speed':'m/s','power':'W','heat_power':'W','duration':'s','minutes':'min','mass_equivalent':'kg'}


def parse_science(text):
    lower=text.lower().strip()
    target=None
    for label,role in sorted(LABELS.items(),key=lambda p:-len(p[0])):
        if re.match(r'^(?:(?:what is|calculate|find|compute|what\'s)\s+(?:the\s+)?)?'+re.escape(label)+r'\b',lower):
            target=role
            break
    if target is None:
        return None
    rest=lower
    for label,role in sorted(ALIASES.items(),key=lambda p:-len(p[0])):
        rest=rest.replace(label,role)
    values={}
    for role,value,unit in re.findall(r'\b([a-z_]+)\s*(?:=|is|of)?\s*(-?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)\s*([a-z/°]*)',rest):
        if role not in {'mass','speed','gravity','height','force','distance','duration','heat','power','work',
            'initial_temperature','final_temperature','specific_heat','delta_temperature','light_speed','heat_power',
            'heat_loss','kinetic_energy','potential_energy','power_factor','price_per_kWh'}:
            continue
        number=float(value)
        allowed_units={'mass':{'kg','g','mg'},'speed':{'m/s','km/h','mph'},'height':{'m','cm'},
            'distance':{'m','cm'},'power':{'w','kw'},'heat_power':{'w','kw'},
            'heat':{'j','kj'},'work':{'j','kj'},'kinetic_energy':{'j','kj'},'heat_loss':{'j','kj'},
            'duration':{'s','sec','seconds','min','minutes','h','hours'}}
        # Conjunctions may immediately follow a dimensionless field value.
        if unit in ('and','with','for'):unit=''
        if unit and role in allowed_units and unit not in allowed_units[role]:
            raise ValueError('Unsupported unit '+unit+' for '+role)
        if not math.isfinite(number) or abs(number)>1e100:
            raise ValueError('A finite quantity within the calculation range is required')
        if role in ('mass','specific_heat','duration','light_speed') and number<=0:
            raise ValueError(role.replace('_',' ')+' must be positive in this calculation')
        if unit in ('g','mg') and role=='mass': number*=.001 if unit=='g' else .000001
        elif unit=='cm' and role in ('height','distance'): number*=.01
        elif unit in ('km/h','mph') and role=='speed': number*=1/3.6 if unit=='km/h' else .44704
        elif unit=='kw' and role in ('power','heat_power'): number*=1000
        elif unit=='kj' and role in ('heat','work','kinetic_energy','heat_loss'): number*=1000
        elif unit in ('min','minutes','h','hours') and role=='duration': number*=60 if unit in ('min','minutes') else 3600
        values[role]=number
    if not values:
        return None
    values.update(seconds_per_minute=60.,joules_per_kWh=3600000.,light_speed=values.get('light_speed',299792458.))
    if target in ('potential_energy','power','duration','speed') and 'height' in values:
        values.setdefault('gravity',9.8)
    return values,target


class Conversation:
    def __init__(self,model_path=None,source_path=None):
        path=model_path or (MODEL if MODEL.exists() else LOCAL_MODEL)
        self.model=load_science(path,ROOT/'experiments/library-20260907-compiled.json',extended=True)
        self.arithmetic=Arithmetic(self.model.registry)
        library_path=Path(source_path or SOURCES)
        self.sources=PassageAnswerer(json.loads(library_path.read_text(encoding='utf-8'))['sources'] if library_path.exists() else [])
        self.dictionary=LexicalDatabase(ROOT/'runs/wordnet-20260907/wordnet.zip')
        bound=ROOT/'experiments/science-20260907-radius-bound.json'
        if not bound.exists():bound=ROOT/'runs/published-bound-20260907/model.json'
        self.has_bound=bound.exists()
        if self.has_bound:install_bound(self.model.registry,bound)
        self.last=None

    def answer(self,question,check=lambda:None):
        started=time.monotonic()
        if not isinstance(question,str) or not question.strip() or len(question)>4000:
            return {'kind':'unknown','text':'Please enter a question of at most 4,000 characters.'}
        work=Work(check=check,limit=300000)
        normalized=question.casefold().strip(' !?.')
        if normalized in ('hi','hello','hey','hello kavi','hi kavi'):
            return {'kind':'conversation','text':'Hello. Ask me a question, give me a calculation, or ask what I can do.'}
        if normalized in ('help','what can you do','who are you','what are you','what is kavi'):
            return {'kind':'conversation','text':f'I am Kavi. I can calculate with my acquired rules, look up {len(self.dictionary.senses):,} dictionary entries, and find passages in {len(self.sources.records)} source documents. Try “What causes earthquakes?” or “Kinetic energy for mass 80 kg and speed 2.4 m/s”. My language and reasoning are still limited.'}
        if normalized in ('why','how','show your work','explain that','how did you get that') and self.last:
            return {'kind':'explanation','text':self.last.get('explanation','This answer is an excerpt from the cited source, not a new derivation.')}
        try:
            if normalized.startswith('radius bound') and self.has_bound:
                values={name:float(v) for name,v in re.findall(r'(descent|rise|fraction)\s*(?:=|is)?\s*([\d.]+)',normalized)}
                if set(values)!={'descent','rise','fraction'}:raise ValueError('Supply descent, rise and normal-force fraction')
                bound=answer_bound(self.model.registry,values['descent'],values['rise'],values['fraction'],work,
                    positive_friction='positive friction' in normalized,starts_at_rest='starts at rest' in normalized,crest='crest' in normalized)
                return self.finish({'kind':'calculation','text':f"0 < radius < {bound['upper']:.10g} m.",'bound':bound,'explanation':bound['explanation']},work,started)
            scientific=parse_science(question)
            if scientific:
                givens,target=scientific
                response=self.model.answer(givens,target,work)
                if response['state']=='answered':
                    value=response['value']
                    trace='\n'.join(f"{s['target'].replace('_',' ')} = {s['value']:.10g}  ({s['configuration']})" for s in response['trace'])
                    result={'kind':'calculation','value':value,'text':f"{target.replace('_',' ').capitalize()}: {value:.10g} {UNITS.get(target,'')}.".strip(),
                            'explanation':trace+'\nInterpreted quantities: '+', '.join(f'{k}={v}' for k,v in givens.items())+'\nUnits and quantity roles are supplied by the interface.',
                            'trace':response['trace']}
                    return self.finish(result,work,started)
                return self.finish({'kind':'unknown','text':'I could not connect those quantities to the requested answer. '+response['reason']},work,started)
            value=self.arithmetic.answer(question,work)
            if value is not None:
                label=str(value) if isinstance(value,(int,Fraction)) else format(value,'.12g')
                detail='Natural-number addition, subtraction and multiplication use acquired programs. Fractions, real numbers and mathematical functions use supplied arithmetic.'
                return self.finish({'kind':'calculation','value':label,'text':label,'explanation':detail},work,started)
        except (ValueError,TypeError,OverflowError,ZeroDivisionError,InterruptedError,RecursionError) as error:
            return self.finish({'kind':'unknown','text':'I could not complete that calculation: '+str(error)},work,started)
        hits=self.sources.search(question,limit=1)
        work.add('passages_scanned',len(self.sources.entries))
        if hits:
            text=[]
            citations=[]
            for hit in hits:
                source=hit['source']
                # Government-authored public-domain passages may be shown as
                # complete short sentences; other extracts remain brief.
                length=60 if source['author'] in ('NASA','U.S. Geological Survey','National Human Genome Research Institute') else 24
                text.append(f"{source['title']} — {source['author']}\n“{excerpt(hit['passage']['text'],question,words=length)}”\n{source['url']}")
                citations.append({'title':source['title'],'url':source['url'],'sha256':source['sha256']})
            return self.finish({'kind':'source','text':'I found these relevant source passages:\n\n'+'\n\n'.join(text),
                               'sources':citations,'explanation':'I matched the words in your question to these real source passages. Relevance does not prove that a passage fully answers the question.'},work,started)
        term=self.dictionary.question_term(question)
        senses=self.dictionary.lookup(term) if term else []
        if senses:
            text='\n'.join(f"{i+1}. {s['definition']}" for i,s in enumerate(senses))
            work.add('dictionary_senses',len(senses))
            return self.finish({'kind':'dictionary','text':f'{term.capitalize()} — dictionary meaning'+('s' if len(senses)>1 else '')+'\n'+text+'\nSource: WordNet 3.0, Princeton University.',
                'sources':[{'title':'WordNet 3.0','url':'https://wordnet.princeton.edu/'}],
                'explanation':'These are the lexical database’s recorded meanings. When a word has multiple senses, the list is not a decision about which one you intended.'},work,started)
        return self.finish({'kind':'unknown','text':'I do not have enough reliable information to answer that yet. I can currently help with calculations and questions covered by my source library.'},work,started)

    def finish(self,result,work,started):
        result.update(work=work.counts,seconds=time.monotonic()-started)
        if result['kind'] in ('calculation','source','dictionary'):
            self.last=result
        return result


def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('question',nargs='*')
    parser.add_argument('--json',action='store_true')
    parser.add_argument('--sources',type=Path)
    args=parser.parse_args()
    chat=Conversation(source_path=args.sources)
    def answer(text):
        result=chat.answer(text)
        print(json.dumps(result,ensure_ascii=False,indent=2) if args.json else result['text'])
    if args.question:
        answer(' '.join(args.question))
        return
    print('Kavi — ask a question. Type /quit to close.')
    while True:
        try: text=input('\nYou: ')
        except (EOFError,KeyboardInterrupt): break
        if text.strip() in ('/quit','/exit'): break
        answer(text)


if __name__=='__main__':
    main()
