#
# Unit Tests for model transformations
#

import unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
from coopr.opt import *
import pyutilib.th
import pyutilib.services
from pyutilib.plugin.core import Plugin

class Test(pyutilib.th.TestCase):

    def setUp(self):
        self.model = Model()

    def tearDown(self):
        if os.path.exists("unknown.lp"):
           os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_relax_integrality1(self):
        """ Coverage of the _clear_attribute method """
        self.model.A = RangeSet(1,4)
        self.model.a = Var()
        self.model.b = Var(within=self.model.A)
        self.model.c = Var(within=NonNegativeIntegers)
        self.model.d = Var(within=Integers, bounds=(-2,3))
        self.model.e = Var(within=Boolean)
        self.model.f = Var(domain=Boolean)
        instance=self.model.create()
        rinst = apply_transformation('relax_integrality',instance)
        self.failUnlessEqual(type(rinst.a.domain), type(Reals))
        self.failUnlessEqual(type(rinst.b.domain), type(Reals))
        self.failUnlessEqual(type(rinst.c.domain), type(Reals))
        self.failUnlessEqual(type(rinst.d.domain), type(Reals))
        self.failUnlessEqual(type(rinst.e.domain), type(Reals))
        self.failUnlessEqual(type(rinst.f.domain), type(Reals))
        self.failUnlessEqual(rinst.a.bounds, instance.a.bounds)
        self.failUnlessEqual(rinst.b.bounds, instance.b.bounds)
        self.failUnlessEqual(rinst.c.bounds, instance.c.bounds)
        self.failUnlessEqual(rinst.d.bounds, instance.d.bounds)
        self.failUnlessEqual(rinst.e.bounds, instance.e.bounds)
        self.failUnlessEqual(rinst.f.bounds, instance.f.bounds)

    def test_apply_transformation1(self):
        self.failUnless('relax_integrality' in apply_transformation())

    def test_apply_transformation2(self):
        self.failUnlessEqual(apply_transformation('foo'),None)
        self.failUnless(isinstance(apply_transformation('relax_integrality'),Plugin))
        self.failUnless(isinstance(apply_transformation('relax_integrality'),Plugin))
        self.failUnlessEqual(apply_transformation('foo', self.model),None)

if __name__ == "__main__":
   unittest.main()

