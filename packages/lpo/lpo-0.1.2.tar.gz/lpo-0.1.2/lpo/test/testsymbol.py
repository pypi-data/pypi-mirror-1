# vim: set fileencoding=utf-8 :
import testbase
import unittest
from lpo.symbol import Symbol

class SymbolTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        #self.set.dispose()
        pass

    def testSymbol(self):
        sym = Symbol('one',2)
        self.assertEquals(sym.name, 'one')
        self.assertEquals(sym.arity, 2)


def suite():
    alltests = unittest.TestLoader().loadTestsFromTestCase(SymbolTestCase)
    return alltests


if __name__ == '__main__':
    testbase.main(suite())