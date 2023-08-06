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
from coopr.pyomo.base import expr, _VarBase, Var, Constraint, Objective
from coopr.pyomo.base.var import _VarValue, VarStatus
from coopr.pyomo.base.numvalue import NumericConstant
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction


class IdentifyVariablesPresolver(pyutilib.plugin.core.SingletonPlugin):
    """
    This plugin processes a Pyomo Model instance to define
    the order of variables and to categorize constraints.
    """

    pyutilib.plugin.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "identify_variables"
        pyutilib.plugin.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 1

    #
    # Recursively work through an exression to identify variables.
    #
    def _identify_variables(self, exp, model):
        if exp.fixed_value():
            return
        #
        # Product Expressions store stuff differently
        #
        if type(exp) is expr._ProductExpression:
            for arg in exp._numerator:
                self._identify_variables(arg, model)
            for arg in exp._denominator:
                self._identify_variables(arg, model)
        #
        # Expression
        #
        elif isinstance(exp,expr.Expression):
            for arg in exp._args:
                self._identify_variables(arg, model)
        #
        # Variable Value
        #
        elif isinstance(exp,_VarValue) or isinstance(exp,_VarBase):
            exp.status = VarStatus.used
            if isinstance(exp,_VarValue):
                if exp.id in model._var:
                    return
                exp.id = self.vnum
                model._var[self.vnum] = exp
            else:
                tmp = exp.as_numeric()
                if tmp is exp:
                    raise ValueError, "Variable %s appears in an expression without an index, but this variable is an indexed value." % exp.name
                if tmp.id in model._var:
                    return
                tmp.id = self.vnum
                model._var[self.vnum] = tmp
            if model._var[self.vnum].is_binary():
                model.statistics.number_of_binary_variables += 1
            elif model._var[self.vnum].is_integer():
                model.statistics.number_of_integer_variables += 1
            else:
                model.statistics.number_of_continuous_variables +=1
            self.vnum += 1
        #
        # If not a constant, then this is an error
        #
        elif exp is not None:
            raise ValueError, "Unexpected expression type in identify_variables: " + str(type(exp))+" "+str(exp)


    def presolve(self,model):
        """
        The main routine to perform the presolve
        """
        Vars = model.active_components(Var)
        Con = model.active_components(Constraint)
        Obj = model.active_components(Objective)
        self.vnum=0
        self.cnum=0
        self.onum=0
        model.statistics.number_of_binary_variables = 0
        model.statistics.number_of_integer_variables = 0
        model.statistics.number_of_continuous_variables = 0
        #
        # Indicate that all variables are unused
        #
        for var in Vars.values():
            for V in var._varval.keys():
                var._varval[V].status = VarStatus.unused
                var._varval[V].id = -1
        #
        # Call identify_variables to find the variables that are used in 
        # the objective and constraints
        #
        for key in Obj.keys():
            for ondx in Obj[key]._data:
                if not Obj[key]._data[ondx].active:
                    continue
                try:
                    self._identify_variables(Obj[key]._data[ondx].expr, model)
                except ValueError, err:
                    raise "Problem processing objective %s (index %s): %s" % (str(key), str(ondx), str(err))

                Obj[key]._data[ondx].id = self.onum
                self.onum += 1
        for key in Con.keys():
            C = Con[key]
            for cndx in C.keys():
                if not C._data[cndx].active:
                    continue
                try:
                    self._identify_variables(C._data[cndx].body, model)
                except ValueError, err:
                    raise "Problem processing constraint %s (index %s): %s" % (str(key), str(cndx), str(err))
                C._data[cndx].id = self.cnum
                model._con[self.cnum] = C._data[cndx]
                self.cnum += 1
        model.statistics.number_of_variables=self.vnum
        model.statistics.number_of_constraints=self.cnum
        model.statistics.number_of_objectives=self.onum
        return model

