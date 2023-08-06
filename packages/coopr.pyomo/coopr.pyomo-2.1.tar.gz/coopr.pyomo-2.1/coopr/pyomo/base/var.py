#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Var', 'VarStatus', '_VarBase']

from numvalue import *
from numvalue import create_name
from plugin import ComponentRegistration
import types
from set_types import *
from indexed_component import IndexedComponent
import pyutilib.math
import pyutilib.misc
from pyutilib.enum import Enum
import sys
from param import _ParamValue

VarStatus = Enum('undefined', 'fixed_by_presolve', 'fixed_by_optimizer', 'unused', 'used')

class _VarValue(NumericValue):
    """Holds the numeric value of a variable, along with suffix info"""

    """Constructor"""
    def __init__(self,**kwds):
        NumericValue.__init__(self,**kwds)
        self.var = None # the "parent" variable.
        self.index = None # the index of this variable within the "parent"
        self.id = None
        self.label = None
        self.initial = None
        self.active = True
        # IMPORTANT: in contrast to the initial value, the lower and upper bounds
        #            of a variable can in principle be either numeric constants,
        #            parameter values, or expressions - anything is OK, as long as
        #            invoking () is legal.
        self.lb = None 
        self.ub = None 
        self.fixed = False 
        self.status = VarStatus.undefined 

    def __str__(self):
        return self.name

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def setlb(self, value):
        # python only has 3 numeric built-in type that we deal with (we ignore complex numbers).       
        if isinstance(value, int) or isinstance(value, long) or isinstance(value, float):
           self.lb = NumericConstant(value=value)
        elif value is None:
           self.lb = None
        elif isinstance(value, _ParamValue):
           self.lb = value
        else:
           raise ValueError, "Unknown type="+str(type(value))+" supplied as variable lower bound - legal types are numeric constants or parameters"

    def setub(self, value):
        # python only has 3 numeric built-in type that we deal with (we ignore complex numbers).       
        if isinstance(value, int) or isinstance(value, long) or isinstance(value, float):
           self.ub = NumericConstant(value=value)
        elif value is None:
           self.ub = None
        elif isinstance(value, _ParamValue):
           self.ub = value
        else:
           raise ValueError, "Unknown type="+str(type(value))+" supplied as variable upper bound - legal types are numeric constants or parameters"       

    def fixed_value(self):
        if self.fixed:
            return True
        return False

    def is_constant(self):
        if self.fixed:
            return True
        return False

    def is_binary(self):
        return self.var.is_binary()

    def is_integer(self):
        return self.var.is_integer()

    def is_continuous(self):
        return self.var.is_continuous()

    def simplify(self, model):
        return self                 #pragma:nocover

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, str(self),

#
# Variable attributes:
#
# Single variable:
#
# x = Var()
# x.fixed = True
# x.domain = Reals
# x.name = "x"
# x.setlb(-1.0)
# x.setub(1.0)
# x.initial = 0.0
# x = -0.4
#
# Array of variables:
#
# y = Var(set1,set2,...,setn)
# y.fixed = True (fixes all variables)
# y.domain = Reals
# y.name = "y"
# y[i,j,...,k] (returns value of a given index)
#
# y[i,j,...,k].fixed
# y[i,j,...,k].lb()
# y[i,j,...,k].ub()
# y[i,j,...,k].initial
#

class _VarBase(IndexedComponent):
    """A numeric variable, which may be defined over a index"""

    """ Constructor
        Arguments:
           name                The name of this variable
           index        The index set that defines the distinct variables.
                          By default, this is None, indicating that there
                          is a single variable.
           domain       A set that defines the type of values that
                          each parameter must be.
           default      A set that defines default values for this
                          variable.
           bounds       A rule for defining bounds values for this
                          variable.
           rule         A rule for setting up this parameter with
                          existing model data
    """
    def __init__(self, *args, **kwd):
	tkwd = {'ctype':Var}
        IndexedComponent.__init__(self, *args, **tkwd)
        #
        # Default keyword values
        #
        self._attr_declarations = {}
        tmpname="unknown"
        tmpdomain=Reals
        tmpbounds=None
        self._varval={}
        self._initialize=None
        for key in kwd.keys():
          if key == "name":
             tmpname=kwd[key]
          elif key == "within" or key=="domain":
             tmpdomain=kwd[key]
          elif key == "doc":
             self.doc=kwd[key]
          elif key == "initialize":
             self.__dict__["_"+key] = kwd[key]
          elif key == "bounds":
             tmpbounds=kwd[key]
          else:
             raise ValueError, "Var constructor: unknown keyword - "+key
        self.name = tmpname
        self.domain = tmpdomain
        self.bounds=tmpbounds

    def as_numeric(self):
        if None in self._varval:
            return self._varval[None]
        return self

    def keys(self):
        return self._varval.keys()

    def __iter__(self):
        return self._varval.keys().__iter__()

    def __contains__(self,ndx):
        return ndx in self._varval

    def dim(self):
        return self._ndim

    def reset(self):
        for key in self._varval:
            if not self._varval[key].initial is None:
                self._varval[key].set_value( self._varval[key].initial )

    def __len__(self):
        return len(self._varval)

    def __setitem__(self,ndx,val):
        #print "HERE",ndx,val, self._valid_value(val,False), self.domain
        if None in self._index:
            raise KeyError, "Cannot set an array value in singleton variable "+self.name
        if ndx not in self._index:
            raise KeyError, "Cannot set the value of array variable "+self.name+" with invalid index "+str(ndx)
        if not self._valid_value(val,False):
            raise ValueError, "Cannot set variable "+self.name+" with invalid value: index=" + str(ndx) + " value=" + str(val)
        self._varval[ndx].value = val

    def __getitem__(self,ndx):
        """This method returns a _VarValue object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        try:
            return self._varval[ndx]
        except KeyError:
            raise KeyError, "Unknown index " + str(ndx) + " in variable " + self.name

    def is_binary(self):
        return isinstance(self.domain, BooleanSet)

    def is_integer(self):
        return isinstance(self.domain, IntegerSet)

    def is_continuous(self):
        return not (self.is_binary() or self.is_integer())

    def simplify(self, model):
        return self

    def construct(self, data=None):
        #
        # Construct _VarValue() objects for all index values
        #
        if self._ndim > 0:
            if type(self._initialize) is dict:
                self._index = self._initialize.keys()
            for ndx in self._index:
                if ndx is not None:
                    self._varval[ndx] = _VarValue(name=create_name(self.name,ndx),domain=self.domain)
                    self._varval[ndx].var = self
                    self._varval[ndx].index = ndx
        #
        # Initialize values with a dictionary if provided
        #
        if self._initialize is not None and type(self._initialize) is not types.FunctionType:
           if type(self._initialize) is dict:
              for key in self._initialize:
                self._varval[key].value = None
                self._varval[key].initial = self._initialize[key]
                self._valid_value(self._initialize[key],True)
           else:
              for key in self._index:
                self._varval[key].value = None
                self._varval[key].initial = self._initialize
              self._valid_value(self._initialize,True)
        #
        # Initialize values with the _rule function if provided
        #
        elif type(self._initialize) is types.FunctionType:
           for key in self._varval:
             if isinstance(key,tuple):
                tmp = list(key)
             elif key is None:
                tmp = []
             else:
                tmp = [key]
             tmp.append(self.model)
             tmp = tuple(tmp)
             self._varval[key].value = None
             self._varval[key].initial = self._initialize(*tmp)
             self._valid_value(self._varval[key].initial,True)
        #
        # Initialize bounds with the bounds function if provided
        #
        if self.bounds is not None:
           # bounds are specified via a tuple
           if type(self.bounds) is tuple:
             for key in self._varval:
               (lb, ub) = self.bounds
               self._varval[key].setlb(lb)
               self._varval[key].setub(ub)               
           else:
             # bounds are specified via a function
             for key in self._varval:
               if isinstance(key,tuple):
                  tmp = list(key)
               elif key is None:
                  tmp = []
               else:
                  tmp = [key]
               tmp.append(self.model)
               tmp = tuple(tmp)
               (lb, ub) = self.bounds(*tmp)
               self._varval[key].setlb(lb)
               self._varval[key].setub(ub)                              
           for key in self._varval:
             if self._varval[key].lb is not None and \
                not pyutilib.math.is_finite(self._varval[key].lb()):
                self._varval[key].setlb(None)
             if self._varval[key].ub is not None and \
                not pyutilib.math.is_finite(self._varval[key].ub()):
                self._varval[key].setub(None)
        #
        # Iterate through all variables, and tighten the bounds based on
        # the domain bounds information.
        #
        dbounds = self.domain.bounds()
        if not dbounds is None and dbounds != (None,None):
            for key in self._varval:
                if not dbounds[0] is None:
                    if self._varval[key].lb is None or dbounds[0] > self._varval[key].lb():
                        self._varval[key].setlb(dbounds[0])
                if not dbounds[1] is None:
                    if self._varval[key].ub is None or dbounds[1] < self._varval[key].ub():
                        self._varval[key].setub(dbounds[1])
        #
        # Setup declared attributes for all variables
        #
        for attr in self._attr_declarations:
            for key in self._varval:
                setattr(self._varval[key],attr,self._attr_declarations[attr][0])

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self)),
        print >>ostream, "\tDomain="+self.domain.name
        if self._index_set is not None:
            print >>ostream, "\tIndicies: ",
            for idx in self._index_set:
               print >>ostream, str(idx.name)+", ",
            print ""
        if None in self._varval:
           print >>ostream, "\tInitial Value : Lower Bound : Upper Bound : Current Value: Fixed"
           lb_value = None
           if self._varval[None].lb is not None:
              lb_value = self._varval[None].lb()
           ub_value = None
           if self._varval[None].ub is not None:
              ub_value = self._varval[None].ub()              
           print >>ostream, "\t", str(self._varval[None].initial)+" : "+str(lb_value)+" : "+str(ub_value)+" : "+str(self._varval[None].value)+" : "+str(self._varval[None].fixed)
        else:
           print >>ostream, "\tKey : Initial Value : Lower Bound : Upper Bound : Current Value: Fixed"
           tmp=self._varval.keys()
           tmp.sort()
           for key in tmp:
             initial_val = self._varval[key].initial
             lb_value = None             
             if self._varval[key].lb is not None:
                lb_value = self._varval[key].lb()
             ub_value = None
             if self._varval[key].ub is not None:
                ub_value = self._varval[key].ub()              
             
             print >>ostream, "\t"+str(key)+" : "+str(initial_val)+" : "+str(lb_value)+" : "+str(ub_value)+" : "+str(value(self._varval[key].value))+" : "+str(value(self._varval[key].fixed))

    def display(self, prefix="", ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, prefix+"Variable "+self.name,":",
        print >>ostream, "  Size="+str(len(self)),
        print >>ostream, "Domain="+self.domain.name
        if None in self._varval:
           print >>ostream, prefix+"  Value="+pyutilib.misc.format_io(self._varval[None].value)
        else:
           for key in self._varval:
             val = self._varval[key].value
             print >>ostream, prefix+"  "+str(key)+" : "+str(val)

    def declare_attribute(self, name, default=None):
        """
        Declare a user-defined attribute.
        """
        if name[0] == "_":
            raise AttributeError, "Cannot define an attribute that begins with  '_'"
        if name in self._attr_declarations:
            raise AttributeError, "Attribute %s is already defined" % name
        self._attr_declarations[name] = (default,)
        #if not default is None:
            #self._valid_value(default)
        #
        # If this variable has been constructed, then
        # generate this attribute for all variables
        #
        if len(self._varval) > 0:
            for key in self._varval:
                setattr(self._varval[key],name,default)


class _VarElement(_VarBase,_VarValue):

    def __init__(self, *args, **kwd):
        _VarValue.__init__(self, **kwd)
        _VarBase.__init__(self, *args, **kwd)
        self._varval[None] = self
        self._varval[None].var = self
        self._varval[None].index = None

    def is_constant(self):
        return _VarValue.is_constant(self)


class _VarArray(_VarBase):

    def __init__(self, *args, **kwd):
        _VarBase.__init__(self, *args, **kwd)
        self._dummy_val = _VarValue(**kwd)

    def __float__(self):
        raise TypeError, "Cannot access the value of array variable "+self.name

    def __int__(self):
        raise TypeError, "Cannot access the value of array variable "+self.name

    def _valid_value(self,value,use_exception=True):
        #print "VALID",self._dummy_val.domain
        return self._dummy_val._valid_value(value,use_exception)

    def set_value(self, value):
        raise ValueError, "Cannot specify the value of array variable "+self.name

    def __str__(self):
        return self.name

class Var(object):
    """
    Variable objects that are used to construct Pyomo models.
    """
    def __new__(cls, *args, **kwds):
        if args == ():
            self = _VarElement(*args, **kwds)
        else:
            self = _VarArray(*args, **kwds)
        return self


ComponentRegistration("Var", Var, "Decision variables in a model.")
