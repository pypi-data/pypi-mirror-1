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

    def _print_model_NL(self, model, OUTPUT, verbose=False):

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
        Var = {}   # Dictionary of all variables used in all expressions in this model
        #
        # Count number of objectives
        #
        for obj in Obj:
            if Obj[obj].trivial:
                continue
            for i in Obj[obj]:
                if not is_constant(Obj[obj][i].repn):
                    # Merge variables from this expression
                    Var.update( Obj[obj][i].repn[-1] )
                    no += 1
        #
        # Count number of constraints
        #
        for con in Con:
            C = Con[con]
            if C.trivial:
                continue
            for i in C:
                if is_constant(C[i].repn):
                    continue
                # Merge variables from this expression
                Var.update( C[i].repn[-1] )
                nc += 1
                if C[i].lower is not None:
                    L = self._get_bound(C[i].lower) if C[i].lower is not None else -inf
                    U = self._get_bound(C[i].upper) if C[i].upper is not None else inf
                    if (L == U):
                        neqn += 1
                elif L > U:
                    raise ValueError, "Constraint " + str(con) +\
                                             "[" + str(i) + "]: lower bound = " + str(L) +\
                                             " > upper bound = " + str(U)
                elif C[i].lower is not None and C[i].upper is not None:
                    nrange += 1
        #
        niv = nbv = 0
        Ilist = []
        Blist = []
        Vlist = []
        keys = Var.keys()
        keys.sort()
        for ndx in keys:
            var = Var[ndx].var
            if isinstance(var.domain, IntegerSet):
                Ilist.append(ndx)
            elif isinstance(var.domain, BooleanSet):
                L = Var[ndx].lb
                U = Var[ndx].ub
                if L is not None and value(L) == 0 \
                    and U is not None and value(U) == 1:
                    Blist.append(ndx)
                else:
                    Ilist.append(ndx)
            else:
                Vlist.append(ndx)
        for ndx in Blist:
            nbv += 1
            Vlist.append(ndx)
        for ndxx in Ilist:
            niv += 1
            Vlist.append(ndx)
        #
        vctr=0
        var_id = {}
        for ndx in Vlist:
            var_id[ndx] = vctr
            vctr += 1
        #
        # Print Header
        #
        # LINE 1
        #
        print >>OUTPUT,"g3 1 1 0\t# problem",model.name
        #
        # LINE 2
        #
        print >>OUTPUT, " ",len(Var), nc, no, nrange, str(neqn) +\
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
        print >>OUTPUT, " " + str(nbv), niv, 0, 0,\
                "0\t# discrete variables: binary, integer, nonlinear (b,c,o)"
        #
        # LINE 8
        #
        nsno = len(Var)
        ngc = ngo = 0
        # Compute # of nonzeros in gradient
        for key in Obj:
            if Obj[key].trivial:
                continue
            for ondx in Obj[key]:
                ngo += len(Obj[key][ondx].repn.get(1,{}))
        # Compute # of nonzeros in Jacobian
        cu = {}
        for i in xrange(nsno):
            cu[i] = 0
        for key in Con:
            C = Con[key]
            if C.trivial:
                continue
            for cndx in C:
                for d in C[cndx].repn.get(1,{}):
                    ngc += 1
                    cu[var_id[d.keys()[0]]] += 1
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
        for key in Con:
            if Con[key].trivial:
                continue
            for ndx in Con[key]:
                if is_constant(Con[key][ndx].repn):
                    continue
                print >>OUTPUT, "C" + str(nc) + "\t#" + str(key) + "[" + str(ndx) + "]"
                nc += 1
                print >>OUTPUT, "n0"
        #
        # "O" lines
        #
        no = 0
        for key in Obj:
            k = 0
            if Obj[key].sense == maximize:
                k = 1
            for ndx in Obj[key]:
                if is_constant(Obj[key][ndx].repn):
                    continue
                print >>OUTPUT, "O" + str(no) + " "+str(k)+"\t#" + str(key) + "[" + str(ndx) + "]"
                no += 1
                if 0 in Obj[key][ndx].repn:
                    print >>OUTPUT, "n" + str(Obj[key][ndx].repn[0][None])
                else:
                    print >>OUTPUT, "n0"
        #
        # "r" lines
        #
        print >>OUTPUT, "r"
        nc=0
        for key in Con:
            if Con[key].trivial:
                continue
            C = Con[key]
            for ndx in C:
                if is_constant(C[ndx].repn):
                    continue
                if 0 in C[ndx].repn:
                    offset=C[ndx].repn[0][None]
                else:
                    offset=0
                if C[ndx]._equality:
                    print >>OUTPUT, "4", self._get_bound(C[ndx].lower)-offset,
                else:
                    if C[ndx].lower is None:
                        if C[ndx].upper is None:
                            print >>OUTPUT,"3",
                        else:
                            print >>OUTPUT,"1", self._get_bound(C[ndx].upper)-offset,
                    else:
                        if C[ndx].upper is None:
                            print >>OUTPUT,"2", self._get_bound(C[ndx].lower)-offset,
                        else:
                            print >>OUTPUT,"0",\
                                    self._get_bound(C[ndx].lower)-offset,\
                                    self._get_bound(C[ndx].upper)-offset,
                print >>OUTPUT, " # c"+ str(nc)+"  "+C[ndx].label #str(key) + "[" + str(ndx) + "]"
                symbol_map["c" + str(nc)] = C[ndx].label #str(key) + "[" + str(ndx) + "]"
                nc += 1
        #
        # "b" lines
        #
        print >>OUTPUT, "b"
        for ndx in Vlist:
            vv = Var[ndx]
            #vi = Vlist[i]
            var = vv.var
            #ndx = vi[1]
            if isinstance(var.domain, BooleanSet):
                print >>OUTPUT, "0 0 1",
                print >>OUTPUT, " # v"+str(var_id[ndx])+"  "+vv.label
                symbol_map["v"+str(var_id[ndx])] = vv.label
                continue
            L = vv.lb
            U = vv.ub
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
            print >>OUTPUT, " # v"+str(var_id[ndx])+"  "+vv.label
            symbol_map["v"+str(var_id[ndx])] = vv.label
        #
        # "k" lines
        #
        n1 = len(Var) - 1
        print >>OUTPUT, "k" + str(n1)
        ktot = 0
        for i in xrange(n1):
                ktot += cu[i]
                print >>OUTPUT, ktot
        #
        # "J" lines
        #
        nc = 0
        for key in Con:
            if Con[key].trivial:
                continue
            con = Con[key]
            for ndx in con:
                if is_constant(con[ndx].repn):
                    continue
                linear = con[ndx].repn.get(1,{})
                print >>OUTPUT, "J" + str(nc), len(linear)
                nc += 1

                for d in linear:
                    for id in d:
                        print >>OUTPUT, var_id[id], linear[d]
        #
        # "G" lines
        #
        no = 0
        for key in Obj:
            if Obj[key].trivial:
                continue
            obj = Obj[key]
            for ndx in obj:
                linear = obj[ndx].repn.get(1,{})
                print >>OUTPUT, "G" + str(no), len(linear)
                no += 1
                for d in linear:
                    for id in d:
                        print >>OUTPUT, var_id[id], linear[d]

        return symbol_map

problem.WriterRegistration(str(ProblemFormat.nl), ProblemWriter_nl)

