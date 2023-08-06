# vim: set fileencoding=utf-8 :
import testbase
import unittest
from lpo.expression import expr

class CoversTestCase(unittest.TestCase):
    def setUp(self):
        self.expr2 = expr('corre(q=juan,c=mucho)')

    def tearDown(self):
        #self.set.dispose()
        pass

    def testNegation(self):
        expr1 = expr('~corre(q=juan,c=mucho)')
        self.assertEquals(expr1.true, False)

    def testCoversEqual(self):
        expr1 = expr('corre(q=juan,c=mucho)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs, {})

    def testCoversUnordered(self):
        expr1 = expr('corre(c=mucho, q=juan)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs, {})

    def testCovers(self):
        expr1 = expr('corre(q=X1,c=mucho)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs['X1'].symbol, 'juan')

    def testCoversTwice(self):
        expr1 = expr('corre(q=X1,c=X2)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs['X1'].symbol, 'juan')
        self.assertEquals(vrs['X2'].symbol, 'mucho')

    def testCoversNotDiffNegation(self):
        expr1 = expr('~corre(q=X1,c=X2)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs, False)

    def testCoversNotDiffAtom(self):
        expr1 = expr('corre(q=X1,c=todo)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs, False)

    def testCoversNotOverloadVar(self):
        expr1 = expr('corre(q=X1,c=X1)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs, False)

    def testCoversNotExtraArgsInCoverer(self):
        expr1 = expr('corre(q=X1,c=X2,v=X3)')
        vrs = expr1.covers(self.expr2)
        self.assertEquals(vrs, False)

    def testCoversExtraArgsInCovered(self):
        expr1 = expr('corre(q=X1,c=X2,v=ymas)')
        expr2 = expr('corre(q=juan,c=mucho,v=ymas)')
        vrs = expr1.covers(expr2)
        self.assertEquals(vrs['X1'].symbol, 'juan')
        self.assertEquals(vrs['X2'].symbol, 'mucho')

    def testCoversNotDiffArity(self):
        expr1 = expr('corre(q=X1,c=X2,v=ymas)')
        expr2 = expr('corre(q=juan,c=mucho)')
        vrs = expr1.covers(expr2)
        self.assertEquals(vrs, False)


class SubstituteTestCase(unittest.TestCase):
    def setUp(self):
        self.expr1 = expr('corre(q=X1,c=X2)')

    def tearDown(self):
        #self.set.dispose()
        pass

    def testSimpleSubstitute(self):
        substitution = {'X1': expr('juan')}
        expr3 = self.expr1.substitute(substitution)
        self.assertEquals(repr(expr3), 'corre(c=X2, q=juan)')

    def testDoubleSubstitute(self):
        substitution = {'X1': expr('juan'), 'X2': expr('mucho')}
        expr2 = self.expr1.substitute(substitution)
        self.assertEquals(repr(expr2), 'corre(c=mucho, q=juan)')

    def testReDoubleSubstitute(self):
        expr1 = expr('corre(q=X1,c=X2,v=X1)')
        substitution = {'X1': expr('juan'), 'X2': expr('mucho')}
        expr2 = expr1.substitute(substitution)
        self.assertEquals(repr(expr2), 'corre(c=mucho, q=juan, v=juan)')

    def testTwoVarRepeatedSubstitute(self):
        expr1 = expr('corre(q=X1,c=como(v=X2, r=apido(as=X1), f=uerte))')
        substitution = {'X1': expr('juan'), 'X2': expr('eloz')}
        expr2 = expr1.substitute(substitution)
        self.assertEquals(repr(expr2),
                'corre(c=como(f=uerte, r=apido(as=juan), v=eloz), q=juan)')

def suite():
    alltests = unittest.TestLoader().loadTestsFromTestCase(CoversTestCase)
    for t in (SubstituteTestCase,):
        alltests.addTest(unittest.TestLoader().loadTestsFromTestCase(t))
    return alltests


if __name__ == '__main__':
    testbase.main(suite())