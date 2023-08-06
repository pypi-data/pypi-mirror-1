#
# Unit Tests for model preprocessing
#

import unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
currdir = dirname(abspath(__file__))+os.sep

import pyutilib.th
from coopr.pyomo import *
from nose.tools import nottest


class TestPreprocess(pyutilib.th.TestCase):

    def test_label1(self):
        model = Model()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        instance=model.create()
        instance.presolve()
        self.failUnlessEqual(instance.num_used_variables(),0)

    def test_label1(self):
        model = Model()
        model.A = Set(initialize=[1,2,3])
        model.B = Param(model.A,initialize={1:100,2:200,3:300})
        model.x = Var(model.A)
        model.y = Var(model.A)
        model.obj = Objective(rule=lambda inst: inst.x[1])
        instance=model.create()
        instance.presolve()
        self.failUnlessEqual(instance.num_used_variables(),1)
        self.failUnlessEqual(instance.x[1].label,"x[1]")
        self.failUnlessEqual(instance.x[2].label,"x[2]")
        self.failUnlessEqual(instance.y[1].label,"y[1]")

if __name__ == "__main__":
   unittest.main()
