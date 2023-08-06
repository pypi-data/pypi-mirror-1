#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import copy
import re
import sys

from plugin import *
from numvalue import *

import pyutilib.plugin.core
from pyutilib.math import *
from pyutilib.misc import quote_split, tuplize, Container

from coopr.opt import ProblemFormat, ResultsFormat, guess_format
from coopr.pyomo.base.var import _VarValue
import coopr.opt
from PyomoModelData import ModelData
import pyomo

from component import Component
from sets import Set, _ProductSet, _SetContainer, _BaseSet
from rangeset import RangeSet
from var import Var
from constraint import Objective, Constraint, ConstraintData
from param import Param


class Model(Component):
    """
    The MINLP model that will be analyzed by the user.
    """

    presolver_ep = pyutilib.plugin.core.ExtensionPoint(IPyomoPresolver)


    def __init__(self):
        """Constructor"""
        Component.__init__(self, ctype=Model)
        #
        # Define component dictionary: component type -> instance
        #
        self._component={}
        for item in pyutilib.plugin.core.ExtensionPoint(IModelComponent):
            self._component[ item.cls() ] = {}
        #
        # A list of the declarations, in the order that they are
        # specified.
        #
        self._declarations=[]
        # the _name_varmap and _name_conmap dictionarys are assigned when 
        # the problem definition
        # file is written, i.e., via the write() command. intent
        # is to map names that will be coming back from a solver
        # into Pyomo variables. Values are of type _VarValue.
        self._name_varmap={}
        self._name_conmap={}
        self._name_objmap={}
        self.name="unknown"
        self.tmpctr=0
        self._varctr=0
        self._presolvers = ["simple_presolver"]
        #
        # Dictionaries that map from id to Variable/Constraints
        #
        self._var = {}
        self._con = {}
        self._obj = {}
        #
        # Model statistics
        #
        self.statistics = Container()

    def components(self, ctype=None):
        if ctype is None:
            return self._component
        if ctype in self._component:
             return self._component[ctype]
        raise KeyError, "Unknown component type: %s" % str(ctype)

    def nvariables(self):
        return self.statistics.number_of_variables

    def variable(self, name):
        if isinstance(name,basestring):
            return self._name_varmap[name]
        else:
            return self._var[name]

    def variables(self):
        return self._name_varmap

    def nconstraints(self):
        return self.statistics.number_of_constraints

    def constraint(self, name):
        if isinstance(name,basestring):
            return self._name_conmap[name]
        else:
            return self._con[name]

    def constraints(self):
        return self._name_conmap

    def nobjectives(self):
        return self.statistics.number_of_objectives

    def objective(self, name):
        if isinstance(name,basestring):
            return self._name_objmap[name]
        else:
            return self._obj[name]

    def objectives(self):
        return self._name_objmap


    def active_components(self, _ctype=None):
        tmp = {}
        if _ctype is None:
            for ctype in self._component:
                tmp[ctype]={}
        elif _ctype in self._component:
            tmp[_ctype]={}
        else:
            raise KeyError, "Unknown component type: %s" % str(ctype)
        for ctype in tmp:
            for name in self._component[ctype]:
                comp = self._component[ctype][name]
                if comp.active:
                    tmp[ctype][name] = comp
        if not _ctype is None:
            return tmp[_ctype]
        print "ACTIVE",tmp
        return tmp

    def num_used_variables(self):
        return len(self._var)


    def valid_problem_types(self):
        return [ProblemFormat.pyomo]


    def _add_temporary_set(self,val):
        if val._index_set is not None:
            ctr=0
            for tset in val._index_set:
                if tset.name == "_unknown_":
                    self._construct_temporary_set(tset,val.name+"_index_"+str(ctr))
                ctr+=1
            val._index = self._construct_temporary_set(val._index_set,val.name+"_index")
        if isinstance(val._index,_SetContainer) and \
            val._index.name == "_unknown_":
            self._construct_temporary_set(val._index,val.name+"_index")
        if val.domain is not None and val.domain.name == "_unknown_":
            self._construct_temporary_set(val.domain,val.name+"_domain")


    def _construct_temporary_set(self, obj, name):
        if type(obj) is tuple:
           if len(obj) == 1:                #pragma:nocover
                  raise Exception, "Unexpected temporary set construction"
           else:
                  tobj=_ProductSet(*obj)
                  setattr(self,name,tobj)
                  tobj.virtual=True
                  return tobj
        if isinstance(obj,_BaseSet):
           setattr(self,name,obj)
           return obj


    def _clear_attribute(self,name):
        #
        # Cleanup Old Model Declaration First
        #
        i=0
        for decl in self._declarations:
            if decl.name == name:
                self.__dict__[name]=None
                del self._declarations[i]
                for item in self._component:
                    if name in self._component[item]:
                        del self._component[item][name]
                        break
                break
            i += 1

    def _setattr_exec(self,name,val):
        self._clear_attribute(name)
        val.name=name
        self._add_temporary_set(val)
        self._component[val.type()][name]=val
        self._declarations.append(val)
        self.__dict__[name]=val
        if not val.type() is Model:
            val.model=self

    def __setattr__(self,name,val):
        """Set attributes"""
        #
        # Set Model Declaration
        #
        if name != "_component":
            #
            # If this is a component type, then simply set it
            #
            if isinstance(val,Component):
                self._setattr_exec(name,val)
                return
        #
        # Try to set the value.  This may fail if the attribute does not already
        # exist in this model, if the set_value function is not defined, or if
        # a bad value is provided.  In the latter case, a ValueError will be thrown, which
        # we raise.  Otherwise, this is an object that we need to set directly.
        #
        try:
            self.__dict__[name].set_value(val)
        except ValueError, e:
            raise
        except Exception, e:
            self.__dict__[name]=val


    def create(self, filename=None, name=None):
        """
        Create a concrete instance of this Model, possibly using data
        read in from a file.
        """
        instance = self.clone()
        instance.load(filename)
        instance.presolve()
        if not name is None:
            instance.name=name
        return instance


    def clone(self):
        """Create a copy of this model"""
        for declaration in self._declarations:
          declaration.model = None
        instance = copy.deepcopy(self)
        for declaration in self._declarations:
          declaration.model = self
        for declaration in instance._declarations:
          declaration.model = instance
        return instance


    def reset(self):
        for declaration in self._declarations:
            declaration.reset()


    def presolve(self):
        """Apply the presolvers defined by the user"""
        for item in self._presolvers:
            self = Model.presolver_ep.service(item).presolve(self)
        

    def solution(self):
        """Return the solution"""
        soln = []
        for i in range(len(self._var)):
            soln.append( self._var[i].value )
        return soln


    def load(self, arg):
        """ Load the model with data from a file or a Solution object """
        if arg is None or type(arg) is str:
           self._load_model_data(ModelData(filename=arg,model=self))
           return True
        elif type(arg) is ModelData:
           self._load_model_data(arg)
           return True
        elif type(arg) is coopr.opt.SolverResults:
           if arg.solver.status != coopr.opt.SolverStatus.ok:
              raise ValueError, "Cannot load a SolverResults object with bad status: "+str(arg.solver.status)
           if len(arg.solution) > 0:
              self._load_solution(arg.solution(0),symbol_map=arg.symbol_map)
              return True
           else:
              return False
        elif type(arg) is coopr.opt.Solution:
           self._load_solution(arg)
           return True
        elif type(arg) in (tuple, list):
           self._load_solution(arg)
           return True
        else:
           raise ValueError, "Cannot load model with object of type "+str(type(arg))


    def _tuplize(self, data, setobj):
        if data is None:            #pragma:nocover
           return None
        if setobj.dimen == 1:
           return data
        ans = {}
        for key in data:
          if type(data[key][0]) is tuple:
             return data
          ans[key] = tuplize(data[key], setobj.dimen, setobj.name)
        return ans


    def _load_model_data(self,modeldata):
        """
        Load declarations from a ModelData object.
        """
        #print "HERE _load_model_data",self._declarations
        for declaration in self._declarations:
            if declaration.type() is Model:
                continue
            tmp = declaration.name
            if tmp in modeldata._default.keys():
                if declaration.type() is Set:
                    declaration.default = self._tuplize(modeldata._default[tmp],declaration)
                else:
                    declaration.default = modeldata._default[tmp]
            if tmp in modeldata._data.keys():
                #print "HERE", declaration.name, str(declaration.dimen),modeldata._data[tmp]
                if declaration.type() is Set:
                    data = self._tuplize(modeldata._data[tmp],declaration)
                else:
                    data = modeldata._data[tmp]
            else:
                data = None
            if pyomo.debug("generate"):           #pragma:nocover
                print "About to generate '"+declaration.name+"' with data: "+str(data)
                self.pprint()
            declaration.construct(data)
            try:
                pass
            except Exception, err:
                print "Error constructing declaration "+str(declaration.name)+" from data="+str(data)
                print "ERROR: "+str(err)
                raise err

    def _load_solution(self, soln, symbol_map=None):
        """
        Load a solution.
        """
        # Load list or tuple into the variables, based on their order
        if type(soln) in (list, tuple):
            if len(soln) != len(self._var):
                raise ValueError, "Attempting to load a list/tuple solution into a model, but its length is %d while the model has %d variables" % (len(soln), len(self._var))
            for i in range(len(soln)):
                self._var[i].value = soln[i]
            return
        #
        # Load variable data
        #
        for name in soln.variable:
          #
          # NOTE: the following is a hack, to handle the ONE_VAR_CONSTANT variable
          #       that is necessary for the objective constant-offset terms.
          #       probably should create a dummy variable in the model map at the same
          #       time the objective expression is being constructed.
          #
          if name != "ONE_VAR_CONSTANT":
             # translate the name first if there is a variable map associated with the input solution.
             if symbol_map is not None:
                 name = symbol_map[name]
             if name not in self._name_varmap:
                names=""
                raise KeyError, "Variable name '"+name+"' is not in model "+self.name+".  Valid variable names: "+str(self._name_varmap.keys())
             if not isinstance(self._name_varmap[name],_VarValue):
                raise TypeError, "Variable '"+name+"' in model '"+self.name+"' is type "+str(type(self._name_varmap[name]))
             if self._name_varmap[name].fixed is True:
                raise TypeError, "Variable '"+name+"' in model '"+self.name+"' is currently fixed - new value is not expected in solution"

             #print "HERE",soln.variable[name].keys()
             for _key in soln.variable[name].keys():
                key = _key[0].lower() + _key[1:] 
                if key == 'value':
                    self._name_varmap[name].value = soln.variable[name].value
                elif not key == 'id':
                    setattr(self._name_varmap[name], key, getattr(soln.variable[name], _key))
        #
        # Load constraint data
        #
        for name in soln.constraint:
             #
             # This is a hack
             #
             if name.endswith('ONE_VAR_CONSTANT'):
                continue
             if symbol_map is not None:
                name = symbol_map[name]
             #
             # This is a hack.  Is there a standard convention for constraint
             # names that we can apply to all data formats?
             #
             if name[0:2] == 'c_':
                _name = name[4:-1]
             #print "HERE",_name
             if _name not in self._name_conmap:
                names=""
                raise KeyError, "Constraint name '"+name+"' is not in model "+self.name+".  Valid constraint names: "+str(self._name_conmap.keys())
             if not isinstance(self._name_conmap[_name],ConstraintData):
                raise TypeError, "Constraint '"+name+"' in model '"+self.name+"' is type "+str(type(self._name_conmap[_name]))

             #print "HERE",soln.constraint[name].keys()
             for _key in soln.constraint[name].keys():
                key = _key[0].lower() + _key[1:] 
                if key == 'value':
                    self._name_conmap[name].value = soln.constraint[name].value
                elif not key == 'id':
                    setattr(self._name_conmap[_name], key, getattr(soln.constraint[name], _key))

    def write(self,filename=None,format=ProblemFormat.cpxlp):
        """
        Write the model to a file, with a given format.
        """
        if format is None and not filename is None:
            #
            # Guess the format
            #
            format = guess_format(filename)
        problem_writer = coopr.opt.WriterFactory(format)
        if problem_writer is None:
           raise ValueError, "Cannot write model in format \"" + str(format) + "\": no model writer registered for that format"
        (fname, symbol_map) = problem_writer(self, filename)
        if pyomo.debug("verbose"):
           print "Writing model "+self.name+" to file '"+str(fname)+"'  with format "+str(format)
        return fname, symbol_map


    def pprint(self, filename=None, ostream=None):
        """
        Print a summary of the model info
        """
        if ostream is None:
           ostream = sys.stdout
        if filename is not None:
           OUTPUT=open(filename,"w")
           self.pprint(ostream=OUTPUT)
           OUTPUT.close()
           return
        if ostream is None:
           ostream = sys.stdout
        #
        # We hard-code the order of the core Pyomo modeling
        # components, to ensure that the output follows the logical
        # expected by a user.
        #
        items = [Set, RangeSet, Param, Var, Objective, Constraint]
        for item in pyutilib.plugin.core.ExtensionPoint(IModelComponent):
            if not item in items:
                items.append(item)
        for item in items:
            if not item in self._component:
                continue
            keys = self._component[item].keys()
            keys.sort()
            #
            # NOTE: these conditional checks should not be hard-coded.
            #
            print >>ostream, len(keys), item.__name__+" Declarations"
            for key in keys:
                self._component[item][key].pprint(ostream)
            print >>ostream, ""
        #
        # Model Order
        #
        print >>ostream, len(self._declarations),"Declarations:",
        for i in range(0,len(self._declarations)):
          print >>ostream, self._declarations[i].name,
        print >>ostream, ""


    def display(self, filename=None, ostream=None):
        """
        Print the Pyomo model in a verbose format.
        """
        if filename is not None:
           OUTPUT=open(filename,"w")
           self.display(ostream=OUTPUT)
           OUTPUT.close()
           return
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "Model "+self.name
        print >>ostream, ""
        print >>ostream, "  Variables:"
        VAR = self.active_components(Var)
        if len(VAR) == 0:
            print >>ostream, "    None"
        else:
            for ndx in VAR:
                VAR[ndx].display(prefix="    ",ostream=ostream)
        print >>ostream, ""
        print >>ostream, "  Objectives:"
        OBJ = self.active_components(Objective)
        if len(OBJ) == 0:
            print >>ostream, "    None"
        else:
            for ndx in OBJ:
                OBJ[ndx].display(prefix="    ",ostream=ostream)
        print >>ostream, ""
        CON = self.active_components(Constraint)
        print >>ostream, "  Constraints:"
        if len(CON) == 0:
            print >>ostream, "    None"
        else:
            for ndx in CON:
                CON[ndx].display(prefix="    ",ostream=ostream)

ComponentRegistration("Model", Model, "Model objects can be used as a component of other models.")
