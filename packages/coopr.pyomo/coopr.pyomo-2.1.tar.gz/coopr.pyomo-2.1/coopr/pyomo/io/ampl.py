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
# AMPL Problem Writer Plugin
#

from coopr.opt import ProblemFormat, WriterFactory
from coopr.pyomo.base.numtypes import minimize, maximize
from coopr.pyomo.base import *
from coopr.opt.base import *
from coopr.pyomo.base.param import _ParamValue
from coopr.pyomo.base.var import _VarBase

class ProblemWriter_nl(AbstractProblemWriter):

    def __init__(self):
        AbstractProblemWriter.__init__(self,ProblemFormat.nl)

    def __call__(self, model, filename):
        if filename is None:
           filename = model.name + ".nl"
        OUTPUT=open(filename,"w")
        symbol_map = self._print_model_NL(model,OUTPUT)
        OUTPUT.close()
        return filename, symbol_map

    def _get_bound(self, exp):
        if isinstance(exp,expr._IdentityExpression):
           return self._get_bound(exp._args[0])
        elif isinstance(exp,NumericConstant):
           return exp.value
        elif isinstance(exp,_ParamValue):
           return exp.value
        else:
           raise ValueError, "ERROR: nonconstant bound: " + str(exp)
           return None

    def _print_model_NL(self,model, OUTPUT, verbose=False):

        # maps NL variables to the "real" variable names in the problem.
        # it's really NL variable ordering, as there are no variable names
        # in the NL format. however, we by convention make them go from
        # x0 upward.
        symbol_map = {}

        #
        # Collect statistics
        #
        nc = no = neqn = nrange = 0
        Obj = model.active_components(Objective)
        Con = model.active_components(Constraint)
        Vars = model.active_components(Var)
        Onontriv = model.Onontriv
        for obj in Onontriv:
                O = Obj[obj]
                no += len(O._Onz)
        Cnontriv = model.Cnontriv
        for con in Cnontriv:
                C = Con[con]
                nc += len(C._Cnz)
                for i in C._Cnz:
                  if C[i].lower is not None:
                           L = self._get_bound(C[i].lower)
                           if C[i].upper is not None:
                                    U = self._get_bound(C[i].upper)
                                    if (L == U):
                                             neqn += 1
                                    elif L > U:
                                             raise ValueError, "Constraint " + str(con) +\
                                             "[" + str(i) + "]: lower bound = " + str(L) +\
                                             " > upper bound = " + str(U)
                                    else:
                                             nrange += 1

        icv = 0
        Ilist = []
        Blist = []
        Vlist = []
        for var in Vars.values():
                Vv = var._varval
                if isinstance(var.domain, IntegerSet):
                  # print "Domain of", var._name, "= Integers"
                  for ndx in Vv:
                           if Vv[ndx].id >= 0:
                                    Ilist.append((var,ndx))
                elif isinstance(var.domain, BooleanSet):
                  # print "Domain of", var._name, "= Boolean"
                  for ndx in Vv:
                           if Vv[ndx].id >= 0:
                              L = Vv[ndx].lb()
                              U = Vv[ndx].ub()
                              if L is not None and value(L) == 0 \
                                 and U is not None and value(U) == 1:
                                        Blist.append((var,ndx))
                              else:
                                        Ilist.append((var,ndx))
                else:
                  # print "Domain of", var_.name, "is not discrete."
                  for ndx in Vv:
                           Vi = Vv[ndx]
                           if Vi.id >= 0:
                                    Vi.id = icv
                                    icv += 1
                                    Vlist.append((var,ndx))
        for x in Blist:
                x[0][x[1]].id = icv
                icv += 1
                Vlist.append((x[0],x[1]))
        for x in Ilist:
                x[0]._varval[x[1]].id = icv
                icv += 1
                Vlist.append((x[0],x[1]))
        #
        # Print Header
        #
        # LINE 1
        #
        print >>OUTPUT,"g3 1 1 0\t# problem",model.name
        #
        # LINE 2
        #
        print >>OUTPUT, " " + str(model.statistics.number_of_variables), nc, no, nrange, str(neqn) +\
                "\t# vars, constraints, objectives, ranges, eqns"
        #
        # LINE 3
        #
        print >>OUTPUT, " 0 0\t# nonlinear constraints, objectives"
        #
        # LINE 4
        #
        print >>OUTPUT, " 0 0\t# network constraints: nonlinear, linear"
        #
        # LINE 5
        #
        print >>OUTPUT, " 0 0 0\t# nonlinear vars in constraints, objectives, both"
        #
        # LINE 6
        #
        print >>OUTPUT, " 0 0 0 1\t# linear network variables; functions; arith, flags"
        #
        # LINE 7
        #
        niv = nbv = 0
        for var in Vars.values():
                Vv = var._varval
                if isinstance(var.domain, IntegerSet):
                  for i in Vv.keys():
                           if Vv[i].id >= 0:
                                    niv += 1
                elif isinstance(var.domain, BooleanSet):
                  for i in Vv.keys():
                           if Vv[i].id >= 0:
                                    nbv += 1
        print >>OUTPUT, " " + str(nbv), niv, 0, 0,\
                "0\t# discrete variables: binary, integer, nonlinear (b,c,o)"
        #
        # LINE 8
        #
        nsno = model.statistics.number_of_variables
        ngc = ngo = 0
        for key in Obj:
                for obj in Obj[key]._linterm:
                    ngo += len(Obj[key]._linterm[obj])
        cu = {}
        for i in xrange(nsno):
                cu[i] = 0
        #Con = model.components(Constraint)
        for key in Cnontriv:
                C = Con[key]
                for cndx in C._Cnz:
                  LT = C._linterm[cndx]
                  #print "HERE",LT.keys()
                  for i in LT:
                           #print "HERE",i,type(LT[i]),LT[i],type(LT[i][1]),LT[i][1]
                           if i != '0':
                              ngc += 1
                              cu[LT[i][1].id] += 1
        print >>OUTPUT, " " + str(ngc), str(ngo) + "\t# nonzeros in Jacobian, gradients"
        #
        # LINE 9
        #
        print >>OUTPUT, " 0 0\t# max name lengths: constraints, variables"
        #
        # LINE 10
        #
        print >>OUTPUT, " 0 0 0 0 0\t# common exprs: b,c,o,c1,o1"
        #
        # "C" lines
        #
        nc = 0
        for key in Cnontriv:
                for cndx in Con[key]._Cnz:
                  print >>OUTPUT, "C" + str(nc) + "\t#" + str(key) + "[" + str(cndx) + "]"
                  nc += 1
                  #if '0' in Con[key]._linterm[cndx]:
                  #  print >>OUTPUT, "n"+str(Con[key]._linterm[cndx]['0'][0])
                  #else:
                  #  print >>OUTPUT, "n0"
                  print >>OUTPUT, "n0"
        #
        # "O" lines
        #
        no = 0
        for key in Obj.keys():
                k = 0
                if Obj[key].sense == maximize:
                        k = 1
                for cndx in Obj[key]._Onz:
                  print >>OUTPUT, "O" + str(no) + " "+str(k)+"\t#" + str(key) + "[" + str(cndx) + "]"
                  no += 1
                  LT = Obj[key]._linterm[cndx]
                  if "0" in LT:
                        print >>OUTPUT, "n" + str(LT["0"][0])
                  else:
                        print >>OUTPUT, "n0"
        #
        # "r" lines
        #
        print >>OUTPUT, "r"
        nc=0
        for key in Cnontriv:
                C = Con[key]
                for cndx in C._Cnz:
                  if '0' in Con[key]._linterm[cndx]:
                        offset=Con[key]._linterm[cndx]['0'][0]
                  else:
                        offset=0
                  if C[cndx]._equality:
                           print >>OUTPUT, "4", self._get_bound(C[cndx].lower)-offset,
                  else:
                           if C[cndx].lower is None:
                                    if C[cndx].upper is None:
                                             print >>OUTPUT,"3",
                                    else:
                                             print >>OUTPUT,"1", self._get_bound(C[cndx].upper)-offset,
                           else:
                                    if C[cndx].upper is None:
                                             print >>OUTPUT,"2", self._get_bound(C[cndx].lower)-offset,
                                    else:
                                             print >>OUTPUT,"0",\
                                                      self._get_bound(C[cndx].lower)-offset,\
                                                      self._get_bound(C[cndx].upper)-offset,
                  print >>OUTPUT, " # c"+ str(nc)+"  "+str(key) + "[" + str(cndx) + "]"
                  symbol_map["c" + str(nc)] = str(key) + "[" + str(cndx) + "]"
                  nc += 1
        #
        # "b" lines
        #
        print >>OUTPUT, "b"
        nv=0
        for i in xrange(len(Vlist)):
                vi = Vlist[i]
                var = vi[0]
                ndx = vi[1]
                if isinstance(var.domain, BooleanSet):
                        print >>OUTPUT, "0 0 1",
                        print >>OUTPUT, " # v"+str(nv)+"  "+str(var)+"["+str(ndx)+"]"
                        nv += 1
                        continue
                vv = var._varval[ndx]
                L = vv.lb()
                U = vv.ub()
                if L is not None:
                  Lv = str(value(L))
                  if U is not None:
                           Uv = str(value(U))
                           if Lv == Uv:
                                    print >>OUTPUT, "4" , Lv,
                           else:
                                    print >>OUTPUT, "0", Lv, Uv,
                  else:
                           print >>OUTPUT, "2", Lv,
                elif U is not None:
                  print >>OUTPUT, "1", str(value(U)),
                else:
                  print >>OUTPUT, "3",
                if ndx is not None:
                   print >>OUTPUT, " # v"+str(nv)+"  "+str(var)+"["+str(ndx)+"]"
                   symbol_map["v"+str(nv)] = (str(var)+"["+str(ndx)+"]")                   
                else:
                   print >>OUTPUT, " # v"+str(nv)+"  "+str(var)
                   symbol_map["v"+str(nv)] = str(var)

                nv += 1
        #
        # "k" lines
        #
        n1 = model.statistics.number_of_variables - 1
        print >>OUTPUT, "k" + str(n1)
        ktot = 0
        for i in xrange(n1):
                ktot += cu[i]
                print >>OUTPUT, ktot
        #
        # "J" lines
        #
        nc = 0
        for key in Cnontriv:
                C = Con[key]
                for cndx in C._Cnz:
                  LT = C._linterm[cndx]
                  LT_len = len(LT) - ('0' in LT)
                  print >>OUTPUT, "J" + str(nc), LT_len
                  nc += 1
                  for x in LT:
                           if x != '0':
                              p = LT[x]
                              print >>OUTPUT, p[1].id, p[0]
        #
        # "G" lines
        #
        no = 0
        for key in Obj:
                OLT = Obj[key]._linterm
                Ng = 0
                for j in OLT:
                        Ng += len(OLT[j])
                print >>OUTPUT, "G" + str(no), Ng
                no += 1
                for j in OLT:
                        LT = OLT[j]
                        for x in LT:
                                if x != '0':
                                   p = LT[x]
                                   print >>OUTPUT, p[1].id, p[0]

        return symbol_map

problem.WriterRegistration(str(ProblemFormat.nl), ProblemWriter_nl)

