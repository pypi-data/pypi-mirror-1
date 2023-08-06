#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# Problem Writer for CPLEX LP Format Files
#

from coopr.opt import ProblemFormat
from coopr.pyomo.base import expr, Var, Constraint, Objective
from coopr.pyomo.base.var import _VarValue, _VarBase
from coopr.pyomo.base.param import _ParamValue
from coopr.pyomo.base.numtypes import minimize, maximize
from coopr.pyomo.base.expr import *
from coopr.pyomo.base import *
from coopr.opt.base import problem, AbstractProblemWriter

def convert_name(namestr):
    namestr = namestr.replace('[','(')
    namestr = namestr.replace(']',')')
    return namestr

class ProblemWriter_cpxlp(AbstractProblemWriter):

    def __init__(self):
        AbstractProblemWriter.__init__(self,ProblemFormat.cpxlp)

        # temporarily placing attributes used in extensive-form writing
        # here, for eventual migration to the base class.
        self._output_objectives = True
        self._output_constraints = True        
        self._output_variables = True # means we're outputting *some* variables - types determined by following flags.

        # building on the above, partition out the variables that should
        # be written if the _output_variables attribute is set to True.
        # this is useful when writing components of multiple models to a 
        # single LP file. unfortunately, the CPLEX LP format requires all
        # integer and binary (and continuous) variables to appear in a 
        # single continuous block.
        self._output_continuous_variables = True
        self._output_integer_variables = True
        self._output_binary_variables = True

        # do I pre-pend the model name to all identifiers I output?
        # useful in cases where you are writing components of multiple
        # models to a single output LP file.
        self._output_prefixes = False 

    def __call__(self, model, filename):
        if filename is None:
           filename = model.name + ".lp"
        OUTPUT=open(filename,"w")
        self._print_model_LP(model,OUTPUT)
        OUTPUT.close()
        return filename, None

    def _get_bound(self, exp):
        if isinstance(exp,expr._IdentityExpression):
           return self._get_bound(exp._args[0])
        elif isinstance(exp,NumericConstant):
           return exp.value
        else:
           raise ValueError, "ERROR: nonconstant bound: " + str(exp)
           return None

    def _print_bound(self, exp, OUTPUT, offset=0.0):
        if isinstance(exp,expr._IdentityExpression):
           self._print_bound(exp._args[0], OUTPUT, offset)
        elif isinstance(exp,NumericConstant) or isinstance(exp,_ParamValue):
           print >>OUTPUT, exp.value+offset
        else:
           # Idea: Bundle the following into a single string and pass with thrown exception
           print "ERROR: nonconstant constraint bound"
           print "Expression type=" + exp.__class__.__name__
           if not exp is None:
                print "Offending expression:"
                exp.pprint()
           raise ValueError

    def _collect_key(self, a):
        return a[0]

    def _print_linterm(self, x, OUTPUT, print_mult=True, cleanup_names=False, print_offset=False):
        if len(x) <= 0:
           raise ValueError, "ERROR: zero-length value in _print_linterm"
        # x maps variable labels to (numeric-coefficient, _VarValue) pairs.
        # y will consist of pairs of variable names and their corresponding coefficients, 
        # basically just stripping out the "_VarValue" component of the input x.       
        y = []
        for i in x.keys():
           output_label = i
           if (self._output_prefixes is True) and (isinstance(x[i][1], _VarValue) is True):
              parent_model = x[i][1].var.model
              if parent_model is None:
                 raise ValueError, "Variable="+x[i][1].var.name+" has no parent model defined - required when outputting LP files when _output_prefixes is enabled"
              output_label = parent_model.name + "_" + output_label
           y.append((output_label,x[i][0]))
        y = sorted(y, key=self._collect_key)
#        print "_print_linterm x: ",x
#        print "_print_linterm y: ",y
        op = None
        offset=0.0
        max_terms_on_line=5 # this is the line-limit hack
        terms_output = 0
        for i in y:
                  c = i[1]
                  if op != None:
                           if c < 0:
                                    c = -c
                                    op = "-"
                           print >>OUTPUT, op,
                  if i[0] == "0":
                     # a key equal to "0" indicates the offset
                     if print_offset:
                        print >>OUTPUT, c, "ONE_VAR_CONSTANT"
                        terms_output += 1
                        op = "+"
                     else:
                        offset = c
                        op = None
                  else:
                     print >>OUTPUT, c,
                     print >>OUTPUT, convert_name(i[0]),
                     terms_output += 1
                     if terms_output >= max_terms_on_line:
                        print >>OUTPUT, ""
                        terms_output = 0
                     op = "+"
        return offset

    def _print_quadterm(self, x, is_minimizing, OUTPUT):
        # the LP format doesn't allow for expression of constant terms in the objective.
        # a work-around involves tracking the sum of constant terms in the quadratic
        # quadratic terms, and then writing that out with a dummy variable forced equal
        # to one.
        print >>OUTPUT, ""
        for arg in x._args:
            if isinstance(arg,expr._ProductExpression):
                # NOTE: we need to handle quadratics defined with the 'pow' term here.
                # WARNING: The following code is very specific to progressive hedging, with
                #          a very specific format assumed. we do need to handle more general
                #          expressions, but we'll worry about that at a latter time.
                blend = arg._numerator[0]()

                if blend is 1:

                   rho = arg._numerator[1]()

                   pow_expression = arg._numerator[2]
                
                   base = pow_expression._args[0]
                   exponent = pow_expression._args[1]

                   if not isinstance(base,expr._SumExpression):
                       raise ValueError, "Quadratic term base must be a _SumExpression"
                   if not isinstance(exponent,numvalue.NumericConstant):
                       raise ValueError, "Quadratic term exponent must be a NumericConstant"
                   variable = base._args[0]
                   offset = base._args[1]
                   if variable.status is not VarStatus.unused:

                      if is_minimizing is True:
                         print >>OUTPUT, " + [" + str(rho) + " " + convert_name(variable.label) + "^2]/2",
                      else:
                         print >>OUTPUT, " - [" + str(rho) + " " + convert_name(variable.label) + "^2]/2",

                      if (is_minimizing is True):
                         if offset.value < 0.0:
                            print >>OUTPUT, " + " + str(abs(rho*offset.value)) + " " + convert_name(variable.label),                    
                         else:
                            print >>OUTPUT, " - " + str(rho*offset.value) + " " + convert_name(variable.label),
                      else:
                         if offset.value < 0.0:
                            print >>OUTPUT, " - " + str(abs(rho*offset.value)) + " " + convert_name(variable.label),                    
                         else:
                            print >>OUTPUT, " + " + str(rho*offset.value) + " " + convert_name(variable.label),

                      objective_offset = (rho * offset.value * offset.value / 2.0)
                      if is_minimizing is True:
                         print >>OUTPUT, " + " + str(objective_offset) + " ONE_VAR_CONSTANT"
                      else:
                         print >>OUTPUT, " - " + str(objective_offset) + " ONE_VAR_CONSTANT"
                      
            elif isinstance(arg,numvalue.NumericConstant):
                # this is the "0.0" element that forms the initial expression - the
                # quadratic sub-expressions aren't known to the presolve routines.
                # ideally unnecessary - hacked in for now.
                pass

            else:
                print `arg`
                raise ValueError, "Unknown expression sub-type found in quadratic objective expression"    

    def _print_model_LP(self, model, OUTPUT):

        _obj = model.active_components(Objective)
        
        #
        # Objective
        #
        if self._output_objectives is True:
           printed_quadterm = False
           if len(_obj) == 0:
              raise ValueError, "ERROR: No objectives defined for input model=" + str(model.name) + "; cannot write legal LP file"
           if _obj[ _obj.keys()[0] ].sense == maximize:
              print >>OUTPUT, "max "
           else:
              print >>OUTPUT, "min "
           print >>OUTPUT, "obj: ",
           obj = _obj[ _obj.keys()[0] ]
           for key in obj._linterm:
                if (len(obj._linterm[key]) == 0) or ((len(obj._linterm[key]) == 1) and (obj._linterm[key].keys()[0] == "0")):
                    continue
                self._print_linterm(obj._linterm[key], OUTPUT, print_mult=False, cleanup_names=True, print_offset=True)
           if obj._quad_subexpr is not None:
               self._print_quadterm(obj._quad_subexpr, (_obj[ _obj.keys()[0] ].sense == minimize), OUTPUT)
               printed_quadterm = True
           print >>OUTPUT, ""
        
        #
        # Constraints
        #
        # the "Cnontriv" attribute of the model is created on-the-fly, by the _Collect method in problem_utils.py.
        #
        # if there are no non-trivial constraints, you'll end up with an empty constraint block. CPLEX is OK with
        # this, but GLPK isn't. And eliminating the constraint block (i.e., the "s.t." line) causes GLPK to whine
        # elsewhere. output a warning if the constraint block is empty, so users can quickly determine the cause
        # of the solve failure.

        if self._output_constraints is True:

           # for now, if this routine isn't writing everything, then assume a meta-level handler is
           # dealing with the writing of the transitional elements - these should probably be done in
           # the form of "end_objective()" and "end_constraint()" helper methods.                    
           if (self._output_objectives is True) and (self._output_variables is True):
              print >>OUTPUT, "s.t."
           
           CON = model.active_components(Constraint)
           for key in model.Cnontriv:
             i=0
             C = CON[key]
             for cndx in C.keys():
               if not C[cndx].active:
                    continue
               try:
                  # there are conditions, e.g., when fixing variables, under which a constraint block might be empty.
                  # ignore these, for both practical reasons and the fact that the CPLEX LP format requires a variable
                  # in the constraint body. it is also possible that the body of the constraint consists of only a
                  # constant, in which case the "variable" of
                  if (len(C._linterm[cndx]) > 1) or ((len(C._linterm[cndx]) == 1) and (C._linterm[cndx].keys()[0] != "0")):
                     prefix = ""
                     if self._output_prefixes is True:
                        if C.model is None:
                           raise RuntimeError, "Constraint="+C._data[cndx].label+" has no model attribute - no label prefix can be assigned"
                        prefix = C.model.name+"_"

                     if C._data[cndx]._equality:
                         #
                         # Equality constraint
                         #
                         print >>OUTPUT, prefix + "c_e_" + convert_name(C._data[cndx].label) + "_: ",
                         offset = self._print_linterm(C._linterm[cndx], OUTPUT, print_mult=False, cleanup_names=True)
                         print >>OUTPUT, "=",
                         self._print_bound(C._data[cndx].lower, OUTPUT, -offset)
                         print >>OUTPUT, ""
                         i=i+1
                     else:
                         #
                         # Inequality constraint
                         #
                         if C._data[cndx].lower is not None:
                            print >>OUTPUT, prefix + "c_l_" + convert_name(C._data[cndx].label) + "_: ",
                            offset = self._print_linterm(C._linterm[cndx], OUTPUT, print_mult=False, cleanup_names=True)
                            print >>OUTPUT, ">=",
                            self._print_bound(C._data[cndx].lower, OUTPUT, -offset)
                            print >>OUTPUT, ""
                            i=i+1
                         if C._data[cndx].upper is not None:
                            print >>OUTPUT, prefix + "c_u_" + convert_name(C._data[cndx].label) + "_: ",
                            offset = self._print_linterm(C._linterm[cndx], OUTPUT, print_mult=False, cleanup_names=True)
                            print >>OUTPUT, "<=",
                            self._print_bound(C._data[cndx].upper, OUTPUT, -offset)
                            print >>OUTPUT, ""
                            i=i+1
               except ValueError, msg:
                  print msg
                  raise ValueError, "ERROR: Failed to output constraint="+C.name+", index="+`cndx`+" in generation of LP format file"
           if len(model.Cnontriv) == 0:
             print "WARNING: Empty constraint block written in LP format - solver may error"
          
           # the CPLEX LP format doesn't allow constants in the objective (or constraint body), which is a bit silly.
           # to avoid painful book-keeping, we introduce the following "variable", constrained to the value 1. this is
           # used when quadratic terms are present. worst-case, if not used, is that CPLEX easily pre-processes it out.
           print >>OUTPUT, "c_e_ONE_VAR_CONSTANT: ONE_VAR_CONSTANT = 1.0"
           print >>OUTPUT, ""
           
        #
        # Bounds
        #

        if self._output_variables is True:

           # for now, if this routine isn't writing everything, then assume a meta-level handler is
           # dealing with the writing of the transitional elements - these should probably be done in
           # the form of "end_objective()" and "end_constraint()" helper methods.                    
           if (self._output_objectives is True) and (self._output_constraints is True):
              print >>OUTPUT, "bounds "

           # scan all variables even if we're only writing a subset of them. required
           # because we don't store maps by variable type currently.
           
           # track the number of integer and binary variables, so you can output their status later.
           niv = nbv = 0
           VAR = model.active_components(Var)
           for var in VAR.values():
              if isinstance(var.domain, IntegerSet):
                 niv += 1
              elif isinstance(var.domain, BooleanSet):
                 nbv += 1

              if self._output_continuous_variables is True:
                 for ndx in var._varval.keys():
                    if not var._varval[ndx].active:
                        continue
                    prefix = ""
                    if self._output_prefixes is True:
                       prefix = convert_name(var.model.name)+"_"

                    if var[ndx].id != -1: # if the variable isn't referenced in the model, don't output bounds...
                       # in the CPLEX LP file format, the default variable bounds are 0 and +inf.
                       # these bounds are in conflict with Pyomo, which assumes -inf and inf (which
                       # we would argue is more rational).
                       print >>OUTPUT,"   ",
                       if var[ndx].lb is not None:
                          print >>OUTPUT, str(value(var[ndx].lb())) + " <= ",
                       else:
                          print >>OUTPUT, " -inf <= ",
                       name_to_output = prefix+convert_name(var[ndx].label)
                       if name_to_output == "e":
                          raise ValueError, "Attempting to write variable with name=e in a CPLEX LP formatted file - will cause a parse failure due to confusion with numeric values expressed in scientific notation"
                       print >>OUTPUT, name_to_output,
                       if var[ndx].ub is not None:
                          print >>OUTPUT, " <= " + str(value(var[ndx].ub())),
                          print >>OUTPUT, ""
                       else:
                          print >>OUTPUT, " <= +inf"
                       
           if (niv > 0) and (self._output_integer_variables is True): 

              # if we're outputting the whole model, then assume we can output the "integer"
              # header. if not, then assume a meta-level process is taking care of it.
              if (self._output_objectives is True) and (self._output_constraints is True):              
                 print >>OUTPUT, "integer"

              prefix = ""
              if self._output_prefixes is True:
                 prefix = convert_name(var.model.name)+"_"

              for var in VAR.values():
                 if isinstance(var.domain, IntegerSet):
                    for ndx in var.keys():
                       if not var[ndx].active:
                            continue
                       if var[ndx].id != -1: # if the variable isn't referenced, skip.
                          print >>OUTPUT, "   ", prefix+convert_name(var[ndx].label)

           if (nbv > 0) and (self._output_binary_variables is True):

              # if we're outputting the whole model, then assume we can output the "binary"
              # header. if not, then assume a meta-level process is taking care of it.
              if (self._output_objectives is True) and (self._output_constraints is True):              
                 print >>OUTPUT, "binary"

              prefix = ""
              if self._output_prefixes is True:
                 prefix = convert_name(var.model.name)+"_"

              for var in VAR.values():
                 if isinstance(var.domain, BooleanSet):
                    for ndx in var.keys():
                       if not var[ndx].active:
                            continue
                       if var[ndx].id != -1: # if the variable isn't referenced, skip.
                          print >>OUTPUT, "   ", prefix+convert_name(var[ndx].label)

        #
        # wrap-up
        #

        if (self._output_objectives is True) and (self._output_constraints is True) and (self._output_variables is True):
           #
           # End
           #
           print >>OUTPUT, "end "
        
problem.WriterRegistration(str(ProblemFormat.cpxlp), ProblemWriter_cpxlp)
