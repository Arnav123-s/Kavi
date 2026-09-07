import itertools
import unittest

from kavi.finite_state_audit import compare
from kavi.recurrent_configuration import Configuration, learn, prefix_configuration


class RecurrentConfigurationTests(unittest.TestCase):
    @staticmethod
    def parity_lessons():
        return [(tokens, tokens.count('a') % 2) for length in range(5)
                for tokens in itertools.product(('a', 'b'), repeat=length)]

    def test_learned_cycles_transfer_beyond_teaching_length(self):
        for seed in (7, 19, 43):
            graph, stats = learn(self.parity_lessons(), seed=seed)
            self.assertEqual(len(graph.outputs), 2)
            self.assertGreater(stats['accepted_merges'], 0)
            self.assertEqual(graph.predict(['b'] * 60 + ['a'] * 101), 1)
            self.assertEqual(graph.predict(['a', 'b'] * 100), 0)
            self.assertTrue(any(step['revisit'] for step in graph.trace('ababa')))

    def test_correction_changes_structure_without_example_records(self):
        evidence = [((), 0), (('b',), 0), (('a', 'a'), 0)]
        before, _ = learn(evidence)
        self.assertEqual(before.predict(('a',)), 0)
        after, _ = learn(evidence + [(('a',), 1)])
        self.assertEqual(after.predict(('a',)), 1)
        self.assertNotEqual(before.encoded(), after.encoded())
        self.assertEqual(set(after.as_dict()), {'format', 'alphabet', 'transitions', 'outputs'})

    def test_serialization_freezes_inference(self):
        graph, _ = learn(self.parity_lessons())
        raw = graph.encoded()
        loaded = Configuration.decode(raw)
        self.assertEqual(loaded.predict('ababaaa'), 1)
        self.assertEqual(loaded.encoded(), raw)
        self.assertIsNone(loaded.predict(['unknown']))
        with self.assertRaises(ValueError):
            Configuration(('a',), ((2,),), (0,))

    def test_unfolded_control_does_not_extrapolate(self):
        control = prefix_configuration(self.parity_lessons())
        self.assertEqual(len(control.outputs), 31)
        self.assertEqual(control.predict('aaba'), 1)
        self.assertIsNone(control.predict('aaaaa'))

    def test_contradictory_evidence_is_not_silently_overwritten(self):
        with self.assertRaisesRegex(ValueError, 'Contradictory'):
            learn([((), 0), ((), 1)])

    def test_budgets_and_cancellation_interrupt_learning(self):
        with self.assertRaisesRegex(RuntimeError, 'Prefix-state'):
            learn(self.parity_lessons(), max_states=2)
        with self.assertRaisesRegex(RuntimeError, 'Merge-proposal'):
            learn(self.parity_lessons(), max_merges=0)
        def stop():
            raise InterruptedError('requested stop')
        with self.assertRaises(InterruptedError):
            learn(self.parity_lessons(), check=stop)

    def test_equivalence_ignores_state_numbering_and_detects_deep_error(self):
        parity = Configuration(('a', 'b'), ((1, 0), (0, 1)), (0, 1))
        redundant = Configuration(('a', 'b'), ((1, 2), (2, 1), (1, 2)), (0, 1, 0))
        self.assertTrue(compare(parity, redundant, ('a', 'b'))['equivalent'])
        # Equal for lengths 0..4, but a difference first appears at length five.
        late = Configuration(('a',), ((1,), (2,), (3,), (4,), (5,), (5,)),
                             (0, 0, 0, 0, 0, 1))
        zero = Configuration(('a',), ((0,),), (0,))
        result = compare(zero, late, ('a',))
        self.assertEqual(result['witness'], ['a'] * 5)
        self.assertFalse(result['equivalent'])

    def test_two_partial_models_do_not_receive_total_equivalence_certificate(self):
        graph = Configuration(('a',), ((-1,),), (0,))
        self.assertEqual(compare(graph, graph, ('a',))['reason'], 'unresolved')

    def test_teacher_can_specify_order_instead_of_parity(self):
        examples = [(seq, int(seq[-2:] == ('a', 'b'))) for n in range(5)
                    for seq in itertools.product(('a', 'b'), repeat=n)]
        graph, _ = learn(examples)
        self.assertEqual(graph.predict('a' * 50 + 'b'), 1)
        self.assertEqual(graph.predict('ab' * 20 + 'a'), 0)
        self.assertEqual(graph.predict('ab' * 20 + 'b'), 0)

    def test_independent_reference_matches_the_label_rule(self):
        from scripts.run_recurrent_configuration import ALPHABET, label, reference, sequences
        oracle = reference()
        for tokens in sequences(ALPHABET, 4):
            self.assertEqual(oracle.predict(tokens), label(tokens))

    def test_new_context_can_require_retaining_previously_irrelevant_input(self):
        from scripts.run_recurrent_configuration import ALPHABET, label, reference, sequences
        old, _ = learn(self.parity_lessons())
        evidence = [(tokens, old.predict(tokens)) for tokens in sequences(('a', 'b'), 4)]
        evidence += [(tokens, label(tokens)) for tokens in sequences(ALPHABET, 4)
                     if '?a' in tokens or '?b' in tokens]
        new, _ = learn(evidence)
        self.assertTrue(compare(old, new, ('a', 'b'))['equivalent'])
        self.assertEqual(new.predict(('b',) * 33 + ('?b',)), 1)
        self.assertEqual(new.predict(('b',) * 33 + ('?a',)), 0)
        # Short teaching data need not identify the whole new task. The live
        # protocol measures that separately after development corrections.
        self.assertTrue(all(new.predict(tokens) == expected for tokens, expected in evidence))


if __name__ == '__main__':
    unittest.main()
