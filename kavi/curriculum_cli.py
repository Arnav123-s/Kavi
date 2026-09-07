"""Inspect the consolidated foundation checkpoint without teaching or mutation."""

import argparse
from fractions import Fraction
import json
from pathlib import Path

from .grounded_language import LanguageModel
from .procedure_core import ProcedureLibrary
from .rational_paths import RationalLibrary


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('show')
    ask=sub.add_parser('ask')
    ask.add_argument('sentence')
    exact=sub.add_parser('exact')
    exact.add_argument('operation')
    exact.add_argument('values',nargs='+',help='Exact integer or fraction values; use -- before negative values')
    args=parser.parse_args()
    folder=Path(__file__).resolve().parents[1]/'experiments'
    natural=ProcedureLibrary.load(folder/'foundation-natural-20260907.json')
    rational=RationalLibrary.from_dict(json.loads((folder/'foundation-rational-20260907.json').read_text(encoding='utf-8')))
    language=LanguageModel.load(folder/'foundation-language-20260907.json')
    if args.command=='show':
        print('Natural-number procedures: '+', '.join(natural.procedures))
        print('Exact signed/fractional procedures: '+', '.join(rational.procedures))
        print('Language: annotated sentence patterns; source-derived lexical memory stays local. General interpretation remains unassessed.')
        print('Stage: tested foundations, not graduate-level competence.')
    elif args.command=='exact':
        try:
            observed=rational.apply('call',args.operation,tuple(Fraction(x) for x in args.values))
            print(f'Answer: {observed.value}')
            print(f'Execution: {observed.calls} calls, {observed.gates} gates, {observed.iterations} iterations. Host fraction normalization is additional work.')
        except (ValueError,ZeroDivisionError) as error:
            parser.error(str(error))
    else:
        result=language.answer(args.sentence,natural)
        if 'value' in result: print('Answer: '+str(result['value']))
        else:
            print('Status: '+result['state'])
            if 'meaning' in result: print(json.dumps(result['meaning'],ensure_ascii=False))
            print(result.get('status','This wording or meaning is not supported by the current checkpoint.'))


if __name__=='__main__': main()
