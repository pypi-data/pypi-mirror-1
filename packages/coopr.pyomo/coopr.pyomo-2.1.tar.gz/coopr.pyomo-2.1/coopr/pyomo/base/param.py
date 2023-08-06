#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['_ParamBase', 'Param']

from numvalue import create_name
from coopr.pyomo.base.numvalue import *
from coopr.pyomo.base.plugin import ComponentRegistration
from sets import _BaseSet
from set_types import *
import pyomo
import sys
import types
from indexed_component import IndexedComponent


class _ParamValue(NumericConstant):
    """Holds the numeric value of a parameter"""

    """Constructor"""
    def __init__(self, **kwds):
        try:
            NumericConstant.__init__(self, **kwds)
        except ValueError, e:
            raise ValueError, "Problem constructing parameter "+self.name+" : "+str(e)

    def fixed_value(self):
        return True

    def __str__(self):
        return self.name


class _ParamBase(IndexedComponent):
    """A parameter value, which may be defined over a index"""

    """ Constructor
        Arguments:
           name                The name of this parameter
           index        The index set that defines the distinct parameters.
                          By default, this is None, indicating that there
                          is a single parameter.
           within        A set that defines the type of values that
                          each parameter must be.
           validate     A rule for validating this parameter w.r.t. data
                          that exists in the model
           default        A set that defines default values for this
                          parameter
           rule                A rule for setting up this parameter with
                          existing model data
    """
    def __init__(self, *args, **kwd):
        tkwd = {'ctype':Param}
        IndexedComponent.__init__(self, *args, **tkwd)
        tmpname="unknown"
        tmpdomain=Any
        self._paramval={}
        self._initialize={}
        self._validate=None
        defaultval=None
        for key in kwd.keys():
          if key == "rule":
             self.__dict__["_initialize"] = kwd[key]
          elif key is "name":
                tmpname = kwd[key]
          elif key == "doc":
             self.doc=kwd[key]
          elif key == "within":
                tmpdomain = kwd[key]
          elif key in ("validate","initialize"):
             self.__dict__["_"+key] = kwd[key]
          elif key == "default":
             defaultval = kwd[key]
          else:
             raise ValueError, "Param constructor: unknown keyword - "+key
        self.name = tmpname
        self.domain = tmpdomain
        self._default = _ParamValue(name=tmpname,domain=tmpdomain,value=value(defaultval))

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self)),
        print >>ostream, "\tDomain="+self.domain.name
        if None in self._paramval:
           print >>ostream, "\t", self._paramval[None].value
        else:
           tmp=self._paramval.keys()
           tmp.sort()
           for key in tmp:
             val = self._paramval[key].value
             print >>ostream, "\t"+str(key)+" : "+str(val)
        if self._default.value is not None and not self._default.value is None:
           print >>ostream, "\tdefault: "+str(self._default.value)

    def keys(self):
        if self._default.value is None:
            return self._paramval.keys()
        else:
            if not isinstance(self._index,_BaseSet):
                raise ValueError, "Expected a set object for _index"
            return self._index

    def __contains__(self, element):
        if self._default.value is None:
            return element in self._paramval
        else:
            return element in self._index

    def __iter__(self):
        if self._default.value is None:
            return self._paramval.keys().__iter__()
        else:
            return self._index.keys().__iter__()

    def dim(self):
        return self._ndim

    def __len__(self):
        if not self._default.value is None:
           return len(self._index)
        return len(self._paramval)

    def __getitem__(self,ndx):
        """This method returns a _ParamVal object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        if ndx in self._paramval:
           return self._paramval[ndx]
        if ndx in self._index and self._default.value is not None and not self._default.value is None:
           return self._default.value
        if ndx in self._index:
           errmsg = "Valid index " + str(ndx) + " for parameter " + self.name+" but no default value specified"
           if pyomo.debug("verbose"):       #pragma:nocover
              errmsg = errmsg+" : Defined indices="+str(self._paramval.keys())
        else:
           errmsg = "Unknown index " + str(ndx) + " in parameter " + self.name
           if pyomo.debug("verbose"):       #pragma:nocover
              errmsg = errmsg+" : Valid indices="+str(list(self._index.value))
        raise KeyError, "Unknown index " + str(ndx) + " in parameter " + self.name

    def __setitem__(self,ndx,val):

        if self._index_set is not None:
           # this is a "hack", in that we still need to check for legal sub-components in the input index.
           if ndx in self._paramval:
                self._paramval[ndx].value = val
           else:
                self._paramval[ndx]= _ParamValue(name=create_name(self.name,ndx),domain=self.domain,value=val)
           return

        if None in self._index:
           raise KeyError, "Cannot set an array value in the simple parameter "+self.name
        if ndx not in self._index:
           raise KeyError, "Cannot set the value of array parameter "+self.name+" with invalid index "+str(ndx)
        if ndx in self._paramval:
           self._paramval[ndx].value = val
        else:
           self._paramval[ndx]= _ParamValue(name=create_name(self.name,ndx),domain=self.domain,value=val)            
        if not self._valid_indexed_value(val,ndx,False):
            raise ValueError, "Cannot set parameter "+self.name+" with invalid value: index=" + str(ndx) + " value=" + str(val)

    def construct(self, data=None):
        """ Apply the rule to construct values in this set """
        if pyomo.debug("verbose"):      #pragma:nocover
           print "Constructing Param, name="+self.name+", from data="+`data`
        #
        # Code optimization with local variables
        #
        _name=self.name
        _domain=self.domain
        #
        # Update the default value, if it's available
        #
        try:
            self._default.value = self.default
        except:
            pass
        #
        # Construct using the initial data or the data loaded from an
        # external source.  Note:  data values will be queried in to following
        # order: 
        #   1) the 'data' dictionary
        #   2) the self._initialize dictionary
        #   3) the default value
        #
        if data is not None or type(self._initialize) is not types.FunctionType:
           #
           # Singleton parameter
           #
           if type(self._index) is dict:
              if data is not None and None in data.keys():
                    self.value=data[None]
              elif type(self._initialize) is not dict:
                    self.value=self._initialize
              elif None in self._initialize:
                    self.value=self._initialize[None]
              elif self._default.value is not None and not self._default.value is None:
                    self.value=self._default.value
                    #self._paramval[None] = self._default
              else:
                    raise ValueError, "Attempting to construct parameter "+_name+" without parameter data"
              #print "Z",type(self._paramval[None].value), self._paramval[None].value
              #print "Z",type(self.__call__())
              self._valid_indexed_value(self.value,(),True)
           else:
              #
              # Set external data values (if provided)
              #
              if data is not None:
                 for key in data:
                   if type(key) is tuple and len(key)==1:
                      tmpkey=key[0]
                   else:
                      tmpkey=key
                   self._paramval[tmpkey] = _ParamValue(name=create_name(_name,key),domain=_domain,value=data[key])
                   self._valid_indexed_value(data[key],key,True)
              #
              # Initialize with initialization data.
              #
              elif self._initialize is not None:
                 if type(self._initialize) is dict:
                    for key in self._initialize:
                      self._paramval[key] = _ParamValue(name=create_name(_name,key),domain=_domain,value=self._initialize[key])
                      self._valid_indexed_value(self._initialize[key],key,True)
                 else:
                    for key in self._index:
                      self._paramval[key] = _ParamValue(name=create_name(_name,key),domain=_domain,value=self._initialize)
                    self._valid_indexed_value(self._initialize,(),True)
        #
        # Construct using the rule
        #
        elif type(self._initialize) is types.FunctionType:
           if (type(self._index) is dict) and (None in self._index):
              # singleton 
              tmp = []
              tmp.append(self.model)
              tval = self._initialize(*tmp)
              self.value = tval
           else:
              # non-singleton 
              for val in self._index:
                 if isinstance(val,tuple):
                    tmp = list(val)
                 elif val is None:
                    tmp = []
                 else:
                    tmp = [val]
                 if len(tmp) > 0:
                       tname=create_name(_name,val)
                 else:
                       tname=_name
                 tmp.append(self.model)
                 tmp = tuple(tmp)
                 tval = self._initialize(*tmp)
                 self._paramval[val] = _ParamValue(name=tname,domain=_domain,value=tval)
                 self._valid_indexed_value(tval,val,True)

    def _valid_indexed_value(self,value,index, use_exception):
        if self._validate is not None:
           tmp = [value]
           if index == ():
              index = (None,)*self._ndim
           if index is not None:
              tmp = tmp + list(index)
           tmp.append(self.model)
           tmp = tuple(tmp)
           if self._validate(*tmp):
              return True
        elif self.domain is None or value in self.domain:
           return True
        if use_exception:           #pragma:nocover
           raise ValueError, "Invalid value "+str(value)+" for parameter "+self.name
        return False
        

class _ParamElement(_ParamBase,_ParamValue):

    def __init__(self, *args, **kwd):
        _ParamValue.__init__(self, **kwd)
        _ParamBase.__init__(self, *args, **kwd)
        self._paramval[None] = self

    #def simplify(self, model):
        #return self
        #return NumericConstant(value=self.value)

    def check_values(self):         #pragma:nocover
        #
        # Validate the values
        #
        if None not in self._index:
            raise ValueError, "Undefined value for parameter "+self.name
        if not self._valid_indexed_value(self.value,None,False):
            print "BUG",self.value,self._index
            raise ValueError, "Parameter "+self.name+" failed validation test value=" + str(self.value)

    def __call__(self, exception=True):
        return self._paramval[None].value


class _ParamArray(_ParamBase):

    def __init__(self, *args, **kwd):
        _ParamBase.__init__(self, *args, **kwd)

    def simplify(self, model):
        raise ValueError, "Cannot simplify array parameter "+self.name

    def __float__(self):
        raise ValueError, "Cannot access the value of array parameter "+self.name

    def __int__(self):
        raise ValueError, "Cannot access the value of array parameter "+self.name

    def set_value(self, value):
        for key in self._paramval:
            self._paramval[key].value = value
            self._valid_indexed_value(value,key,True)
            #self._valid_value(value,key,True)

    def check_values(self):         #pragma:nocover
        #
        # Validate the values
        #
        for val in self._paramval:
            if val not in self._index:
                raise ValueError, "Undefined value for parameter "+self.name+" index=" + str(val)
            if not self._valid_indexed_value(self._paramval[val].value,val,False):
                raise ValueError, "Parameter "+self.name+" failed validation test: index=" + str(val) + " value=" + str(self._paramval[val].value)

    def reset(self):
        pass                        #pragma:nocover

    def display(self, ostream=None):
        self.pprint(ostream=ostream)

    def __str__(self):
        return str(self.name)


class Param(object):
    """
    Data objects that are used to construct Pyomo models.
    """
    def __new__(cls, *args, **kwds):
        if args == ():
            self = _ParamElement(*args, **kwds)
        else:
            self = _ParamArray(*args, **kwds)
        return self


ComponentRegistration("Param", Param, "Parameter data that is used to define a model instance.")
