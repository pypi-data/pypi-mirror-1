from __future__ import with_statement

import os
import sys

import unittest
import logging
import pickle

sys.path.insert(0, os.getenv('CURRYPY_HOME'))

import currypy as CurryModule

def foo(a, b=3):
    return a*b 


class TestCase(unittest.TestCase):
    """
    """

    def setUp(self):

        self._path = '/tmp/TestCurry'
        return
    
    def tearDown(self):
        os.unlink(self._path)
        
        return
    
    
    def testPickle1(self):

        curriedObj = CurryModule.Curry(foo, 2, b=5)
        dumped = False
        with open(self._path, 'w') as f:
            pickle.dump(curriedObj, f)
            dumped =True
        assert dumped

        loaded = False
        with open(self._path, 'r') as f:
            curried = pickle.load(f)
            assert curried() is 10
            loaded = True
        assert loaded

        return

    def testPickle2(self):

        curriedObj = CurryModule.Curry(foo, 2)
        dumped = False
        with open(self._path, 'w') as f:
            pickle.dump(curriedObj, f)
            dumped =True
        assert dumped

        loaded = False
        with open(self._path, 'r') as f:
            curried = pickle.load(f)
            assert curried(b=7) is 14
            loaded = True
        assert loaded

        return


    def testPickle3(self):

        curriedObj = CurryModule.Curry(foo, b=5)
        dumped = False
        with open(self._path, 'w') as f:
            pickle.dump(curriedObj, f)
            dumped =True
        assert dumped

        loaded = False
        with open(self._path, 'r') as f:
            curried = pickle.load(f)
            assert curried(7) is 35
            loaded = True
        assert loaded

        return

        
    # END class TestPickle
    pass


def main():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase, 'test'))
    
    runner = unittest.TextTestRunner()
    runner.run(suite)
    return

if __name__=="__main__":
    main()

