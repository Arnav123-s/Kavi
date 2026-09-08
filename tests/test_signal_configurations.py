"""Execution checks for current-state propagation; no model is taught here."""

from pathlib import Path
import unittest

from kavi.composable_configurations import Configuration,StaleConfiguration,Work
from kavi.published_learning import load_science
from kavi.recurrent_configuration import Configuration as RecurrentConfiguration
from kavi.signal_configurations import HOLD,SignalGraph,SignalExecution,recurrent_execution

ROOT=Path(__file__).resolve().parents[1]


class SignalConfigurationTests(unittest.TestCase):
    def registry(self):
        return load_science(ROOT/'experiments/science-20260907-published-model.json',
            ROOT/'experiments/library-20260907-compiled.json',extended=True).registry

    def test_values_wait_and_then_activate_dependents(self):
        registry=self.registry()
        registry.install('sum_square',Configuration(2,(('add',(0,1)),('multiply',(2,2))),3))
        work=Work()
        graph=SignalGraph.from_registry(registry,'sum_square',work)
        execution=SignalExecution(graph,registry.invoke,work,registry=registry)
        execution.feed(0,4)
        self.assertFalse(execution.settle()['output_available'])
        execution.feed(1,4)
        provisional=execution.settle()
        self.assertFalse(provisional['output_available'])
        self.assertIsNone(provisional['output'])
        self.assertEqual(execution.values[graph.output],64)
        self.assertEqual(execution.values[2],8)
        previous=execution.invocations
        execution.settle()
        self.assertEqual(execution.invocations,previous)
        execution.feed(1,5)
        self.assertFalse(execution.settle()['output_available'])
        execution.finish_input()
        self.assertEqual(execution.status()['output'],81)
        self.assertEqual(execution.status()['live_values'],4)

    def test_held_value_released_by_a_later_input(self):
        registry=self.registry()
        def invoke(name,args,work):
            if name=='release':
                return args[0] if args[1] else HOLD
            return registry.invoke(name,args,work)
        graph=SignalGraph(3,(('add',(0,1)),('release',(3,2)),('multiply',(4,4))),5)
        execution=SignalExecution(graph,invoke,Work())
        execution.feed(0,4);execution.feed(1,4)
        self.assertFalse(execution.settle()['output_available'])
        self.assertEqual(execution.values[3],8)
        execution.feed(2,True)
        execution.finish_input()
        self.assertFalse(execution.status()['output_available'])
        self.assertEqual(execution.settle()['output'],64)

    def test_feedback_loop_does_not_retain_earlier_steps(self):
        def invoke(name,args,work):
            return args[0]-1 if args[0]>0 else HOLD
        graph=SignalGraph(0,(('count_down',(0,)),),0,((0,1000),))
        execution=SignalExecution(graph,invoke,Work())
        execution.finish_input()
        result=execution.settle()
        self.assertEqual(result['output'],0)
        self.assertEqual(result['configuration_calls'],1001)
        self.assertEqual(result['live_values'],1)
        self.assertEqual(result['pending_activations'],0)
        self.assertEqual(len(execution.signatures),1)

    def test_nonterminating_loop_can_be_stopped(self):
        graph=SignalGraph(0,(('continue',(0,)),),0,((0,1),))
        execution=SignalExecution(graph,lambda name,args,work:args[0],Work(limit=100))
        with self.assertRaises(InterruptedError):execution.settle()
        self.assertEqual(len(execution.values),1)

    def test_latest_ports_are_independent_between_invocations(self):
        graph=SignalGraph(1,(('identity',(0,)),),1)
        invoke=lambda name,args,work:args[0]
        first=SignalExecution(graph,invoke,Work())
        second=SignalExecution(graph,invoke,Work())
        first.feed(0,7);first.settle()
        self.assertFalse(second.status()['output_available'])
        self.assertEqual(second.values,{})

    def test_further_input_cannot_change_a_closed_turn(self):
        graph=SignalGraph(1,(('identity',(0,)),),1)
        execution=SignalExecution(graph,lambda name,args,work:args[0],Work())
        execution.feed(0,7)
        execution.finish_input()
        self.assertFalse(execution.status()['output_available'])
        self.assertEqual(execution.settle()['output'],7)
        with self.assertRaises(ValueError):execution.feed(0,8)
        self.assertEqual(execution.status()['output'],7)

    def test_missing_external_input_blocks_the_answer(self):
        graph=SignalGraph(2,(('identity',(0,)),),2)
        execution=SignalExecution(graph,lambda name,args,work:args[0],Work())
        execution.feed(0,7)
        execution.finish_input()
        self.assertFalse(execution.settle()['output_available'])

    def test_replacement_requires_a_new_guarded_invocation(self):
        registry=self.registry()
        work=Work()
        graph=SignalGraph.from_registry(registry,'science_work',work)
        execution=SignalExecution(graph,registry.invoke,work,registry=registry)
        execution.feed(0,3)
        registry.install('science_work',Configuration(2,output=0))
        with self.assertRaises(StaleConfiguration):execution.feed(1,4)

    def test_failed_later_computation_does_not_release_earlier_output(self):
        graph=SignalGraph(1,(('reciprocal',(0,)),),1)
        execution=SignalExecution(graph,lambda name,args,work:1/args[0],Work())
        execution.feed(0,2);execution.settle()
        execution.feed(0,0);execution.finish_input()
        with self.assertRaises(ZeroDivisionError):execution.settle()
        result=execution.status()
        self.assertFalse(result['output_available'])
        self.assertIsNone(result['output'])
        self.assertIn('ZeroDivisionError',result['failure'])

    def test_same_tokens_in_different_orders_keep_distinct_activity(self):
        model=RecurrentConfiguration.decode((ROOT/'experiments/recurrent-20260907-model.json').read_bytes())
        outputs=[]
        for tokens in [('?a','?b','b'),('?b','?a','b')]:
            execution=recurrent_execution(model,Work())
            for token in tokens:
                self.assertFalse(execution.accept(0,token)['output_available'])
            execution.finish_input()
            result=execution.status()
            self.assertEqual(result['output'],model.predict(tokens))
            self.assertEqual(result['live_values'],3)
            self.assertEqual(execution.values[0],'b')
            outputs.append(result['output'])
        self.assertEqual(outputs,[1,0])

    def test_each_repeated_token_is_consumed_once_without_a_history(self):
        model=RecurrentConfiguration.decode((ROOT/'experiments/recurrent-20260907-model.json').read_bytes())
        execution=recurrent_execution(model,Work())
        for _ in range(101):execution.accept(0,'a')
        execution.finish_input()
        self.assertEqual(execution.status()['output'],1)
        self.assertEqual(execution.values[0],'a')
        self.assertEqual(len(execution.values),3)
        self.assertEqual(execution.revisions[1],102)
        self.assertEqual(len(execution.signatures),2)

    def test_unknown_later_token_does_not_release_a_previous_answer(self):
        model=RecurrentConfiguration.decode((ROOT/'experiments/recurrent-20260907-model.json').read_bytes())
        execution=recurrent_execution(model,Work())
        execution.accept(0,'a')
        execution.accept(0,'unknown')
        execution.finish_input()
        self.assertFalse(execution.status()['output_available'])


if __name__=='__main__':unittest.main()
