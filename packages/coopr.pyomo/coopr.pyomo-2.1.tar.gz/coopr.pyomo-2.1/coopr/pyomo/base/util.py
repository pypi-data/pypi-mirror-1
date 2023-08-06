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
# Utility functions
#

import expr

"""
A utility function to compute a generalized dot product.  The following examples illustrate
the use of this function:

summation(x)
Sum the elements of x

summation(x,y)
Sum the product of elements in x and y

summation(x,y, index=z)
Sum the product of elements in x and y, over the index set z

summation(x, denom=a)
Sum the product of x_i/a_i

summation(denom=(a,b))
Sum the product of 1/(a_i*b_i)
"""
def summation(*args, **kwds):
    if 'denom' in kwds:
        denom=kwds['denom']
    else:
        denom=()
    if not type(denom) in [list,tuple]:
        denom=[denom]
    if len(args) == 0 and len(denom) == 0:
        raise ValueError, "The summation() command requires at least on argument or a denominator term"
    if 'index' in kwds:
        index=kwds['index']
    else:  
        if len(args) > 0:
            index=args[-1].keys()
        else:
            index=denom[-1].keys()

    ans = 0
    num_index = range(0,len(args))
    denom_index = range(0,len(denom))
    #
    # Iterate through all indices
    #
    for i in index:
        #
        # Iterate through all arguments
        #
        item = 1
        for j in num_index:
            item *= args[j][i]
        for j in denom_index:
            item /= denom[j][i]
        ans += item
    return ans

def dot_product(*args, **kwds):
    return summation(*args, **kwds)
