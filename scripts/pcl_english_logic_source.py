"""Original English examples and explicit teacher annotations.

Quoted source fragments are checked against the pinned author's HTML. Their
clause spans and formula labels are supplied annotations, not acquired parsing.
"""

from html.parser import HTMLParser
import hashlib
from scripts.pcl_discrete_source import DATA, Tables, rows

DIGEST = '953b886b8b046b569e183f8304ea9ee7ebe899b0c5de8a48f8a7bec6ce6bfe25'


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, data):
        self.parts.append(data)


def english():
    raw = (DATA/'statements.html').read_bytes()
    if hashlib.sha256(raw).hexdigest() != DIGEST:
        raise ValueError('English source changed')
    parser = Text(); parser.feed(raw.decode('utf-8'))
    source = ' '.join(' '.join(parser.parts).split())
    import json
    from pathlib import Path
    metadata = json.loads((Path(__file__).resolve().parents[1]/'curriculum/pcl-english-logic-annotations.json').read_text())
    banks = []
    for name in ('training', 'final'):
        examples = []
        for item in metadata['banks'][name]:
            start, end = item['span']
            sentence = source[start:end]
            clauses = tuple(sentence[a:b] for a,b in item['clauses'])
            examples.append((sentence, clauses, item['port']))
        banks.append(examples)
    return tuple(banks)


def hard_cases():
    parser=Tables(); parser.feed((DATA/'logic.html').read_text(encoding='utf-8'))
    specifications = [
        (13, ('P','Q'), [(4,('implies',('not','P'),'Q'))]),
        (19, ('P','Q'), [(4,('implies',('and','P','Q'),('or','P','Q')))]),
        (21, ('P','Q'), [(4,('or',('not','Q'),('implies','Q','P')))]),
        (23, ('P','Q','R'), [(5,('or','P',('implies','R',('not','Q'))))]),
        (25, ('P','Q','R'), [(3,('implies','P',('or','Q','R'))),
                            (4,('or',('implies','P','Q'),('implies','P','R')))]),
    ]
    result=[]
    for index,variables,columns in specifications:
        for row in rows(parser.tables[index]):
            for col,formula in columns:
                result.append({'formula':formula,'assignments':dict(zip(variables,row)),
                               'answer':row[col], 'table':index})
    return result
