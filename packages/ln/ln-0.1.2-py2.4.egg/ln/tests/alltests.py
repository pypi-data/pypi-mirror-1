import testbase
import unittest

import doctests

def suite():
    alltests = unittest.TestSuite()
    for suite in (doctests,):
        alltests.addTest(suite.suite())
    return alltests


if __name__ == '__main__':
    testbase.main(suite())