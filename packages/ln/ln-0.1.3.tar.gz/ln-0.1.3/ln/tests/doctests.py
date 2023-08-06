import os,sys
import glob
import testbase
import unittest
import doctest


def suite():
    alltests = unittest.TestSuite()
    for filename in glob.glob('../doc/*.txt'):
        alltests.addTest(doctest.DocFileSuite(filename))
    return alltests


if __name__ == '__main__':
    testbase.main(suite())