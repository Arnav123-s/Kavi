import unittest

from kavi.composable_configurations import Configuration, Registry, Work
from kavi.science_course import ScienceModel, Relation, precise, consolidate


class ScienceCourseTests(unittest.TestCase):
    def model(self):
        r=Registry({'mul':lambda a,w:a[0]*a[1],'div':lambda a,w:a[0]/a[1]},'test')
        r.install('mul',Configuration(2,kernel='mul'))
        r.install('div',Configuration(2,kernel='div'))
        r.install('science_product',Configuration(2,(('mul',(0,1)),),2))
        r.install('science_inverse',Configuration(3,(('mul',(1,2)),('div',(0,3))),4))
        r.install('wire',Configuration(1,output=0))
        return ScienceModel(r,[Relation('work',('force','distance'),'science_product'),
            Relation('heat',('work',),'wire','full_thermalization'),
            Relation('delta_temperature',('heat','mass','specific_heat'),'science_inverse')])

    def test_input_dependencies_compose_and_guard_conversion(self):
        m=self.model()
        givens={'force':4.,'distance':3.,'mass':2.,'specific_heat':3.}
        self.assertEqual(m.answer(givens,'delta_temperature',Work())['state'],'unresolved')
        givens['full_thermalization']=True
        answer=m.answer(givens,'delta_temperature',Work())
        self.assertEqual(answer['value'],2.)
        self.assertEqual([x['target'] for x in answer['trace']],['work','heat','delta_temperature'])
        self.assertNotIn('heat',givens)

    def test_unrelated_missing_quantities_are_not_needed(self):
        m=self.model()
        m.relations.insert(0,Relation('unrelated',('unknown',),'wire'))
        self.assertEqual(m.answer({'force':7,'distance':9},'work',Work())['value'],63)
        m.relations.append(Relation('a',('a',),'wire'))
        self.assertEqual(m.answer({},'a',Work())['state'],'unresolved')

    def test_tiny_physical_answers_need_relative_accuracy(self):
        self.assertTrue(precise(9e-31,9e-31))
        self.assertFalse(precise(0.,9e-31))
        self.assertFalse(precise(1e-13,1e-14))
        self.assertFalse(precise(float('nan'),1.))

    def test_only_identical_structures_are_shared(self):
        m=self.model()
        m.registry.install('science_second',m.registry.definitions['science_product'])
        shares=consolidate(m)
        self.assertEqual(len(shares),1)
        for a,b in [(1,2),(5,7),(.2,6.)]:
            self.assertEqual(m.registry.execute('science_second',(a,b),Work()),a*b)


if __name__=='__main__':
    unittest.main()
