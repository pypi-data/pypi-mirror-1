#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Set', '_BaseSet', '_SetContainer', '_SetArray', '_ProductSet']

import pyutilib.plugin.core
from coopr.pyomo.base.plugin import ComponentRegistration
from component import Component
import pyutilib.misc
import sys
import types
import copy

log = pyutilib.plugin.core.PluginGlobals.env().log

##------------------------------------------------------------------------
##
## An abstract Set class
##
##------------------------------------------------------------------------

class _BaseSet(Component):
    """The base class for set objects that are used to index other Pyomo objects

       This class has a similar look-and-feel as a built-in set class.  However,
       the set operations defined in this class return another abstract
       Set object.  This class contains a concrete set, which can be 
       initialized by the load() method.
    """

    """ Constructor
        Arguments:
           name          The name of the set
           within        A set that defines the type of values that can
                          be contained in this set
           rule
           initialize    Default set members, which may be overriden
                          when setting up this set
           validate      Define a function for validating membership in a
                          set.  This has the functional form:
                          f: data -> bool
                          and returns true if the data belongs in the set
           dimen         Specify the set's arity.
           doc           Documentation for this object
           virtual       Indicate that this is a virtual set that does not
                            have concrete members.
    """
    def __init__(self, **kwds):
        Component.__init__(self, ctype=Set)
        self.initialize=None
        self.name="_unknown_"
        self.validate=None
        self.ordered=False
        self.order=[]
        self.domain=None
        self.dimen = None
        self.virtual = False
        self._bounds=None
        self.doc = ""
        for key in kwds.keys():
          if key == "dimen":
             pass
          elif key == "doc":
             self.doc=kwds[key]
          elif key == "virtual":
             self.virtual=kwds[key]
          elif key == "bounds":
             self._bounds=kwds[key]
          elif key == "within":
             self.domain = kwds[key]
             if self.domain is not None:
                self.dimen = self.domain.dimen
          elif key == "rule":
             setattr(self,"initialize",kwds[key])
          elif key in ["name", "initialize", "validate", "ordered"]:
             setattr(self,key,kwds[key])
          else:
             raise ValueError, "Unknown option '"+key+"' when constructing Set "
        if "dimen" in kwds.keys():
           if self.within is not None and self.dimen != kwds["dimen"]:
              raise ValueError, "Option dimen "+str(kwds["dimen"])+" is different from the dimen of superset "+self.within.name+": "+str(self.dimen)
           self.dimen = kwds["dimen"]
        if self.dimen is None:
            # We set the default to 1
            self.dimen=1
        if self.initialize is not None:
           #
           # Convert generators to lists, since a generator is not copyable
           #
           if type(self.initialize) is types.GeneratorType:
              self.initialize = list(self.initialize)
           #
           # Try to guess dimen from the initialize list
           #
           tmp=None
           if type(self.initialize) is tuple:
              tmp = len(self.initialize)
           elif type(self.initialize) is list and len(self.initialize) > 0 \
                and type(self.initialize[0]) is tuple:
              tmp = len(self.initialize[0])
           if tmp is not None:
              if "dimen" in kwds and tmp != self.dimen:
                 raise ValueError, "Dimension argument differs from the data in the initialize list"
              else:
                 self.dimen=tmp

    def reset(self):
        pass

    def dim(self):
        return self._ndim

    def display(self, ostream=None):
        self.pprint(ostream=ostream)

    def __getattr__(self,name):
        if name is "within":
           return self.domain
        raise AttributeError, "Unknown attribute "+name

    def __setattr__(self,name,val):
        if name is "within":
           self.domain = val
        return object.__setattr__(self,name,val)

    def _verify(self,element,use_exception=True):
        # A utility routine that is used to verify if the element
        # is valid for this set.
        if self.domain is not None and element not in self.domain:
           if use_exception:
              raise ValueError, "Value "+str(element)+" is not valid for set "+self.name+", because it is not within set "+self.domain.name
           return False
        if self.validate is not None and not self.validate(element,self.model):
           if use_exception:
              raise ValueError, "Value "+str(element)+" violates the validation rule of set "+self.name
           return False
        if self.dimen > 1 and type(element) is not tuple:
           if use_exception:
              raise ValueError, "Value "+str(element)+" is not a tuple for set "+self.name+", which has dimen "+str(self.dimen)
           return False
        elif self.dimen == 1 and type(element) is tuple:
           if use_exception:
              raise ValueError, "Value "+str(element)+" is a tuple for set "+self.name+", which has dimen "+str(self.dimen)
           return False
        elif type(element) is tuple and len(element) != self.dimen:
           if use_exception:
              raise ValueError, "Value "+str(element)+" does not have dimension "+str(self.dimen)+", which is needed for set "+self.name
           return False
        return True

    def bounds(self):
        """Return bounds information.  The default value is 'None', which
        indicates that this set does not contain bounds."""
        return self._bounds


class _SetContainer(_BaseSet):
    """A derived _BaseSet object that contains a single set."""

    def __init__(self, *args, **kwds):
        """ Constructor """
        if args != ():
            raise TypeError, "A _SetContainer expects no arguments"
        self._index_set=None
        self._index=[None]
        self._ndim=0
        self.value=set()
        _BaseSet.__init__(self,**kwds)

    def construct(self, values=None):
        """ Apply the rule to construct values in this set """
        log.debug("Constructing _SetContainer, name="+self.name+", from data="+repr(values))
        #
        # Construct using the values list
        #
        if values is not None:
           if type(self._bounds) is tuple:
                first=self._bounds[0]
                last=self._bounds[1]
           else:
                first=None
                last=None
           all_numeric=True
           for val in values[None]:
                if type(val) in [int,float,long]:
                    if first is None or val<first:
                        first=val
                    if last is None or val>last:
                        last=val
                else:
                    all_numeric=False
                self.add(val)
           if all_numeric:
                self._bounds = (first,last)
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
           if self.model is None:
              raise ValueError, "Must pass a model in to initialize with a function"
           if self.initialize.func_code.co_argcount == 1:
              #
              # Using a rule of the form f(model) -> iterator
              #
              tmp = self.initialize(self.model)
              for val in tmp:
                if self.dimen is None:
                   if type(val) in [tuple,list]:
                        self.dimen=len(val)
                   else:
                        self.dimen=1
                self.add(val)
           else:
              #
              # Using a rule of the form f(z,model) -> element
              #
              ctr=0
              val = self.initialize(ctr,self.model)
              if self.dimen is None:
                   if type(val) in [tuple,list]:
                        self.dimen=len(val)
                   else:
                        self.dimen=1
              while val is not None:
                self.add(val)
                ctr += 1
                val = self.initialize(ctr,self.model)
           #
           # We should be verifying as part of the add() method
           #
           #for val in self.value:
             #self._verify(val)
        #
        # Construct using the default values
        #
        elif self.initialize is not None:
              if type(self.initialize) is dict:
                 raise ValueError, "Cannot initialize set "+self.name+" with dictionary data"
              if type(self._bounds) is tuple:
                first=self._bounds[0]
                last=self._bounds[1]
              else:
                first=None
                last=None
              all_numeric=True
              for val in self.initialize:
                if type(val) in [int,float,long]:
                    if first is None or val<first:
                        first=val
                    if last is None or val>last:
                        last=val
                else:
                    all_numeric=False
                self.add(val)
              #print "HERE",self.name,first,last,all_numeric
              if all_numeric:
                self._bounds = (first,last)

    def data(self):
        """The underlying set data."""
        if self.virtual:
           raise TypeError, "Cannot access underlying set data for virtual set "+self.name
        return self.value

    def clear(self):
        """Remove all elements from the set."""
        if self.virtual:
           raise TypeError, "Cannot clear virtual Set object `"+self.name+"'"
        self.value.clear()
        self.order=[]

    def check_values(self):
        """ Verify that the values in this set are valid.
        """
        if self.virtual:
           return
        for val in self.value:
          self._verify(val)

    def first(self):
        if self.virtual:
           raise TypeError, "Cannot access the first element of virtual set `"+self.name+"'"
        if len(self.order) > 0:
           return self.order[0]
        else:
           for val in self.value:
             return val

    def add(self, *args):
        """Add one or more elements to a set."""
        if self.virtual:
           raise TypeError, "Cannot add elements to virtual set `"+self.name+"'"
        for val in args:
          tmp = pyutilib.misc.flatten_tuple(val)
          self._verify(tmp)
          try:
            if tmp in self.value:
               raise ValueError, "Element "+str(tmp)+" already exists in set "+self.name
            self.value.add(tmp)
            if self.ordered:
               self.order.append(tmp)
          except TypeError:
            raise TypeError, "Problem inserting "+str(tmp)+" into set "+self.name

    def remove(self, element):
        """Remove an element from the set.
           If the element is not a member, raise an error.
        """
        if self.virtual:
           raise KeyError, "Cannot remove element `"+str(element)+"' from virtual set "+str(self.name)
        if element not in self.value:
           raise KeyError, "Cannot remove element `"+str(element)+"' from set "+str(self.name)
        self.value.remove(element)
        if self.ordered:
           self.order.remove(element)

    def discard(self, element):
        """Remove an element from the set.
           If the element is not a member, do nothing.
        """
        if self.virtual:
           raise KeyError, "Cannot discard element `"+str(element)+"' from virtual set "+str(self.name)
        if self.ordered and element in self.value:
           self.order.remove(element)
        self.value.discard(element)

    def ord(self, match_element):
        """ For ordered sets, return the position index (1-based) 
            of the input element.
        """
        if self.ordered is False:
           raise AttributeError, "Cannot invoke ord method for an unordered set!"
        # linear, but the only way given the current representation/attributes of a set.
        i=1
        for element in self.order:
           if match_element == element:
              return i
           i=i+1
        raise ValueError, "Unknown input element="+str(match_element)+" provided as input to ord() method for set="+str(self.name)

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tDim="+str(self.dim()),
        print >>ostream, "\tDimen="+str(self.dimen),
        print >>ostream, "\tSize="+str(len(self)),
        if self.domain is not None:
           print >>ostream, "\tDomain="+str(self.domain.name),
        else:
           print >>ostream, "\tDomain="+str(None),
        print >>ostream, "\tOrdered="+str(self.ordered),
        print >>ostream, "\tBounds="+str(self._bounds)
        if self.model is None:
           print >>ostream, "\t Model=None"
        else:
           print >>ostream, "\t Model="+str(self.model.name)
        if self.virtual:
           print >>ostream, "\t  Virtual"
        else:
           if self.ordered:
              tmp = copy.copy(self.order)
           else:
              tmp = copy.copy(list(self.value))
           tmp.sort()
           print >>ostream, "\t  ",tmp

    def __getitem__(self, key):
        if not self.ordered:
           raise IndexError, "Cannot get an item in unordered set "+self.name
        return self.order[key]

    def __len__(self):
        """ The number of items in the set.
            The set is empty until a concrete instance has been setup.
        """
        if self.virtual:
           raise ValueError, "The size of a virtual set is unknown"
        return len(self.value)

    #def __repr__(self):
        #"""Return string representation of the underlying set"""
        #return str(self)+" : "+str(self.value)

    def __iter__(self):
        """Return an iterator for the underlying set"""
        if self.virtual:
           raise TypeError, "Cannot iterate over Set object `"+self.name+"', which is a virtual set"
        if self.ordered:
           return self.order.__iter__()
        return self.value.__iter__()

    def __hash__(self):
        """Hash this object"""
        return _BaseSet.__hash__(self)

    def __eq__(self,other):
        """ Equality comparison """
        tmp = self._set_repn(other)
        if self.virtual:
            if other.virtual:
                return hash(self) == hash(tmp)
            return False
        if self.dimen != other.dimen:
           return False
        return self.value.__eq__( tmp )

    def __ne__(self,other):
        return not self.__eq__(other)

    def __contains__(self, element):
        """Report whether an element is a member of this set.
        (Called in response to the expression 'element in self'.)
        """
        #
        # If the element is a set, then see if this is a subset
        #
        if isinstance(element,_SetContainer):
           return element.issubset(self)
        #
        # If this is not a valid element, then return False
        #
        if not self._verify(element,False):
           return False
        #
        # If the restriction rule is used then we do not actually
        # check whether the data is in the set self.value.
        #
        if self.validate is not None and self.virtual:
           return True
        #
        # The final check: return true if self.virtual is True, since we should
        # have already validated this value
        #
        return self.virtual or element in self.value

    def issubset(self,other):
        """Report whether another set contains this set"""
        if self.virtual:
           raise TypeError, "ERROR: cannot perform \"issubset\" test because the current set is a virtual set."
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        for val in self.value:
          if val not in other:
             return False
        return True

    def issuperset(self,other):
        """Report this set contains another set"""
        if isinstance(other,_BaseSet):
           if other.virtual:
              raise TypeError, "ERROR: cannot perform \"issuperset\" test because the target set is a virtual set."
           return other.issubset(self) and (self.virtual or len(self) >= len(other))
        for val in other:
          if val not in self:
             return False
        return True

    __le__ = issubset
    __ge__ = issuperset

    def __lt__(self,other):
        if self.virtual or \
           (isinstance(other,_BaseSet) and other.virtual):
           raise TypeError, "ERROR: cannot test for __lt__ because either or both of the sets are virtual."
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        for val in self.value:
          if val not in other:
             return False
        return len(self) < len(other)

    def __gt__(self,other):
        if self.virtual or \
           (isinstance(other,_BaseSet) and other.virtual):
           raise TypeError, "ERROR: cannot test for __lt__ because either or both of the sets are virtual."
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        for val in other:
          if val not in self.value:
             return False
        return len(self) > len(other)

    def _set_repn(self,other):
        if isinstance(other,_SetContainer) and other.virtual:
            return other
        if isinstance(other,_SetContainer) and type(other.value) is not dict:
           return other.value
        raise TypeError, "Cannot apply Set operation with a "+str(type(other))+" object"
        
    def __or__(self,other):
        """ Return a _SetContainer object that is the union of this set
        with another set. """
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        def SetUnionRule(model):
            data = set()
            for val in getattr(model,SetUnionRule.Set1):
              data.add(val)
            for val in getattr(model,SetUnionRule.Set2):
              data.add(val)
            return data
        SetUnionRule.Set1 = self.name
        SetUnionRule.Set2 = other.name
        return _SetContainer(dimen=self.dimen, initialize=SetUnionRule)

    def __and__(self,other):
        """Return a _SetContainer object that is the intersection of this set
        with another set"""
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        def SetIntersectionRule(model):
            data = set()
            for val in getattr(model,SetIntersectionRule.Set1):
              if val in getattr(model,SetIntersectionRule.Set2):
                 data.add(val)
            return data
        SetIntersectionRule.Set1 = self.name
        SetIntersectionRule.Set2 = other.name
        return _SetContainer(dimen=self.dimen, initialize=SetIntersectionRule)

    def __xor__(self,other):
        """Return a _SetContainer object that is the symmetric difference of 
        this set with another set"""
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        def SetSymmetricDifferenceRule(M):
            Set1 = getattr(M,SetSymmetricDifferenceRule.Set1)
            Set2 = getattr(M,SetSymmetricDifferenceRule.Set2)
            data = set()
            for val in Set1:
              if val not in Set2:
                 data.add(val)
            for val in Set2:
              if val not in Set1:
                 data.add(val)
            return data
        SetSymmetricDifferenceRule.Set1 = self.name
        SetSymmetricDifferenceRule.Set2 = other.name
        return _SetContainer(dimen=self.dimen, initialize=SetSymmetricDifferenceRule)

    def __sub__(self,other):
        """Return a _SetContainer object that is the difference between this set
        and another set"""
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if self.dimen != other.dimen:
           raise ValueError, "Cannot perform set operation with sets "+self.name+" and "+other.name+" that have different element dimensions: "+str(self.dimen)+" "+str(other.dimen)
        def SetDifferenceRule(model):
            data = set()
            for val in getattr(model,SetDifferenceRule.Set1):
              if val not in getattr(model,SetDifferenceRule.Set2):
                 data.add(val)
            return data
        SetDifferenceRule.Set1 = self.name
        SetDifferenceRule.Set2 = other.name
        return _SetContainer(dimen=self.dimen, initialize=SetDifferenceRule)

    def __mul__(self,other):
        """Return a _ProductSet that is the cross-product between this set and
        and another set"""
        if not isinstance(other,_SetContainer):
           raise TypeError, "Set operator __mul__ cannot be applied with an object of type "+str(type(other))
        if self.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+self.name+"'"
        if other.virtual:
           raise TypeError, "Cannot perform set operations with virtual set '"+other.name+"'"
        if isinstance(self,_ProductSet) and self.name=="_unknown_":
           self.set_tuple = tuple( list(self.set_tuple) + [other] )
           self._compute_dimen()
           return self
        return _ProductSet(self,other)


class _SetArray(_BaseSet):
    """An array of sets, which are indexed by other sets"""

    def __init__(self, *args, **kwds):      #pragma:nocover
        """ Constructor """
        self._index_set=None
        self.value={}
        self._ndim=len(args)
        if len(args) == 1:
            if isinstance(args[0],_BaseSet):
                self._index=args[0]
            else:
                self._index=Set(initialize=args[0])
        else:
            self._index=None
            tmp = []
            for arg in args:
                if isinstance(arg,_BaseSet):
                    tmp.append(arg)
                else:
                    tmp.append( Set(initialize=arg) )
            self._index_set=tuple(tmp)
        _BaseSet.__init__(self,**kwds)
        self.value={}

    def keys(self):
        return self.value.keys()

    def __contains__(self, element):
        return element in self.value.keys()

    def clear(self):
        """Remove all elements from the set."""
        for key in self.value:
          self.value[key].clear()

    def data(self):
        """The underlying set data."""
        raise TypeError, "Cannot access underlying set data for array set "+self.name

    def __getitem__(self, key):
        if key not in self.value:
           raise KeyError, "Cannot access index "+str(key)+" in array set "+self.name
        return self.value[key]

    def __setitem__(self, key, val):
        if key not in self._index:
           raise KeyError, "Cannot set index "+str(key)+" in array set "+self.name
        if key in self.value:
           self.value[key].clear()
           for elt in val:
             self.value[key].add(elt)
        else:
           self.value[key] = Set(initialize=val,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
           self.value[key].construct()

    def __len__(self):
        result = 0
        for val in self.value.values():
            result += len(val)
        return result

    def __iter__(self):
        """Return an iterator for the set array"""
        return self.value.__iter__()

    def check_values(self):
        for key in self.value:
          for val in self.value[key]:
            self._verify(val,True)

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tDim="+str(self.dim()),
        print >>ostream, "\tDimen="+str(self.dimen),
        if self.domain is None:
           print >>ostream, "\tDomain="+str(self.domain),
        else:
           print >>ostream, "\tDomain="+str(self.domain.name),
        print >>ostream, "\tArraySize="+str(len(self.value.keys())),
        print >>ostream, "\tOrdered="+str(self.ordered)
        if self.model is None:
           print >>ostream, "\t Model=None"
        else:
           print >>ostream, "\t Model="+str(self.model.name)        
        tmp=self.value.keys()
        if tmp is not None:
            tmp.sort()
        else:
            tmp=[]
        for val in tmp:
          if self.ordered:
             ttmp = copy.copy(self.value[val].order)
          else:
             ttmp = copy.copy(list(self.value[val].value))
             ttmp.sort()
          print >>ostream, "\t",self.name+"["+str(val)+"]\t",ttmp

    def construct(self, values=None):
        """ Apply the rule to construct values in each set"""
        log.debug("Constructing _SetArray, name="+self.name+", from data="+repr(values))
        if self.virtual:                                #pragma:nocover
           raise TypeError, "It doesn't make sense to create a virtual set array"
        #
        # Construct using the values list
        #
        if values is not None:
           for key in values:
             if type(key) is tuple and len(key)==1:
                tmpkey=key[0]
             else:
                tmpkey=key
             if tmpkey not in self._index:
                raise KeyError, "Cannot set index "+str(tmpkey)+" in array set "+self.name
             self.value[tmpkey] = Set(initialize=values[key],within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(tmpkey)+"]",dimen=self.dimen)
             self.value[tmpkey].model = self.model
             self.value[tmpkey].construct()
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
           if self.model is None:
              raise ValueError, "Need model to construct a set array with a function"
           if self._index is None:
              raise ValueError, "No index for set "+self.name
           for key in self._index:
             if isinstance(key,tuple):
                tmp = list(key)
             else:
                tmp = [key]
             if self.initialize.func_code.co_argcount == len(tmp)+1:
                tmp.append(self.model)
                tmp = tuple(tmp)
                rule_list = list(self.initialize(*tmp))
             else:
                rule_list=[]
                ctr=0
                args = tuple(tmp+[ctr,self.model])
                val = self.initialize(*args)
                while val is not None:
                  rule_list.append(val)
                  ctr += 1
                  args = tuple(tmp+[ctr,self.model])
                  val = self.initialize(*args)
             if self.dimen is None and len(rule_list) > 0:
                   if type(rule_list[0]) in [tuple,list]:
                        self.dimen=len(rule_list[0])
                   else:
                        self.dimen=1
             self.value[key] = Set(initialize=rule_list,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
             self.value[key].model = self.model
             self.value[key].construct()
        #
        # Construct using the default values
        #
        else:
           if self.initialize is not None:
              if type(self.initialize) is not dict:
                 for key in self._index:
                   self.value[key] = Set(initialize=self.initialize,within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
                   self.value[key].model = self.model
                   self.value[key].construct()
              else:
                 for key in self.initialize:
                   self.value[key] = Set(initialize=self.initialize[key],within=self.domain,validate=self.validate,ordered=self.ordered,name=self.name+"["+str(key)+"]",dimen=self.dimen)
                   self.value[key].model = self.model
                   self.value[key].construct()


##------------------------------------------------------------------------
##
## A set that defines an abstract cross-product set.
##
##------------------------------------------------------------------------

class _ProductSet(_SetContainer):
    """Set that represents a cross-product of other sets"""

    """ Constructor
        Arguments:
           name         The name of this set
           initialize   Default set members, which may be overriden
                            when setting up this set
           rule         A rule for setting up this set with
                            existing model data.  This has the functional form:
                            f: pyomo.Model -> set
    """
    def __init__(self, *args, **kwd):
        self._class_override=False
        self.set_tuple = args
        tmp=()
        _SetContainer.__init__(self,*tmp,**kwd)
        self._compute_dimen()
        self._len=0

    def __iter__(self):
        """Returns an iterator/generator for the cross-product"""
        return pyutilib.misc.flattened_cross_iter(*self.set_tuple)

    def __len__(self):
        return self._len

    def _compute_dimen(self):
        ans=0
        for set in self.set_tuple:
            if set.dimen is None:
                self.dimen=None
                return
            else:
                ans += set.dimen
        self.dimen = ans

    def _verify(self,element,use_exception=True):
        """
        If this set is virtual, then an additional check is made
        to ensure that the element is in each of the underlying sets.
        """
        tmp = _SetContainer._verify(self,element,use_exception)
        if not tmp or not self.virtual:
            return tmp

        next_tuple_index = 0
        member_set_index = 0
        for member_set in self.set_tuple:
           tuple_slice = element[next_tuple_index:next_tuple_index + member_set.dimen]
           if member_set.dimen == 1:
              tuple_slice = tuple_slice[0]
           if tuple_slice not in member_set:
             return False
           member_set_index += 1
           next_tuple_index += member_set.dimen
        return True
        
    def construct(self, values=None):
        """ Apply the rule to construct values in this set """
        log.debug("Constructing _ProductSet, name="+self.name+", from data="+repr(values))
        if self.virtual:
           if len(self.set_tuple) == 0:
              self._len=0
           else:
              self._len=1
              for val in self.set_tuple:
                self._len *= len(val)
        #
        # Construct using the values list
        #
        elif values is not None:
           for val in values[None]:
             self.add(val)
        #
        # Construct using the rule
        #
        elif type(self.initialize) is types.FunctionType:
           for val in self.initialize(self.model):
             self.add(val)
        #
        # Construct using the default values
        #
        else:
           if self.initialize is not None:
              if type(self.initialize) is dict:
                 for val in self.initialize:
                   self.add(val)
              else:
                 self.add(self.initialize)
           else:
              for val in pyutilib.misc.cross(self.set_tuple):
                self.add(val)
        #
        if not self.virtual:
            self._len=len(self.value)
        self._compute_dimen()
        if self.dimen is None:
            raise ValueError, "The product set dimension must be computeable after constructing this set!"


class Set(object):
    """Set objects that are used to index other Pyomo objects

       This class has a similar look-and-feel as a built-in set class.  However,
       the set operations defined in this class return another abstract
       Set object.  This class contains a concrete set, which can be 
       initialized by the load() method.
    """
    def __new__(cls, *args, **kwds):
        if args == ():
            self = _SetContainer(*args, **kwds)
        else:
            self = _SetArray(*args, **kwds)
        return self


ComponentRegistration("Set", Set, "Set data that is used to define a model instance.")

