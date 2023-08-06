#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['IPyomoExpression', 'ExpressionRegistration', 'ExpressionFactory',
        'IPyomoSet', 'IModelComponent', 'ComponentRegistration',
        'ComponentFactory',
        'IPyomoPresolver', 'IPyomoPresolveAction',
        'IModelTransformation',
        'apply_transformation']

from pyutilib.plugin.core import *


class IPyomoPresolver(Interface):

    def get_actions(self):
        """Return a list of presolve actions, in the order in which 
        they will be applied."""
    
    def activate_action(self, action):
        """Activate an action, but leave its default rank"""

    def deactivate_action(self, action):
        """Deactivate an action"""

    def set_actions(self, actions):
        """Set presolve action list"""

    def presolve(self, instance):
        """Apply the presolve actions to this instance, and return the 
        revised instance"""


class IPyomoPresolveAction(Interface):

    def presolve(self, instance):
        """Apply the presolve action to this instance, and return the 
        revised instance"""

    def rank(self):
        """Return an integer that is used to automatically order presolve actions,
        from low to high rank."""


class IPyomoExpression(Interface):

    def type(self):
        """Return the type of expression"""

    def create(self, args):
        """Create an instance of this expression type"""


class ExpressionRegistration(Plugin):

    implements(IPyomoExpression)

    def __init__(self, type, cls):
        Plugin.__init__(self, name=type)
        self._type = type
        self._cls = cls

    def type(self):
        return self._type

    def create(self, args):
        return self._cls(args)


def ExpressionFactory(name=None, args=[]):
    ep = ExpressionFactory.ep
    if name is None:
        return map(lambda x:x.name, ep())
    return ep.service(name).create(args)
ExpressionFactory.ep = ExtensionPoint(IPyomoExpression)




class IPyomoSet(Interface):
    pass



class IModelComponent(Interface):

    def type(self):
        """Return the type of component"""

    def cls(self):
        """Return the class type of this component"""

    def create(self):
        """Create an instance of this component type"""


class ComponentRegistration(Plugin):

    implements(IModelComponent)

    def __init__(self, type, cls, doc=""):
        Plugin.__init__(self, name=type)
        self._type = type
        self._cls = cls
        self.doc=doc

    def type(self):
        return self._type

    def cls(self):
        return self._cls

    def create(self):
        return self._cls()


def ComponentFactory(name=None, args=[]):
    ep = ExtensionPoint(IModelComponent)
    if name is None:
        return map(lambda x:x.name, ep())
    return ep.service(name).create(*args)



class IModelTransformation(Interface):

    def apply(self, model, **kwds):
        """Apply a model transformation and return a new model instance"""

    def __call__(self, model, **kwds):
        """Use this plugin instance as a functor to apply a transformation"""
        return self.apply(model, **kwds)


def apply_transformation(*args, **kwds):
    ep = ExtensionPoint(IModelTransformation)
    if len(args) is 0:
        return map(lambda x:x.name, ep())
    service = ep.service(args[0])
    if len(args) == 1 or service is None:
        return service
    tmp=(args[1],)
    return service.apply(*tmp, **kwds)
    
