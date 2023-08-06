#
# Test the canonical expressions 
#

import unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+"..")
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
from coopr.opt import *
#from coopr.pyomo.base.var import _VarElement
import pyutilib.th
import pyutilib.services
from coopr.pyomo.presolve.simple_presolver import SimplePresolver
from pyutilib.plugin.core import PluginGlobals

class frozendict(dict):
    __slots__ = ('_hash',)
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval


class TestBase(pyutilib.th.TestCase):

    def setUp(self):
        self.model = Model()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class Test(TestBase):

    def setUp(self):
        #
        # Create Model
        #
        TestBase.setUp(self)
        #PluginGlobals.pprint()
        self.plugin = SimplePresolver()
        self.plugin.deactivate_action("collect_linear_terms")

    def tearDown(self):
        if os.path.exists("unknown.lp"):
           os.unlink("unknown.lp")
        pyutilib.services.TempfileManager.clear_tempfiles()
        self.plugin.activate_action("collect_linear_terms")

    def test_expr1(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.p, model.x)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), {1: {frozendict({2: 1}): 6.0, frozendict({1: 1}): 4.0, frozendict({3: 1}): 8.0, frozendict({0: 1}): 2.0}})

    def test_expr2(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.x, model.p)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), {1: {frozendict({2: 1}): 6.0, frozendict({1: 1}): 4.0, frozendict({3: 1}): 8.0, frozendict({0: 1}): 2.0}})

    def test_expr3(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return 2*model.x[1] + 3*model.x[1] + 4*(model.x[1]+model.x[2])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), 
                    {1: {frozendict({0: 1}):9.0, frozendict({1: 1}):4.0}})

    def test_expr4(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return 1.2 + 2*model.x[1] + 3*model.x[1]
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), {0:frozendict({None:1.2}), 1: {frozendict({0: 1}): 5.0}})

    def test_expr5(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return model.x[1]*(model.x[1]+model.x[2]) + model.x[2]*(model.x[1]+3.0*model.x[3]*model.x[3])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), 
                {2: {frozendict({0:2}):1.0, frozendict({0:1, 1:1}):2.0}, 3:{frozendict({1:1,2:2}):3.0}})

    def test_expr6(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return 2.0*(1.2 + 2*model.x[1] + 3*model.x[1]) + 3.0*(1.0+model.x[1])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), 
            {0:frozendict({None:5.4}), 1: {frozendict({0: 1}): 13.0}})

    def test_expr7(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        def obj_rule(model):
            return summation(model.p, model.x)/2.0
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), 
            {1: {frozendict({2: 1}): 3.0, frozendict({1: 1}): 2.0, frozendict({3: 1}): 4.0, frozendict({0: 1}): 1.0}})

    def test_expr8(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=2.0)
        def obj_rule(model):
            return summation(model.p, model.x)/model.y
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.y.fixed = True
        self.instance.y.reset()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), 
            {1: {frozendict({2: 1}): 3.0, frozendict({1: 1}): 2.0, frozendict({3: 1}): 4.0, frozendict({0: 1}): 1.0}})

    def test_expr9(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return summation(model.p, model.x)/(1+model.y)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        self.instance.y.fixed = True
        self.instance.y.reset()
        #self.instance.obj[None].expr.pprint()
        self.failUnlessEqual(generate_canonical_repn(self.instance.obj[None].expr, self.instance), 
            {1: {frozendict({2: 1}): 3.0, frozendict({1: 1}): 2.0, frozendict({3: 1}): 4.0, frozendict({0: 1}): 1.0}})

    def test_expr10(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return summation(model.p, model.x)/(1+model.y)
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr, self.instance)
        self.failUnless(len(rep) == 1 and None in rep)

    def test_expr11(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return (1.0+model.x[1]+1/model.x[2]) + (2.0+model.x[2]+1/model.x[3])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr, self.instance)
        rep[None].pprint()
        del rep[None]
        self.failUnlessEqual(rep, {0: {None: 3.0}, 1: {frozendict({1: 1}): 1.0, frozendict({0: 1}): 1.0}})

    def test_expr12(self):
        self.model.A = RangeSet(1,4)
        def p_init(i, model):
            return 2*i
        self.model.p = Param(self.model.A, initialize=p_init)
        self.model.x = Var(self.model.A, bounds=(-1,1))
        self.model.y = Var(initialize=1.0)
        def obj_rule(model):
            return (1.0+model.x[1]+1/model.x[2]) * (2.0+model.x[2]+1/model.x[3])
        self.model.obj = Objective(rule=obj_rule)
        self.instance = self.model.create()
        #self.instance.obj[None].expr.pprint()
        rep = generate_canonical_repn(self.instance.obj[None].expr, self.instance)
        rep[None].pprint()
        del rep[None]
        self.failUnlessEqual(rep, {0: {None: 2.0}, 1: {frozendict({1: 1}): 1.0, frozendict({0: 1}): 2.0}, 2: {frozendict({0: 1, 1: 1}): 1.0}})

if __name__ == "__main__":
   unittest.main()

