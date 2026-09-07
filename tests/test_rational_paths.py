"""Independent rational arithmetic and execution-budget checks."""

from fractions import Fraction
from pathlib import Path
import unittest

from kavi.procedure_core import ProcedureLibrary,Limits,ExecutionLimit
from kavi.rational_paths import RationalLibrary


def backend():
    source=ProcedureLibrary.load(Path(__file__).resolve().parents[1]/'experiments/library-20260907-compiled.json')
    return ProcedureLibrary(p for n,p in source.procedures.items() if n in {'add','subtract','multiply'})


class RationalTests(unittest.TestCase):
    def test_finite_disjoint_rational_partitions(self):
        from scripts.run_rational_curriculum import partitions
        for arity in (1,2,3):
            train,final=partitions(arity,71)
            self.assertEqual(len(train),8)
            self.assertEqual(len(final),12 if arity==1 else 24)
            self.assertFalse(set(train)&set(final))
            self.assertEqual(len(set(final)),len(final))
    def test_all_signs_and_denominators(self):
        lib=RationalLibrary(backend())
        values={Fraction(n,d) for n in (-7,-2,-1,0,1,3,8) for d in (1,2,5)}
        for a in values:
            for b in values:
                for name,expected in [('add',a+b),('subtract',a-b),('multiply',a*b)]+([('divide',a/b)] if b else []):
                    self.assertEqual(lib.apply('call',name,(a,b)).value,expected)

    def test_composition_and_round_trip(self):
        lib=RationalLibrary(backend())
        lib.add('affine',3,('call','add',('call','multiply',('arg',0),('arg',1)),('arg',2)))
        restored=RationalLibrary.from_dict(lib.to_dict())
        self.assertEqual(restored.apply('call','affine',(Fraction(-1,2),Fraction(2,3),Fraction(1,6))).value,Fraction(-1,6))
        self.assertEqual(restored.encoded(),lib.encoded())

    def test_invalid_inputs_and_resource_limits(self):
        lib=RationalLibrary(backend())
        with self.assertRaises(ValueError): lib.apply('call','divide',(1,0))
        with self.assertRaises(ValueError): lib.apply('call','add',(0.5,1))
        with self.assertRaises(ExecutionLimit): lib.apply('call','multiply',(3,7),limits=Limits(max_gates=0))
        with self.assertRaises(ExecutionLimit): lib.apply('call','add',(3,7),limits=Limits(max_calls=1))


if __name__=='__main__': unittest.main()
