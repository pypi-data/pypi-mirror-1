import unittest

import TestCurry

def additional_tests():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCurry.TestCase, 'test'))
    return suite

