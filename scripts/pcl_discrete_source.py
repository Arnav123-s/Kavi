"""Read textbook truth-table cells, with no computed teaching labels."""

import hashlib
from html.parser import HTMLParser
from pathlib import Path

from kavi.phase.logic import gate_events

DATA = Path(__file__).resolve().parents[1]/'private/discrete-source-20260908'
URL = 'https://discrete.openmathbooks.org/dmoi3/sec_propositional.html'
DIGEST = 'd45179154bbce0faea7f15e2cf56f33cc2b6b8307ad53faa3cb52ea43c3f106d'


class Tables(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables, self.table, self.row, self.cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.table = []
        elif tag == 'tr' and self.table is not None:
            self.row = []
        elif tag in ('td', 'th') and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None:
            self.row.append(''.join(self.cell).strip())
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == 'table' and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def rows(table):
    width = len(table[0])
    return [[int(cell == 'T') for cell in row] for row in table[1:]
            if len(row) == width and all(cell in ('T', 'F') for cell in row)]


def packet():
    raw = (DATA/'logic.html').read_bytes()
    if hashlib.sha256(raw).hexdigest() != DIGEST:
        raise ValueError('Textbook source fingerprint mismatch')
    parser = Tables()
    parser.feed(raw.decode('utf-8'))
    tables = parser.tables
    teaching = []
    for index, operator in enumerate(('and', 'or', 'implies', 'iff', 'not')):
        table_rows = rows(tables[index])
        if len(table_rows) != (2 if operator == 'not' else 4):
            raise ValueError('Primitive truth-table shape changed')
        for row in table_rows:
            teaching.append((gate_events(operator, row[:-1]), row[-1]))
    def cases(index, variables, columns):
        result = []
        for number, row in enumerate(rows(tables[index])):
            assignment = dict(zip(variables, row))
            for column, formula in columns:
                result.append({'table': index, 'row': number, 'column': column,
                               'formula': formula, 'assignments': assignment, 'answer': row[column]})
        return result
    development = cases(5, ('P', 'Q'), [(3, ('or', ('not', 'P'), 'Q'))])
    final = cases(6, ('P', 'Q', 'R'),
                  [(5, ('or', ('implies', 'P', 'Q'), ('implies', 'Q', 'R')))])
    final += cases(8, ('P', 'Q'), [(2, ('not', ('or', 'P', 'Q'))),
                                 (3, ('and', ('not', 'P'), ('not', 'Q')))])
    final += cases(9, ('P', 'Q', 'R'), [(3, ('implies', ('or', 'P', 'Q'), 'R')),
                                      (4, ('or', ('implies', 'P', 'R'), ('implies', 'Q', 'R')))])
    if (len(teaching), len(development), len(final)) != (18, 4, 32):
        raise ValueError('Textbook packet size mismatch')
    return {'first': teaching[:8], 'training': teaching,
            'development': development, 'final': final}
