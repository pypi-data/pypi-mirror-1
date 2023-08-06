#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

#
# Note: this leaves the trivial constraints in the model
#

import pyutilib.component.core
from coopr.pyomo.base import Constraint, Objective
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction
import coopr.pyomo.expr 


class ComputeCanonicalRepn(pyutilib.component.core.SingletonPlugin):
    """
    This plugin computes the canonical representation for 
    all objectives and constraints
    linear terms.
    """

    pyutilib.component.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "compute_canonical_repn"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 10000

    def presolve(self, model):
        """
        The main routine to perform the presolve
        """
        #
        # Objectives
        #
        Obj = model.active_components(Objective)
        for key in Obj.keys():
            obj = Obj[key]
            # number of objective indicies with non-trivial expressions
            nt = 0
            for ondx in obj:
                if not obj._data[ondx].active:
                    continue
                if obj._data[ondx].expr is None:
                    raise ValueError, "No expression has been defined for objective %s" % str(key)
                try:
                    obj._data[ondx].repn = coopr.pyomo.expr.generate_canonical_repn(obj._data[ondx].expr)
                except Exception, e:
                    print "Error generating a canonical representation for objective %s (index %s)" % (str(key), str(ondx))
                    raise e
                if not coopr.pyomo.expr.is_constant(obj._data[ondx].repn):
                    nt += 1
            if nt == 0:
                obj.trivial = True
        #
        # Constraints
        #
        Con = model.active_components(Constraint)
        for key in Con.keys():
            con = Con[key]
            # number of constraint indicies with non-trivial bodies
            nt = 0 
            for cndx in con:
                if not con._data[cndx].active:
                    continue
                if con._data[cndx].body is None:
                    raise ValueError, "No expression has been defined for the body of constraint %s" % str(key)
                try:                 
                    con._data[cndx].repn = coopr.pyomo.expr.generate_canonical_repn(con._data[cndx].body)
                except Exception, e:
                    print "Error generating a canonical representation for constraint %s (index %s)" % (str(key), str(cndx))
                    raise e
                if not coopr.pyomo.expr.is_constant(con._data[cndx].repn):
                    nt += 1
            if nt == 0:
                con.trivial = True
        #
        # Return modified instance
        #
        return model

