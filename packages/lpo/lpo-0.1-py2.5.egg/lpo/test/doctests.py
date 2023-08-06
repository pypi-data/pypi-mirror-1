import os,sys
import glob
import testbase
import unittest
import doctest
from lpo import expression, rule


def suite():
    alltests = unittest.TestSuite()
    for mod in (expression, rule):
        alltests.addTest(doctest.DocTestSuite(mod))
    for filename in glob.glob('../doc/*.txt'):
        alltests.addTest(doctest.DocFileSuite(filename))
    return alltests


if __name__ == '__main__':
    testbase.main(suite())