"""Small parser fixtures only; never used as curriculum evidence."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.pcl_relation_source import records


class RelationSourceTests(unittest.TestCase):
    def parse(self, rows):
        with TemporaryDirectory() as folder:
            path = Path(folder)/'fixture.conllu'
            path.write_text('# sent_id = fixture-doc-0001\n'+ '\n'.join(rows)+'\n', encoding='utf-8')
            return list(records(path))

    def rows(self):
        return ['1\tThey\tthey\tPRON\t_\t_\t2\tnsubj\t_\t_',
                '2\tsee\tsee\tVERB\t_\t_\t0\troot\t_\t_',
                '3\tit\tit\tPRON\t_\t_\t2\tobj\t_\t_',
                '4\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_']

    def test_two_queries_preserve_order_without_target_in_events(self):
        rows = self.parse(self.rows())
        self.assertEqual([r['label'] for r in rows], [0, 1])
        self.assertEqual(rows[0]['events'], ('candidate', 'predicate', 'other', 'other'))
        self.assertEqual(rows[1]['events'], ('other', 'predicate', 'candidate', 'other'))
        self.assertEqual(rows[0]['document'], 'fixture-doc')
        self.assertNotIn('text', rows[0])

    def test_passive_subtype_not_relabelled_as_active_subject(self):
        rows = self.rows()
        rows[0] = rows[0].replace('\tnsubj\t', '\tnsubj:pass\t')
        self.assertEqual([r['label'] for r in self.parse(rows)], [1])

    def test_nonverbal_root_is_ineligible(self):
        rows = self.rows()
        rows[1] = rows[1].replace('\tVERB\t', '\tNOUN\t')
        self.assertEqual(self.parse(rows), [])

    def test_multiword_and_empty_node_rows_do_not_create_positions(self):
        rows = self.rows()
        rows.insert(0, '1-2\tcombined\t_\t_\t_\t_\t_\t_\t_\t_')
        rows.append('4.1\tomitted\t_\tNOUN\t_\t_\t2\tobj\t_\t_')
        self.assertEqual(self.parse(rows), self.parse(self.rows()))


if __name__ == '__main__':
    unittest.main()
