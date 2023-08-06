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
# TODO:  Do we need to have different Expression objects for different
#        intrinsic expressions?
# TODO:  If an expression has a fixed value, should we simply call the
#        intrinsic function with the value of that expression?
# TODO:  Do we need to register these expression objects?
#

__all__ = ['log']

import component
import expr
import numvalue
import math


class _IntrinsicFuncExpression(expr.Expression):
    """
    An expression class that is used for all intrinsic expressions.
    """

    def __init__(self, args=(), name=None, operation=None):
        expr.Expression.__init__(self, args=args, nargs=len(args), name=name, operation=operation, tuple_op=True)


def expr_args(*args):
    """
    Return False if one of the arguments is not an expression or numeric
    value.
    """
    for arg in args:
        if not (isinstance(arg,expr.Expression) or isinstance(arg,numvalue.NumericValue) or isinstance(arg,component.Component)):
            return False
    return True
        


def log(*args):
    if len(args) != 1:
       raise "TypeError: log() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        return _IntrinsicFuncExpression(args=args, name='log', operation=math.log)
    return math.log(*args)

