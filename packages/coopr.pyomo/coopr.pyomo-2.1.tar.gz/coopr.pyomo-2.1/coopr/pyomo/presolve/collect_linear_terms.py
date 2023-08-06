#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________


import pyutilib.plugin.core
from coopr.pyomo.base import expr, Var, Constraint, Objective
from coopr.pyomo.base.numvalue import NumericConstant
from coopr.pyomo.base.var import _VarValue
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction

import string
import StringIO


class CollectLinearTerms(pyutilib.plugin.core.SingletonPlugin):
    """
    This plugin processes a Pyomo Model instance to collect 
    linear terms.
    """

    pyutilib.plugin.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "collect_linear_terms"
        pyutilib.plugin.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 10000

    #
    # Identify variables and confirm that the expression is linear
    #
    def _Collect2(self, exp, x, scale=1.0):
        #
        # Ignore identity expressions
        #
        while isinstance(exp,expr._IdentityExpression):
            exp = exp._args[0]
        #
        # Expression
        #
        if isinstance(exp,expr.Expression):
           #
           # Sum
           #
           if isinstance(exp,expr._SumExpression):
              for i in xrange(len(exp._args)):
                x = self._Collect2(exp._args[i], x, scale*exp._coef[i])
              c = exp._const * scale
              if "0" in x:
                   xv = x["0"]
                   x["0"] = (xv[0]+c,xv[1])
              else:
                   x["0"] = (c,"0")
           #
           # Product
           #
           elif isinstance(exp,expr._ProductExpression):
              c = scale * exp.coef
              ve = v = "0"
              for e in exp._numerator:
                 if e.fixed_value():
                     # at this point, we have checked that the expression has a fixed value.
                     # however, that check isn't particularly strong, as the "fixedness" of
                     # something is typically a function of the class, e.g., numeric values or
                     # parameter values. it is currently possible to specify expressions for
                     # parameter values, which is something to warn on and completely chokes
                     # the presolve.
                     if isinstance(e.value, expr.Expression):
                        value_as_string = StringIO.StringIO()
                        e.value.pprint(ostream=value_as_string)
                        raise AttributeError, "Expression encountered where fixed value (probably a parameter) was expected - offending subexpression="+string.strip(value_as_string.getvalue())
                     c *= e.value
                 else:
                     if not v is "0":
                         raise ValueError, "Nonlinear expression: found two non-fixed variables in ProductExpression"
                     if hasattr(e, "label") is False:
                        expression_string = StringIO.StringIO()
                        e.pprint(ostream=expression_string)
                        msg = "No label for expression object="+string.strip(expression_string.getvalue())+" of type="+str(type(e))
                        raise AttributeError, msg
                     v = e.label
                     ve = e
              for e in exp._denominator:
                   if e.fixed_value():
                       c /= e.value
                   elif e.is_constant():
                      # This is experimental, based on issues with logically valid 
                      # expressions being flagged as "nonlinear, with variables". 
                      try:
                         c /= e()
                      except ZeroDivisionError:
                         print "Divide-by-zero error - offending sub-expression:"
                         e.pprint()
                         raise ZeroDivisionError                        
                   else:
                       print "***Error identified with expression=",e
                       raise ValueError, "Nonlinear expression: found variable in denominator"
              if v in x:
                 xv = x[v]
                 x[v] = (xv[0]+c,xv[1])
              else:
                 x[v] = (c,ve)
           #
           # ERROR
           #
           else:
              raise ValueError, "Unsupported expression type: "+str(exp)
        #
        # Constant
        #
        elif exp.fixed_value():
           c = exp.value * scale
           if "0" in x:
              xv = x["0"]
              x["0"] = (xv[0]+c,xv[1])
           else:
              x["0"] = (c,"0")
        #
        # Variable
        #
        elif isinstance(exp,_VarValue):
          v = exp.label
          if v in x:
               xv = x[v]
               x[v] = (xv[0] + scale, xv[1])
          else:
               x[v] = (scale, exp)
        #
        # ERROR
        #
        else:
           raise ValueError, "Unexpected expression type in _Collect2:"+str(exp)
        return x

    def _Collect3(self, exp):
        """
        The highest-level linear term collection process for an expression.
        Pretty much just a simple filter over _Collect2.
        """
        # the 'x' is just a dictonary mapping variable names to (coefficient, VarValue) pairs.
        x = self._Collect2(exp,{})
        # the 'y' is just a reduction of 'x' that eliminates entries with coefficients = 0.0.
        y = {}
        for i in x:
           if x[i][0] != 0.:
              y[i] = x[i]
        return y

    def presolve(self,model):
        """
        The main routine to perform the presolve
        """
        #Vars = model.active_components(Var)
        Con = model.active_components(Constraint)
        Obj = model.active_components(Objective)
        #
        # Collect the linear terms
        #
        # Objectives
        #
        Obj1 = []
        for key in Obj.keys():
            obj = Obj[key]
            obj._linterm = {}
            Onz = []
            nt = 0
            for ondx in obj._data:
                if not obj._data[ondx].active:
                    continue
                if obj._data[ondx].expr is None:
                    raise ValueError, "No expression has been defined for objective %s" % str(key)
                t = obj._linterm[ondx] = self._Collect3(obj._data[ondx].expr)
                lt = len(t)
                if lt > 0:
                    Onz.append(ondx)
                    nt += 1
            if nt > 0:
                Obj1.append(key)
            obj._Onz = Onz
        model.Onontriv = Obj1
        #
        # Constraints
        #

        # there are currently expressions within pyomo that the collect routines
        # have issues with - most notably, _SumExpression objects not having labels
        # (which of course they don't). we are working to fix this issue, but in
        # the meantime, we are providing a bit more context regarding which specific
        # constraint is causing the issue.

        # a model maintains a list of constraints with at least one non-empty expression index.
        # attribute is "Cnontriv" - see set below.
        Con1 = [] 
        for key in Con.keys():
           C = Con[key]
           # for each constraint, a map between each index and the associated linear term construct.              
           C._linterm = {}
           # each constraint tracks a list of the indices with non-empty expressions.
           # attribute is _Cnz - see set below.              
           Cnz = [] 
           nt = 0 # track number of constraint indicies with non-trivial bodies
           for cndx in C.keys():
              if not C._data[cndx].active:
                    continue
                  
#              print "Collecting linear terms for constraint="+key+"["+str(cndx)+"]"
#              junk = StringIO.StringIO()
#              C._data[cndx].body.pprint(ostream=junk)                 
#              print "CONSTRAINT BODY:"+string.strip(junk.getvalue())

              try:                 
                 t = C._linterm[cndx] = self._Collect3(C._data[cndx].body)
              except AttributeError, msg:
                 print "***Error encountered in class CollectLinearTerms, method=presolve, encountered when invoking _Collect3 on constraint="+key+"["+str(cndx)+"]"
                 constraint_as_string = StringIO.StringIO()
                 C._data[cndx].body.pprint(ostream=constraint_as_string)                                  
                 print "***Constraint body:"+string.strip(constraint_as_string.getvalue())
                 print "***Problem: "+str(msg)
                 raise RuntimeError
                 
              if len(t) > 0:
                 Cnz.append(cndx)
                 nt += 1
                    
           if nt > 0:
              Con1.append(key)
           C._Cnz = Cnz
        model.Cnontriv = Con1

        #
        # Return modified instance
        #
        return model

