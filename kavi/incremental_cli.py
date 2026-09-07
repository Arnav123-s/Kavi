"""Follow incoming tokens through the published shared sentence graph."""

import argparse
from pathlib import Path
from .grounded_language import LanguageModel,tokens
from .incremental_paths import IncrementalPaths
from .procedure_core import ProcedureLibrary
from .terminal import configure_utf8_output


def main():
    configure_utf8_output()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('text')
    parser.add_argument('--trace',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    language=LanguageModel.load(root/'experiments/incremental-language-20260907.json')
    graph=IncrementalPaths(language.rules)
    for word in tokens(args.text):
        state=graph.feed(word)
        if args.trace:
            print(f"{word}: {', '.join(state['possible_roles']) or 'no compatible pathway'}")
    result=graph.finish()
    if result['state']!='interpreted':
        print('No unique complete interpretation: '+result['state'])
        return
    meaning=result['complete'][0]
    if meaning['kind']=='calculation':
        library=ProcedureLibrary.load(root/'experiments/library-20260907-compiled.json')
        print('Answer: '+str(library.execute(meaning['label'],tuple(meaning['inputs'])).value))
    else:
        print('Identified relation: '+meaning['label'])
        for role,value in meaning['slots'].items(): print(f'{role}: {value}')
        print('This identifies the statement; its truth is unassessed.')


if __name__=='__main__': main()
