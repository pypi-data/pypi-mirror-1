#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import re
import copy
import math
from coopr.pyomo.base.plugin import *
from coopr.pyomo.base import pyomo


def _preprocess_data(cmd):
        """
        Called by _process_data() to (1) combine tokens that comprise a tuple
        and (2) combine the ':' token with the previous token
        """
        if pyomo.debug("reader"):               #pragma:nocover
           print "_preprocess_data(start)",cmd
        status=")"
        newcmd=[]
        for token in cmd:
          if type(token) in (str,unicode):
             token=str(token)
             if "(" in token and ")" in token:
                newcmd.append(token)
                status=")"
             elif "(" in token:
                if status == "(":
                   raise ValueError, "Two '('s follow each other in data "+token
                status="("
                newcmd.append(token)
             elif ")" in token:
                if status == ")":
                   raise ValueError, "Two ')'s follow each other in data"
                status=")"
                newcmd[-1] = newcmd[-1]+token
             elif status == "(":
                newcmd[-1] = newcmd[-1]+token
             else:
                newcmd.append(token)
          else:
             if type(token) is float and math.floor(token) == token:
                token=int(token)
             newcmd.append(token)
        if pyomo.debug("reader"):               #pragma:nocover
           print "_preprocess_data(end)",newcmd
        return newcmd


def _process_set(cmd, _model, _data):
        """
        Called by _process_data() to process a set declaration.
        """
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _process_set(start)",cmd
        #
        # Process a set
        #
        if "[" in cmd[1]:
           tokens = re.split("[\[\]]",cmd[1])
           ndx=tokens[1]
           ndx=tuple(_data_eval(ndx.split(",")))
           if tokens[0] not in _data:
              _data[tokens[0]] = {}
           _data[tokens[0]][ndx] = _process_set_data(cmd[3:], tokens[0], _model)
        elif cmd[2] == ":":
           _data[cmd[1]] = {}
           _data[cmd[1]][None] = []
           i=3
           while cmd[i] != ":=":
              i += 1
           ndx1 = cmd[3:i]
           i += 1
           while i<len(cmd):
              ndx=cmd[i]
              for j in range(0,len(ndx1)):
                if cmd[i+j+1] == "+":
                   _data[cmd[1]][None] += _process_set_data(["("+str(ndx1[j])+","+str(cmd[i])+")"], cmd[1], _model)
              i += len(ndx1)+1
        else:
           _data[cmd[1]] = {}
           _data[cmd[1]][None] = _process_set_data(cmd[3:], cmd[1], _model)


def _process_set_data(cmd, sname, _model):
        """
        Called by _process_set() to process set data.
        """
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _process_set_data(start)",cmd
        if len(cmd) == 0:
           return []
        sd = getattr(_model,sname)
        #d = sd.dimen
        cmd = _data_eval(cmd)
        ans=[]
        i=0
        flag=type(cmd[0]) is tuple
        tmp=None
        ndx=None
        while i<len(cmd):
          if type(cmd[i]) is not tuple:
            if flag:
               #if type(cmd[i]) is not tuple:
               #   raise ValueError, "Problem initializing set="+sname+" with input data="+str(cmd)+" - first element was interpreted as a tuple, but element="+str(i)+" is of type="+str(type(cmd[i]))+"; types must be consistent"
               tmpval=tmp
               tmpval[ndx] = _data_eval([cmd[i]])[0]
               #
               # WEH - I'm not sure what the next two lines are for
               #        These are called when initializing a set with more than
               #        one dimension
               #if d > 1:
               #   tmpval = util.tuplize(tmpval,d,sname)
               ans.append(tuple(tmpval))
            else:
               ans.append(cmd[i])
          elif "*" not in cmd[i]:
            ans.append(cmd[i])
          else:
            j = i
            tmp=list(cmd[j])
            ndx=tmp.index("*")
          i += 1
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _process_set_data(end)",ans
        return ans


def _process_param(cmd, _model, _data, _default):
        """
        Called by _process_data to process data for a Parameter declaration
        """
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _process_param(start)",cmd
        #
        # Process parameters
        #
        dflt = None
        singledef = True
        cmd = cmd[1:]
        if cmd[0] == ":":
           singledef = False
           cmd = cmd[1:]
        if singledef:
           pname = cmd[0]
           cmd = cmd[1:]
           if len(cmd) >= 2 and cmd[0] == "default":
              dflt = _data_eval(cmd[1])[0]
              cmd = cmd[2:]
           if dflt != None:
              _default[pname] = dflt
           if cmd[0] == ":=":
              cmd = cmd[1:]
           transpose = False
           if cmd[0] == "(tr)":
              transpose = True
              if cmd[1] == ":":
                 cmd = cmd[1:]
              else:
                 cmd[0] = ":"
           if cmd[0] != ":":
              if pyomo.debug("reader"):             #pragma:nocover
                 print "DEBUG: _process_param (singledef without :...:=)",cmd
              if not transpose:
                 if pname not in _data:
                    _data[pname] = {}
                 finaldata = _process_data_list(getattr(_model,pname).dim(), _data_eval(cmd))
                 for key in finaldata:
                    _data[pname][key]=finaldata[key]
              else:
                 tmp = ["param", pname, ":="]
                 i=1
                 while i < len(cmd):
                    i0 = i
                    while cmd[i] != ":=":
                      i=i+1
                    ncol = i - i0 + 1
                    lcmd = i
                    while lcmd < len(cmd) and cmd[lcmd] != ":":
                      lcmd += 1
                    j0 = i0 - 1
                    for j in range(1,ncol):
                      ii = 1 + i
                      kk = ii + j
                      while kk < lcmd:
                        if cmd[kk] != ".":
                        #if 1>0:
                           tmp.append(copy.copy(cmd[j+j0]))
                           tmp.append(copy.copy(cmd[ii]))
                           tmp.append(copy.copy(cmd[kk]))
                        ii = ii + ncol
                        kk = kk + ncol
                    i = lcmd + 1
                 _process_param(tmp, _model, _data, _default)
           else:
              tmp = ["param", pname, ":="]
              i=1
              if pyomo.debug("reader"):             #pragma:nocover
                 print "DEBUG: _process_param (singledef with :...:=)",cmd
              while i < len(cmd):
                i0 = i
                while i<len(cmd) and cmd[i] != ":=":
                  i=i+1
                if i==len(cmd):
                   raise ValueError, "ERROR: Trouble on line "+str(Lineno)+" of file "+Filename
                ncol = i - i0 + 1
                lcmd = i
                while lcmd < len(cmd) and cmd[lcmd] != ":":
                  lcmd += 1
                j0 = i0 - 1
                for j in range(1,ncol):
                  ii = 1 + i
                  kk = ii + j
                  while kk < lcmd:
                    if cmd[kk] != ".":
                        if transpose:
                           tmp.append(copy.copy(cmd[j+j0]))
                           tmp.append(copy.copy(cmd[ii]))
                        else:
                           tmp.append(copy.copy(cmd[ii]))
                           tmp.append(copy.copy(cmd[j+j0]))
                        tmp.append(copy.copy(cmd[kk]))
                    ii = ii + ncol
                    kk = kk + ncol
                i = lcmd + 1
                _process_param(tmp, _model, _data, _default)

        else:
           if pyomo.debug("reader"):                #pragma:nocover
              print "DEBUG: _process_param (cmd[0]=='param:')",cmd
           i=0
           nsets=0
           while i<len(cmd) and cmd[i] != ":=":
             if cmd[i] == ":":
                nsets = i
             i += 1
           if i==len(cmd):
              raise ValueError, "Trouble on data file line "+str(Lineno)+" of file "+Filename
           if pyomo.debug("reader"):                #pragma:nocover
              print "NSets",nsets
           Lcmd = len(cmd)
           j=0
           d = 1
           #
           # Process sets first
           #
           while j<nsets:
             sname = cmd[j]
             d = getattr(_model,sname).dimen
             np = i-1
             if pyomo.debug("reader"):              #pragma:nocover
                print "I,J,SName,d",i,j,sname,d
             dnp = d + np - 1
             #k0 = i + d - 2
             ii = i + j + 1
             tmp = [ "set", cmd[j], ":=" ]
             while ii < Lcmd:
               for dd in range(0,d):
                 tmp.append(copy.copy(cmd[ii+dd]))
               ii += dnp
             _process_set(tmp, _model, _data)
             j += 1
           if nsets > 0:
              j += 1
           #
           # Process parameters second
           #
           while j < i:
             pname = cmd[j]
             if pyomo.debug("reader"):              #pragma:nocover
                print "I,J,Pname",i,j,pname
             #d = 1
             d = getattr(_model,pname).dim()
             if nsets > 0:
                np = i-1
                dnp = d+np-1
                ii = i + 1
                kk = i + d + j-1
             else:
                np = i
                dnp = d + np
                ii = i + 1
                kk = np + 1 + d + nsets + j
             tmp = [ "param", pname, ":=" ]
             if pyomo.debug("reader"):              #pragma:nocover
                print "dnp",dnp
                print "np",np
             while kk < Lcmd:
               if pyomo.debug("reader"):                #pragma:nocover
                  print "kk,ii",kk,ii
               iid = ii + d
               while ii < iid:
                 tmp.append(copy.copy(cmd[ii]))
                 ii += 1
               ii += dnp-d
               tmp.append(copy.copy(cmd[kk]))
               kk += dnp
             _process_param(tmp, _model, _data, _default)
             j += 1


def _process_data_list(dim, cmd):
        """
        Called by _process_param() to process a list of data for a
        Parameter.
        """
        if pyomo.debug("reader"):               #pragma:nocover
           print "process_data_list",dim,cmd
        if len(cmd) % (dim+1) != 0:
           raise ValueError, "Parameter data has "+str(len(cmd))+" values (" + str(cmd) + "), which is incompatible with having "+str(dim)+" dimensions"            
        ans={}
        if dim==0:
           ans[None]=cmd[0]
           return ans
        i=0
        while i<len(cmd):
          ndx = tuple(cmd[i:i+dim])
          ##print i,cmd[i:i+dim],ndx,cmd[i+dim]
          if cmd[i+dim] != ".":
                 ans[ndx] = cmd[i+dim]
          i += dim+1
        return ans


def _data_eval(values):
        """
        Evaluate the list of values to make them bool, integer or float,
        or a tuple value.
        """
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _data_eval(start)",values
        ans = []
        for val in values:
          if type(val) in (bool,int,float,long):
             ans.append(val)
             continue
          if val in ('True','true','TRUE'):
             ans.append(True)
             continue
          if val in ('False','false','FALSE'):
             ans.append(False)
             continue
          tmp = None
          if "(" in val and ")" in val:
             vals = []
             tval = val[1:-1]
             for item in tval.split(","):
               tmp=_data_eval([item])
               vals.append(tmp[0])
             ans.append(tuple(vals))
             continue
          try:
             tmp = int(val)
             ans.append(tmp)
          except ValueError:
             pass
          if tmp is None:
             try:
               tmp = float(val)
               ans.append(tmp)
             except ValueError:
               ans.append(val)
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _data_eval(end)",ans
        return ans


def _process_data(cmd, _model, _data, _default):
        """
        Called by import_file() to (1) preprocess data and (2) call
        subroutines to process different types of data
        """
        #global Lineno
        #global Filename
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _process_data (start)",cmd
        if len(cmd) == 0:                       #pragma:nocover
           raise ValueError, "ERROR: Empty list passed to Model::_process_data"
        cmd = _preprocess_data(cmd)
        if cmd[0] == "data":
           return True
        if cmd[0] == "end":
           return False
        if cmd[0][0:3] == "set":
           _process_set(cmd, _model, _data)
        elif cmd[0][0:5] == "param":
           _process_param(cmd, _model, _data, _default)
        else:
           raise IOError, "ERROR: Unknown data command: "+" ".join(cmd)
        return True


