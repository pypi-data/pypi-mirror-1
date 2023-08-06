#
# Unit Tests for pyomo.base.misc
#

import unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir= dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
import pyutilib.th

def rule1(model):
    return (1,model.x+model.y[1],2)
def rule2(i,model):
    return (1,model.x+model.y[1]+i,2)

class PyomoModel(pyutilib.th.TestCase):

    def setUp(self):
        self.model = Model()

    def test_construct(self):
        model = Model()
        model.a = Set(initialize=[1,2,3])
        model.A = Param(initialize=1)
        model.B = Param(model.a)
        model.x = Var(initialize=1,within=Reals)
        model.y = Var(model.a, initialize=1,within=Reals)
        model.obj = Objective(rule=lambda model: model.x+model.y[1])
        model.obj2 = Objective(model.a,rule=lambda i,model: i+model.x+model.y[1])
        model.con = Constraint(rule=rule1)
        model.con2 = Constraint(model.a, rule=rule2)
        instance = model.create()
        expr = instance.x + 1
        instance.reset()
        OUTPUT = open(currdir+"display.out","w")
        display(instance,ostream=OUTPUT)
        display(instance.obj,ostream=OUTPUT)
        display(instance.x,ostream=OUTPUT)
        display(instance.con,ostream=OUTPUT)
        expr.pprint(ostream=OUTPUT)
        model = Model()
        instance = model.create()
        display(instance,ostream=OUTPUT)
        OUTPUT.close()
        try:
            display(None)
            self.fail("test_construct - expected TypeError")
        except TypeError:
            pass
        self.failUnlessFileEqualsBaseline(currdir+"display.out",currdir+"display.txt")

if __name__ == "__main__":
   unittest.main()
