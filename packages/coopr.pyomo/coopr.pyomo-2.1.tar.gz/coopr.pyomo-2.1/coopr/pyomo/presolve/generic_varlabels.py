#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction, Var, Constraint
import pyutilib.plugin.core

ignore = set(['"', "'", '`'])
remap = {}
# Remap as underscores
remap['-']='_'
remap['_']='_'
remap[' ']='_'
remap['(']='['
remap['{']='['
remap[')']=']'
remap['}']=']'
# Remap as Q+ASCII-Dec
remap['!']='_Q33_'
remap['#']='_Q35_'
remap['$']='_Q36_'
remap['%']='_Q37_'
remap['&']='_Q38_'
remap['*']='_Q42_'
remap['+']='_Q43_'
#remap[',']='_Q44_'
remap['.']='_Q46_'
remap['/']='_Q47_'
remap[';']='_Q59_'
remap['<']='_Q60_'
remap['=']='_Q61_'
remap['>']='_Q62_'
remap['?']='_Q63_'
remap['@']='_Q63_'
remap['\\']='_Q92_'
remap['^']='_Q94_'
remap['|']='_Q124_'
remap['~']='_Q126_'

class GenericVarLabelsPresolver(pyutilib.plugin.core.SingletonPlugin):
    """
    This plugin changes variables names to generate a label that
    can be used in LP/MILP file formats.
    """

    pyutilib.plugin.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "generic_varlabels"
        pyutilib.plugin.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 1000

    def _name_fix(self, name):
        global ignore
        global remap
        tmp=""
        for c in name:
            if c in remap:
                tmp += remap[c]
            elif not c in ignore:
                tmp += c
        return tmp

    def presolve(self,model):
        """
        The main routine to perform the presolve
        """
        #
        # This creates labels for all variables, not just the ones used
        # in this instance.  This is useful when interrogating unused 
        # variables.
        #
        Vars = model.active_components(Var)
        for var in Vars.values():
            for V in var._varval.keys():
                var._varval[V].label = self._name_fix( var._varval[V].name )
                model._name_varmap[ var._varval[V].label ] = var._varval[V]
        Cons = model.active_components(Constraint)
        for con in Cons.values():
            for C in con._data:
                con._data[C].label = self._name_fix( con._data[C].name )
                model._name_conmap[ con._data[C].label ] = con._data[C]
        return model
            
