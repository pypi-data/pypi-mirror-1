import testbase
import unittest

import doctests
import testexpression
import testexpressionset

def suite():
    alltests = unittest.TestSuite()
    for suite in (doctests, testexpression, testexpressionset):
        alltests.addTest(suite.suite())
    return alltests


if __name__ == '__main__':
    testbase.main(suite())