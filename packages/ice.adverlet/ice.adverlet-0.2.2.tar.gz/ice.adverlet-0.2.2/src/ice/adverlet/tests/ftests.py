### -*- coding: utf-8 -*- ############################################
### Author: Ilshad Habibullin, 2008 <astoon.net@gmail.com> ###########
######################################################################

__license__ = "GPL v.3"

import unittest
from zope.app.testing import functional

try:
    from z3c import sampledata
    sampledata = True
except ImportError:
    sampledata = False

functional.defineLayer('TestLayer', 'ftesting.zcml')

def setUp(test):
    pass

def tearDown(test):
    pass

def test_suite():
    suite = unittest.TestSuite()
    if not sampledata:
        return suite
    suites = (functional.FunctionalDocFileSuite(
            'ftests.txt', setUp=setUp, tearDown=tearDown
            ),)

    for s in suites:
        s.layer=TestLayer
        suite.addTest(s)

    return suite

    
