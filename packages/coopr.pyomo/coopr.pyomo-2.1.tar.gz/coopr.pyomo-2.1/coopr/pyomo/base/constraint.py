#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Objective', 'Constraint']

from numvalue import *
from numvalue import create_name
from expr import *
from plugin import ComponentRegistration
import pyomo
from var import Var, _VarValue
from indexed_component import IndexedComponent
from sets import _BaseSet
import pyutilib.misc
import pyutilib.math
from numtypes import *
import sys
from set_types import *


class ObjectiveData(NumericValue):

    def __init__(self, expr=None, name=None):
        NumericValue.__init__(self,name=name,domain=Reals)
        self.expr = expr
        self.label = None
        self.id = -1
        self.active = True

    def __call__(self, exception=True):
        if self.expr is None:
            return None
        return self.expr()

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False


class Objective(NumericValue, IndexedComponent):
    """An object that defines a objective expression"""

    def __init__(self, *args, **kwd):
        """Construct an objective expression with rule to construct the
           expression
        """
	tkwd = {'ctype':Objective}
        IndexedComponent.__init__(self, *args, **tkwd)
        tmpname="unknown"
        tmpsense = minimize
        tmprule = None
        self._data = {}
        if args == ():
           self._data[None] = ObjectiveData()
        self._quad_subexpr = None # this is a hack for now; we eventually want a "QuadraticObjective" class.        
        for key in kwd.keys():
          if key == "name":
             tmpname=kwd[key]
          elif key == "doc":
             self.doc=kwd[key]
          elif key == "rule":
             tmprule = kwd[key]
          elif key == "sense":
             tmpsense = kwd[key]
          else:
             raise ValueError, "Objective constructor: unknown keyword - "+key
        NumericValue.__init__(self,name=tmpname)
        if None in self._data:
            self._data[None].name = tmpname
        self.sense = tmpsense
        self.rule = tmprule

    def __call__(self, exception=True):
        if len(self._data) == 0:
            return None
        if None in self._data:
            if self._data[None].expr is None:
                return None
            return self._data[None].expr()
        if exception:
            raise ValueError, "Cannot compute the value of an array of objectives"

    def dim(self):
        return self._ndim

    def __len__(self):
        return len(self._data.keys())

    def keys(self):
        return self._data.keys()
        #return self._index

    def __contains__(self,ndx):
        return ndx in self._data
        #return ndx in self._index

    def __getitem__(self,ndx):
        """This method returns a ObjectiveData object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        if ndx in self._data:
           return self._data[ndx]
        raise KeyError, "Unknown index " + str(ndx) + " in objective " + self.name

    def __iter__(self):
        return self._data.keys().__iter__()
        #return self._index.__iter__()

    def _apply_rule(self,arg,ndx):
        tmp = self.rule(*arg)
        if tmp is None:
           return None
        if type(tmp) in [bool,int,long,float]:
           return NumericConstant(value=tmp)
        return tmp

    def construct(self, data=None):
        if self.rule is not None:
           if self._ndim==0:
              tmp = self._apply_rule((self.model,),None)
              if not tmp is None and not (type(tmp) in [int,long,float] and tmp == 0):
                 self._data[None].expr = tmp
           else:
              _name=self.name
              for val in self._index:
                if type(val) is tuple:
                   tmp = list(val)
                else:
                   tmp = [val]
                tmp.append(self.model)
                tmp = tuple(tmp)
                tmp = self._apply_rule(tmp,val)
                if not tmp is None and not (type(tmp) in [int,long,float] and tmp == 0):
                   self._data[val] = ObjectiveData(expr=tmp, name=create_name(_name,val))
           #self._index = self._data.keys()
                
        for val in self._data:
            if self._data[val].expr is not None:
                self._data[val].expr = self._data[val].expr.simplify(self.model)

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self._data.keys())),
        if isinstance(self._index,_BaseSet):
           print >>ostream, "\tIndex=",self._index.name
        else:
           print >>ostream,""
        for key in self._data:
          if not self._data[key].expr is None:
                print >>ostream, "\t",
                self._data[key].expr.pprint(ostream)
                print >>ostream, ""
        if self._quad_subexpr is not None:
           print >>ostream, "\tQuadratic sub-expression: ",
           self._quad_subexpr.pprint(ostream)          
           print >>ostream, ""

    def display(self, prefix="", ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, prefix+"Objective "+self.name,":",
        print >>ostream, "  Size="+str(len(self))
        if None in self._data:
           print >>ostream, prefix+"  Value="+pyutilib.misc.format_io(self._data[None].expr(exception=False))
        else:
           for key in self._data:
             if not self._data[key].active:
                continue
             val = self._data[key].expr(exception=False)
             print >>ostream, prefix+"  "+str(key)+" : "+str(val)


class ConstraintData(NumericValue):

    def __init__(self, name=None):
        NumericValue.__init__(self,name=name,domain=Reals)
        self._equality = False
        self.lower = None
        self.lower_ineq_strict = None
        self.body = None
        self.upper = None
        self.upper_ineq_strict = None
        self.label = None
        self.id = None
        self.active = True

    def __call__(self, exception=True):
        if self.body is None:
            return None
        return self.body()

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False


class Constraint(NumericValue, IndexedComponent):
    """An object that defines a objective expression"""

    def __init__(self, *args, **kwd):
        """Construct an objective expression with rule to construct the
           expression
        """
	tkwd = {'ctype':Constraint}
        IndexedComponent.__init__(self, *args, **tkwd)
        tmpname="unknown"
        tmprule=None
        self._data = {}
        #if args == ():
        #   self._data[None]=ConstraintData()
        for key in kwd.keys():
          if key == "name":
             tmpname=kwd[key]
          elif key == "doc":
             self.doc=kwd[key]
          elif key == "rule":
             tmprule = kwd[key]
          else:
             raise ValueError, "Constraint constructor: unknown keyword - "+key
        NumericValue.__init__(self,name=tmpname)
        if None in self._data:
            self._data[None].name=tmpname
        self.rule = tmprule

    def __call__(self, exception=True):
        if len(self._data) == 0:
            return None
        if None in self._data:
            if self._data[None].body is None:
                return None
            return self._data[None].body()
        if exception:
            raise ValueError, "Cannot compute the value of an array of constraints"

    def dim(self):
        return self._ndim

    def __len__(self):
        return len(self._data.keys())

    def keys(self):
        return self._data.keys()
        #return self._index

    def __contains__(self,ndx):
        return ndx in self._data
        #return ndx in self._index

    def __getitem__(self,ndx):
        """This method returns a ConstraintData object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        if ndx in self._data:
           return self._data[ndx]
        raise KeyError, "Unknown index " + str(ndx) + " in constraint " + self.name

    def __iter__(self):
        return self._data.keys().__iter__()

    def construct(self, data=None):

        if pyomo.debug("verbose") or pyomo.debug("normal"):     #pragma:nocover
           print "Construcing constraint "+self.name
        if self.rule is None:
           self._data={}
           return
        #
        # Local variables for code optimization
        #
        _self_rule = self.rule
        #
        if not None in self._index and len(self._index) > 0 and _self_rule.func_code.co_argcount == 1:
            if pyomo.debug("verbose"):                            #pragma:nocover
                print "   Constructing constraint indices with rule that returns a dictionary"
            constraints = _self_rule(self.model)
            for val in constraints:
                if val not in self._index:
                    raise IndexError, "The index "+str(val)+" generated by the constructor rule is not valid"
                ##constructed_indices.append(val)
                self.add(val, constraints[val])
        else:
            for val in self._index:
                if pyomo.debug("verbose"):                            #pragma:nocover
                    print "   Constructing constraint index "+str(val)
                if val is None:
                    expr = _self_rule(self.model)
                    if expr is None or (type(expr) in [int,long,float] and expr == 0):
                        continue
                else:
                    if type(val) is tuple:
                        tmp=list(val)
                    else:
                        tmp=[val]
                    tmp.append(self.model)
                    tmp=tuple(tmp)
                    expr = _self_rule(*tmp)
                    if expr is None or (type(expr) in [int,long,float] and expr == 0):
                        continue
                ##constructed_indices.append(val)
                self.add(val, expr)
        #self._index=constructed_indices

    def add(self, index, expr):
        # index: the constraint index (should probably be renamed)
        # expr: the constraint expression
        # model: the parent model

        #
        # Ignore an 'empty' constraint
        #
        if expr is None:
            return
        #
        # Verify that the user actually provided an expression or tuple/list - they can (and have)
        # specified odd expressions that evaluate to unexpected values, e.g., True or False.
        #
        if isinstance(expr,Expression) is False and isinstance(expr,tuple) is False and isinstance(expr, list) is False:
           raise ValueError, "Non-expression object of "+str(type(expr))+" supplied to initialize constraint="+self.name+", index="+str(index)
           
        #
        #
        # Local variables to optimize runtime performance
        #
        _self_data = self._data
        _self_data[index] = ConstraintData(name=create_name(self.name,index))
        if not type(expr) in [tuple,list]:
            _expr_args0 = expr._args[0]
            _expr_args1 = expr._args[1]

            #_expr_args0.pprint()
            #print "HERE", is_constant(_expr_args0)
            #_expr_args1.pprint()
            #print "HERE", is_constant(_expr_args1)
        #
        # If the constructor rule returns an equality expression, then
        # convert to a 3-tuple
        #
        if isinstance(expr,_EqualToExpression):
            _self_data[index]._equality = True
            if is_constant(_expr_args1):
                tpl = [ _expr_args1,_expr_args0,_expr_args1, False, False ]
            elif is_constant(_expr_args1):
                tpl = [ _expr_args0,_expr_args1,_expr_args0, False, False ]
            else:
                tpl = [ 0.0 , _expr_args0 - _expr_args1, 0.0, False, False ]
        #
        # If the constructor rule returns a greater-than expression, then
        # convert to a 3-tuple
        #
        elif isinstance(expr,_GreaterThanExpression) or\
                isinstance(expr,_GreaterThanOrEqualExpression):

            if isinstance(_expr_args0,_GreaterThanExpression) or\
                    isinstance(_expr_args0,_GreaterThanOrEqualExpression):
                tpl = [ _expr_args1, _expr_args0._args[1], _expr_args0._args[0], 
                        isinstance(expr,_GreaterThanExpression), isinstance(_expr_args0,_GreaterThanExpression) ]

            elif isinstance(_expr_args0,_LessThanExpression) or\
                    isinstance(_expr_args0,_LessThanOrEqualExpression):
                tpl = [ _expr_args1, _expr_args0._args[0], _expr_args0._args[1], 
                        isinstance(expr,_GreaterThanExpression), isinstance(_expr_args0,_LessThanExpression) ]

            elif isinstance(_expr_args1,_GreaterThanExpression) or\
                    isinstance(_expr_args1,_GreaterThanOrEqualExpression):
                tpl = [ _expr_args1._args[1], _expr_args1._args[0], _expr_args0, 
                        isinstance(_expr_args1,_GreaterThanExpression), isinstance(expr,_GreaterThanExpression) ]

            elif isinstance(_expr_args1,_LessThanExpression) or\
                    isinstance(_expr_args1,_LessThanOrEqualExpression):
                tpl = [ _expr_args1._args[0], _expr_args1._args[1], _expr_args0,  
                        isinstance(_expr_args1,_LessThanExpression), isinstance(expr,_GreaterThanExpression) ]

            elif isinstance(_expr_args0,_EqualToExpression) or\
                    isinstance(_expr_args1,_EqualToExpression):
                raise ValueError, "Bound error: > expression used with an = expression."

            elif _expr_args0.is_constant():
                tpl = [ None, _expr_args1, _expr_args0, 
                        True, isinstance(expr,_GreaterThanExpression) ]
            elif _expr_args1.is_constant():
                tpl = [ _expr_args1, _expr_args0, None, 
                        isinstance(expr,_GreaterThanExpression), True]
            else:
                tpl = [ 0.0, _expr_args0-_expr_args1, None, 
                        isinstance(expr,_GreaterThanExpression), True ]

        #
        # If the constructor rule returns a less-than expression, then
        # convert to a 3-tuple
        #
        elif isinstance(expr,_LessThanExpression) or\
                isinstance(expr,_LessThanOrEqualExpression):

            if isinstance(_expr_args0,_LessThanExpression) or\
                    isinstance(_expr_args0,_LessThanOrEqualExpression):
                tpl = [ _expr_args0._args[0],_expr_args0._args[1],_expr_args1,
                        isinstance(_expr_args0,_LessThanExpression), isinstance(expr,_LessThanExpression) ]

            elif isinstance(_expr_args0,_GreaterThanExpression) or\
                    isinstance(_expr_args0,_GreaterThanOrEqualExpression):
                tpl = [ _expr_args0._args[1],_expr_args0._args[0],_expr_args1,
                        isinstance(_expr_args0,_GreaterThanExpression), isinstance(expr,_LessThanExpression) ]

            elif isinstance(_expr_args1,_LessThanExpression) or\
                    isinstance(_expr_args1,_LessThanOrEqualExpression):
                tpl = [ _expr_args0,_expr_args1._args[0],_expr_args1._args[1],
                        isinstance(expr,_LessThanExpression), isinstance(_expr_args1,_LessThanExpression) ]

            elif isinstance(_expr_args1,_GreaterThanExpression) or\
                    isinstance(_expr_args1,_GreaterThanOrEqualExpression):
                tpl = [ _expr_args0,_expr_args1._args[1],_expr_args1._args[0],
                        isinstance(expr,_LessThanExpression), isinstance(_expr_args1,_GreaterThanExpression) ]

            elif isinstance(_expr_args0,_EqualToExpression) or\
                    isinstance(_expr_args1,_EqualToExpression):
                raise ValueError, "Bound error: < expression used with an = expression."+str(expr)+str(expr._args)

            elif _expr_args0.is_constant():
                tpl = [ _expr_args0, _expr_args1, None,
                        isinstance(expr,_LessThanExpression), True ]
            elif _expr_args1.is_constant():
                tpl = [ None, _expr_args0, _expr_args1,
                        True, isinstance(expr,_LessThanExpression) ]
            else:
                tpl = [ 0.0, _expr_args1 - _expr_args0, None, 
                        isinstance(expr,_LessThanExpression), True ]
        #
        # If the constructor rule returns a tuple or list, then convert
        # it into a canonical form
        #
        elif type(expr) in [tuple,list]:
            #
            # Convert tuples to list
            #
            if type(expr) is tuple:
                expr = list(expr)
            #
            # Form equality expression
            #
            if len(expr) == 2:
                _self_data[index]._equality = True
                if is_constant(expr[1]):
                    tpl = [ expr[1], expr[0], expr[1], False, False ]
                else:
                    tpl = [ expr[0], expr[1], expr[0], False, False ]
            #
            # Form inequality expression
            #
            elif len(expr) == 3:
                tpl=list(expr)+[expr[0] is None, expr[2] is None]
            else:
                raise ValueError, "Constructor rule for constraint "+self.name+" returned a tuple of length "+str(len(expr))
        #
        # Unrecognized constraint values
        #
        else:
            raise ValueError, "Constraint \"" + self.name + "\" does not have a proper value:" + str(expr)
        #
        # Replace numeric bound values with a NumericConstant object,
        # and reset the values to 'None' if they are 'infinite'
        #
        if type(tpl[0]) in [bool,int,long,float]:
            if pyutilib.math.is_finite(tpl[0]):
                tpl[0] = NumericConstant(value=float(tpl[0]))
            else:
                tpl[0] = None
        elif type(tpl[0]) is NumericConstant and not pyutilib.math.is_finite(tpl[0]()):
                tpl[0] = None
        if type(tpl[1]) in [bool,int,long,float]:
            raise ValueError, "Constraint \""+self.name+"\" has a numeric body.  Expecting Expression instance."
        if _self_data[index]._equality:
            tpl[2] = tpl[0]
        elif type(tpl[2]) in [bool,int,long,float]:
            if pyutilib.math.is_finite(tpl[2]):
                tpl[2] = NumericConstant(value=float(tpl[2]))
            else:
                tpl[2] = None
        elif type(tpl[2]) is NumericConstant and not pyutilib.math.is_finite(tpl[2]()):
                tpl[2] = None
        #
        # Error check, to ensure that we don't have an equality constraint with
        # 'infinite' RHS
        #
        if (tpl[0] is None or tpl[2] is None) and _self_data[index]._equality:
            raise ValueError, "Equality constraint "+self.name+" defined with infinity RHS"
        #
        # Setup identity expressions
        #
        if tpl[0] is not None:
            if not isinstance(tpl[0],Expression):
                tpl[0] = _IdentityExpression(tpl[0])
            tpl[0] = tpl[0].simplify(self.model)
        if tpl[1] is not None:
            if not isinstance(tpl[1],Expression):
                tpl[1] = _IdentityExpression(tpl[1])
            tpl[1] = tpl[1].simplify(self.model)
        if tpl[2] is not None:
            if not isinstance(tpl[2],Expression):
                tpl[2] = _IdentityExpression(tpl[2])
            tpl[2] = tpl[2].simplify(self.model)
        #
        # Finally, setup the data
        #
        _self_data[index].lower = tpl[0]
        _self_data[index].lower_ineq_strict = tpl[3]
        _self_data[index].body = tpl[1]
        _self_data[index].upper = tpl[2]
        _self_data[index].upper_ineq_strict = tpl[4]


    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self._data.keys())),
        if isinstance(self._index,_BaseSet):
           print >>ostream, "\tIndex=",self._index.name
        else:
           print >>ostream,""
        for val in self._data:
          if not val is None:
             print >>ostream, "\t"+`val`
          if self._data[val].lower is not None:
             print >>ostream, "\t\t",
             self._data[val].lower.pprint(ostream)
          else:
             print >>ostream, "\t\t-Inf"
          if self._data[val].lower_ineq_strict:
             print >>ostream, "\t\t<"
          else:
             print >>ostream, "\t\t<="
          if self._data[val].body is not None:
             print >>ostream, "\t\t",
             self._data[val].body.pprint(ostream)
          #else:                         #pragma:nocover
             #raise ValueError, "Unexpected empty constraint body"
          if self._data[val].upper_ineq_strict:
             print >>ostream, "\t\t<"
          else:
             print >>ostream, "\t\t<="
          if self._data[val].upper is not None:
             print >>ostream, "\t\t",
             self._data[val].upper.pprint(ostream)
          elif self._data[val]._equality:
             print >>ostream, "\t\t",
             self._data[val].lower.pprint(ostream)
          else:
             print >>ostream, "\t\tInf"

    def display(self, prefix="", ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, prefix+"Constraint "+self.name,":",
        print >>ostream, "  Size="+str(len(self))
        if None in self._data:
           print >>ostream, prefix+"  Value="+pyutilib.misc.format_io(self._data[None].body())
        else:
           flag=True
           for key in self._data:
             if not self._data[key].active:
                continue
             if flag:
                print >>ostream, prefix+"        \tLower\tBody\t\tUpper"
                flag=False
             if self._data[key].lower is not None:
                lval = str(self._data[key].lower())
             else:
                lval = "-Infinity"
             val = str(self._data[key].body())
             if self._data[key].upper is not None:
                uval = str(self._data[key].upper())
             else:
                uval = "Infinity"
             print >>ostream, prefix+"  "+str(key)+" :\t"+lval+"\t"+val+"\t"+uval
           if flag:
                print >>ostream, prefix+"  None active"


ComponentRegistration("Objective", Objective, "Expressions that are minimized or maximized in a model.")
ComponentRegistration("Constraint", Constraint, "Constraint expressions a model.")
