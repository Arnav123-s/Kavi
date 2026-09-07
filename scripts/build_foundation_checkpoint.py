"""Consolidate inspected artifacts and retest the combined library."""

from fractions import Fraction
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from kavi.foundation_curriculum import target as new_target
from kavi.grounded_language import LanguageModel
from kavi.library_curriculum import target as old_target
from kavi.procedure_core import ProcedureLibrary,expression,Limits
from kavi.rational_paths import RationalLibrary


def main():
    output=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'runs/foundation-checkpoint-20260907-01')
    output=output.resolve()
    if not output.is_relative_to(ROOT/'runs'): raise ValueError('Use a new directory below runs')
    output.mkdir(parents=True,exist_ok=False)
    natural=ProcedureLibrary.load(ROOT/'experiments/library-20260907-compiled.json')
    expanded=ProcedureLibrary.load(ROOT/'runs/composition-hints-20260907-01/library-cumulative-17.json')
    for name,proc in expanded.procedures.items():
        if name not in natural.procedures: natural.add(proc)
    rational=RationalLibrary.from_dict(json.loads((ROOT/'runs/rational-20260907-02/library.json').read_text(encoding='utf-8')))
    repaired=RationalLibrary.from_dict(json.loads((ROOT/'runs/rational-repair-20260907-01/library.json').read_text(encoding='utf-8')))
    for name,proc in repaired.procedures.items():
        if name not in rational.procedures: rational.add(name,proc.arity,proc.body)
    original_language=LanguageModel.load(ROOT/'runs/connector-language-20260907-01/language.json')
    original_language.prefer_specific=True
    new_language=LanguageModel.load(ROOT/'runs/composition-hints-20260907-01/language.json')
    # Preserve existing interpretations when two frames differ only in slot naming.
    def signature(rule):
        return tuple(x if isinstance(x,str) else ('slot',x['type']) for x in rule['pattern'])
    old_signatures={signature(rule) for rule in original_language.rules}
    added=[]
    for rule in new_language.rules:
        if signature(rule) not in old_signatures:
            original_language.rules.append(rule)
            old_signatures.add(signature(rule))
            added.append(rule['label'])
    checks=[]
    for name,proc in natural.procedures.items():
        cases=[(27,),(31,)] if proc.arity==1 else [(31,27),(40,29)] if proc.arity==2 else [(31,27,29),(40,29,37)]
        if name=='factorial': cases=[(12,),(13,)]
        for xs in cases:
            if name in ('fourth','eighth'): expected=xs[0]**({'fourth':4,'eighth':8}[name])
            else:
                try: expected=old_target(name,xs)
                except ValueError: expected=new_target(name,xs)
            actual=natural.execute(name,xs).value
            checks.append({'name':name,'inputs':xs,'expected':expected,'value':actual,'correct':actual==expected})
    rational_checks=[]
    oracles={'reciprocal':lambda x:1/x[0],'ratio':lambda x:x[0]/x[1],
             'signed_affine':lambda x:x[0]*x[1]+x[2],'secant_slope':lambda x:(x[0]-x[1])/x[2],
             'mean_pair':lambda x:(x[0]+x[1])/2}
    for name,oracle in oracles.items():
        arity=rational.procedures[name].arity
        for xs in [tuple([Fraction(-47,17),Fraction(53,19),Fraction(59,23)][:arity]),
                   tuple([Fraction(61,29),Fraction(-67,31),Fraction(71,37)][:arity])]:
            actual=rational.apply('call',name,xs).value
            expected=oracle(xs)
            rational_checks.append({'name':name,'inputs':[str(x) for x in xs],'expected':str(expected),
                                    'value':str(actual),'correct':actual==expected})
    packet=json.loads((ROOT/'private/sources/connector-language-packet.json').read_text(encoding='utf-8'))
    old_model=LanguageModel.load(ROOT/'runs/connector-language-20260907-01/language.json')
    language_retention=[old_model.interpret(x['text'])==original_language.interpret(x['text']) for x in packet['evaluation']]
    if not all(x['correct'] for x in checks+rational_checks) or not all(language_retention):
        failure={'natural':[x for x in checks if not x['correct']],
                 'rational':[x for x in rational_checks if not x['correct']],
                 'language':[{'text':x['text'],'before':old_model.interpret(x['text']),
                             'after':original_language.interpret(x['text'])} for x in packet['evaluation']
                             if old_model.interpret(x['text'])!=original_language.interpret(x['text'])]}
        (output/'failed-integration.json').write_text(json.dumps(failure,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(failure))
        raise RuntimeError('Integrated artifact failed a retention or correctness check')
    (output/'natural.json').write_bytes(natural.encoded())
    (output/'rational.json').write_bytes(rational.encoded())
    (output/'language.json').write_bytes(original_language.encoded())
    report={'scope':'Consolidation check; lowest-seed cumulative artifact chosen for inspection, not a new independent graduate assessment. Existing names retain existing implementations.',
            'natural_procedures':len(natural.procedures),'rational_procedures':len(rational.procedures),
            'natural_bytes':len(natural.encoded()),'rational_bytes':len(rational.encoded()),'language_bytes':len(original_language.encoded()),
            'added_language_labels':added,'natural_checks':checks,'rational_checks':rational_checks,
            'old_language_retention':{'correct':sum(language_retention),'total':len(language_retention)}}
    (output/'integration.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if not k.endswith('_checks')}))


if __name__=='__main__': main()
