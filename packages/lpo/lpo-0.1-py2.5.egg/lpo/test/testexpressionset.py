# vim: set fileencoding=utf-8 :
import testbase
import unittest
import sqlalchemy as sa
from lpo import expressionset as es,tables as ta,rule as ru,expression as ex

class ExprSetTestCase(unittest.TestCase):

    def setUp(self):

        self.s1 = es.add_expr('esun(e=juan, c=hombre)')

        self.s2 = es.add_expr('es(c=animal, s=hombre)')

        self.s3 = es.add_expr('es(s=animal, c=cosa)')

        self.r1 = es.add_rule(ru.Rule(prems=(ex.expr('esun(e=X1, c=X2)'),
                                             ex.expr('es(s=X2, c=X3)')),
                                       cons=(ex.expr('esun(e=X1, c=X3)'),)))

        self.r2 = es.add_rule(ru.Rule(prems=(ex.expr('es(s=X1, c=X2)'),
                                             ex.expr('es(s=X2, c=X3)')),
                                       cons=(ex.expr('es(s=X1, c=X3)'),)))

    def tearDown(self):
        #self.set.dispose()
        ta.proofs.delete().execute()
        ta.expressions.delete().execute()
        ta.rules.delete().execute()
        ta.counters.delete().execute()
        ta.session.clear()


    def testExprSetReprBasicExpr(self):
        self.assertEquals(repr(self.s1), 'esun(c=hombre, e=juan)')

    def testExprSetReprRule(self):
        self.assertEquals(self.r1.name,
                'es(c=X3,s=X2);esun(c=X2,e=X1)-->esun(c=X3,e=X1)')

    def testExprSetGetSameExpr(self):
        s1 = es.get_same_expr(ex.expr('esun(e=juan, c=hombre)'))
        self.assertEquals(repr(s1), 'esun(c=hombre, e=juan)')

    def testExprSetNotGetSameExpr(self):
        s1 = es.get_same_expr(ex.expr('esun(e=julio, c=hombre)'))
        self.assertEquals(repr(s1), 'None')

    def testExprSetDiffEquals(self):
        s1 = es.get_same_expr(ex.expr('esun(e=juan, c=hombre)'))
        self.assertTrue(s1 is self.s1)

    def testExprSetAddTwoBasicExpr(self):
        s1 = es.add_expr('esun(e=juan, c=hombre)')
        self.assertTrue(s1 is self.s1)

    def testExprSetAskTruth(self):
        self.assertEquals(repr(es.ask('esun(e=juan, c=hombre)')),
                                        'esun(c=hombre, e=juan)')

        self.assertEquals(repr(es.ask('esun(e=julio, c=cosa)')),
                                        'False')

    def testExprSetExtend(self):
        count = ta.session.query(ex.Expression).count()
        es.extend()
        self.assertTrue(ta.session.query(ex.Expression).count() > count)

    def testExprSetExtendTwice(self):
        es.extend()
        count = ta.session.query(ex.Expression).count()
        es.extend()
        self.assertEquals(ta.session.query(ex.Expression).count(), count)

    def testExprSetAskTruthExtended(self):
        es.extend()
        self.assertEquals(repr(es.ask('esun(e=juan, c=animal)')),
                                        'esun(c=animal, e=juan)')

        self.assertEquals(repr(es.ask('esun(e=juan, c=cosa)')),
                                        'esun(c=cosa, e=juan)')

        self.assertEquals(repr(es.ask('esun(e=julio, c=cosa)')),
                                        'False')

    def testExprSetContradiction(self):
        es.add_expr('~esun(e=juan, c=cosa)')
        self.assertRaises(es.ParadoxError, es.extend)

    def testExprSetDelete(self):
        es.extend()

        self.assertEquals(repr(es.ask('esun(e=juan, c=cosa)')),
                                        'esun(c=cosa, e=juan)')

        es.delete('esun(e=juan, c=hombre)')

        self.assertEquals(repr(es.ask('esun(e=juan, c=cosa)')),
                                        'False')

class ExprSetArithTestCase(unittest.TestCase):

    def setUp(self):

        self.s1 = es.add_expr('esun(e=8, c=5)')

        self.r1 = es.add_rule(ru.Rule(prems=(ex.expr('esun(e=X1, c=X2)'),),
                       cons=(ex.expr('sobra(q=X1, c=dif(a1=X2, a2=2))'),)))

        self.r1 = es.add_rule(ru.Rule(prems=(ex.expr('esun(e=X1, c=X2)'),),
                       cons=(ex.expr('lt(a1=X2, a2=X1)'),)))

    def tearDown(self):
        #self.set.dispose()
        ta.proofs.delete().execute()
        ta.expressions.delete().execute()
        ta.rules.delete().execute()
        ta.counters.delete().execute()
        ta.session.clear()


    def testExprSetBasicSum(self):
        es.extend()
        self.assertEquals(repr(es.ask('sobra(q=8, c=3)')),
                                        'sobra(c=3, q=8)')


    def testExprSetParadox(self):
        self.s1 = es.add_expr('esun(e=3, c=5)')
        self.assertRaises(es.ParadoxError, es.extend)


def suite():
    alltests = unittest.TestLoader().loadTestsFromTestCase(ExprSetTestCase)
    for t in (ExprSetArithTestCase,):
        alltests.addTest(unittest.TestLoader().loadTestsFromTestCase(t))
    return alltests


if __name__ == '__main__':
    testbase.main(suite())