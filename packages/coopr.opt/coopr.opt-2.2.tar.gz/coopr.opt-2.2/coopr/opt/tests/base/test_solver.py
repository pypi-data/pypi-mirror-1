#
# Unit Tests for util/misc
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+"/../.."
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import coopr.opt
import coopr
import pyutilib.services


class TestSolver(coopr.opt.OptSolver):

    def __init__(self, **kwds):
        kwds['type'] = 'stest_type'
        kwds['doc'] = 'TestSolver Documentation'
        coopr.opt.OptSolver.__init__(self,**kwds)

    def enabled(self):
        return False

    
class OptSolverDebug(unittest.TestCase):

    def run(self, result=None):
        self.stest_plugin = coopr.opt.SolverRegistration("stest", TestSolver)
        unittest.TestCase.run(self,result)
        self.stest_plugin.deactivate()

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()


    def test_solver_init1(self):
        """
        Verify the processing of 'type', 'name' and 'doc' options
        """
        ans = coopr.opt.SolverFactory("stest")
        self.failUnlessEqual(type(ans), TestSolver)
        self.failUnlessEqual(ans._doc, "TestSolver Documentation")

        ans = coopr.opt.SolverFactory("stest", doc="My Doc")
        self.failUnlessEqual(type(ans), TestSolver)
        self.failUnlessEqual(ans._doc, "TestSolver Documentation")

        ans = coopr.opt.SolverFactory("stest", name="my name")
        self.failUnlessEqual(type(ans), TestSolver)
        self.failUnlessEqual(ans._doc, "TestSolver Documentation")

    def test_solver_init2(self):
        """
        Verify that options can be passed in.
        """
        opt = {}
        opt['a'] = 1
        opt['b'] = "two"
        ans = coopr.opt.SolverFactory("stest", name="solver_init2", options=opt)
        self.failUnlessEqual(ans.options['a'], opt['a'])
        self.failUnlessEqual(ans.options['b'], opt['b'])

    def test_avail(self):
        ans = coopr.opt.SolverFactory("stest")
        try:
            ans.available()
            self.fail("Expected exception for 'stest' solver, which is disabled")
        except pyutilib.common.ApplicationError:
            pass



if __name__ == "__main__":
   unittest.main()

