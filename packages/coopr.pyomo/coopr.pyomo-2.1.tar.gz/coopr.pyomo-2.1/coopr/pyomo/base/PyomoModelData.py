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
import os
from pyutilib.misc import quote_split
import pyomo
from pyutilib.excel import ExcelSpreadsheet
import coopr


class ModelData(object):
    """
    An object that manages data for a model.
    This object contains the interface routines for importing and
    exporting data from external data sources.
    """

    def __init__(self,model=None,filename=None):
        """
        Constructor
        """
        self._info=[]
        #self._info_dict={}
        self._data={}
        self._default={}
        self._model=model
        self._table={}
        if filename is not None:
           self.import_data_file(filename)


    #def add_data_file(self,filename, name=None):
        #if name is not None:
        #   self._info_dict[name] = len(self._info)
    def add_data_file(self,filename):
        self._info.append(filename)


    def add_table(self, filename, range=None, **kwds):
        """
        Add an Excel table
        """
        #if "name" in kwds:
        #   if name is not None:
        #      self._info_dict[kwds["name"]] = len(self._info)
        if filename not in self._table.keys():
           kwds["filename"]=filename
           self._table[filename] = TableData(**kwds)
        self._info.append((filename,range,kwds))


    def read(self,model=None):
        """ 
        Read data
        """
        if model is not None:
           self._model=model
        if self._model is None:
           raise ValueError, "Cannot read model data without a model"
        #
        # Open all tables
        #
        for key in self._table.keys():
          self._table[key].open()
        #
        # For every information item, import the data or table
        #
        for item in self._info:
          if type(item) is str:
             if pyomo.debug("verbose"):         #pragma:nocover
                print "Importing data from file "+item,
             status = self.import_data_file(item)
             if pyomo.debug("verbose"):         #pragma:nocover
                print "... done."
          else:        
             if pyomo.debug("verbose"):         #pragma:nocover
                print "Importing data from table "+item[0],
                if item[1] is not None:
                   print "at range "+item[1],
             try:
                status = self.import_table(self._table[item[0]], item[1], item[2])
             except IOError, err:
                raise IOError, "Problem importing data from table "+item[0]+": "+str(err)
             except AttributeError, err:
                raise IOError, "Problem importing data from table "+item[0]+": "+str(err)
             if pyomo.debug("verbose"):         #pragma:nocover
                print "... done."
          if not status:
             print "Warning: status is "+str(status)+" after processing "+str(item)
        #
        # Close all tables
        #
        for key in self._table.keys():
          self._table[key].close()


    def import_table(self, table, range, keywords):
        """
        Import a table
        """
        table.read(range, keywords)
        tmp = table.data()
        if pyomo.debug("reader"):               #pragma:nocover
           print "import_table - data: "+str(tmp)
        status = self._process_data(tmp)
        table.clear()
        return status


    def import_data_file(self, filename):
        """
        Create a table of tuples to values, based on data from a file.
        We assume that this data is defined in a format that is
        compatible with AMPL.
        """
        global Filename
        Filename = filename
        global Lineno
        Lineno = 0
        INPUT = open(filename,"r")
        cmd=""
        status=True
        for line in INPUT:
          Lineno += 1
          line = re.sub(":"," :",line)
          line = line.strip()
          if line == "" or line[0] == '#':
             continue
          cmd = cmd + " " + line
          if ';' in cmd:
             #
             # We assume that a ';' indicates an end-of-command declaration.
             # However, the user might have put multiple commands on a single
             # line, so we need to split the line based on these values.
             # BUT, at the end of the line we should see an 'empty' command,
             # which we ignore.
             #
             for item in cmd.split(';'):
               item = item.strip()
               if item != "":
                  status = self._process_data(quote_split("[\t ]+",item))
               if not status:
                  break
             cmd = ""
          if not status:
                 break
        if cmd != "":
           raise IOError, "ERROR: There was unprocessed text at the end of the data file!: \"" + cmd + "\""
        return status


    def _preprocess_data(self,cmd):
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


    def _process_data(self,cmd):
        """
        Called by import_file() to (1) preprocess data and (2) call
        subroutines to process different types of data
        """
        global Lineno
        global Filename
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _process_data (start)",cmd
        if len(cmd) == 0:                       #pragma:nocover
           raise ValueError, "ERROR: Empty list passed to Model::_process_data"
        cmd = self._preprocess_data(cmd)
        if cmd[0] == "data":
           return True
        if cmd[0] == "end":
           return False
        if cmd[0][0:3] == "set":
           self._process_set(cmd)
        elif cmd[0][0:5] == "param":
           self._process_param(cmd)
        else:
           raise IOError, "ERROR: Trouble on line "+str(Lineno)+" of file "+Filename+": Unknown data command: "+" ".join(cmd)
        return True


    def _process_set(self,cmd):
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
           ndx=tuple(self._data_eval(ndx.split(",")))
           if tokens[0] not in self._data:
              self._data[tokens[0]] = {}
           self._data[tokens[0]][ndx] = self._process_set_data(cmd[3:],tokens[0])
        elif cmd[2] == ":":
           self._data[cmd[1]] = {}
           self._data[cmd[1]][None] = []
           i=3
           while cmd[i] != ":=":
              i += 1
           ndx1 = cmd[3:i]
           i += 1
           while i<len(cmd):
              ndx=cmd[i]
              for j in range(0,len(ndx1)):
                if cmd[i+j+1] == "+":
                   self._data[cmd[1]][None] += self._process_set_data(["("+str(ndx1[j])+","+str(cmd[i])+")"],cmd[1])
              i += len(ndx1)+1
        else:
           self._data[cmd[1]] = {}
           self._data[cmd[1]][None] = self._process_set_data(cmd[3:], cmd[1])


    def _process_set_data(self,cmd,sname):
        """
        Called by _process_set() to process set data.
        """
        if pyomo.debug("reader"):               #pragma:nocover
           print "DEBUG: _process_set_data(start)",cmd
        if len(cmd) == 0:
           return []
        sd = getattr(self._model,sname)
        #d = sd.dimen
        cmd = self._data_eval(cmd)
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
               tmpval[ndx] = self._data_eval([cmd[i]])[0]
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


    def _process_param(self,cmd):
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
        #print "HERE",cmd
        #
        # WEH - this is apparently not used
        #
        #if cmd[0] == "default":
        #   dflt = self._data_eval(cmd[1])[0]
        #   cmd = cmd[2:]
        if cmd[0] == ":":
           singledef = False
           cmd = cmd[1:]
        if singledef:
           pname = cmd[0]
           cmd = cmd[1:]
           if len(cmd) >= 2 and cmd[0] == "default":
              dflt = self._data_eval(cmd[1])[0]
              cmd = cmd[2:]
           if dflt != None:
              self._default[pname] = dflt
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
                 if pname not in self._data:
                    self._data[pname] = {}
                 finaldata = self._process_data_list(getattr(self._model,pname).dim(), self._data_eval(cmd))
                 for key in finaldata:
                    self._data[pname][key]=finaldata[key]
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
                 self._process_param(tmp)
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
                self._process_param(tmp)

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
             d = getattr(self._model,sname).dimen
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
             self._process_set(tmp)
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
             d = getattr(self._model,pname).dim()
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
             self._process_param(tmp)
             j += 1


    def _process_data_list(self,dim,cmd):
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


    def _data_eval(self, values):
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
               tmp=self._data_eval([item])
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



class TableData(object):
    """
    An object that imports data from a table in an external data source.
    The initialization of this object depends on the format specified by the 
    file:
 
                *.tab       Simple ASCII table
                *.xls       Excel spreadsheet
                *.mdb       MSAccess database

    NOTE: it probably makes sense to migrate the table handlers to
    external classes, and to enable registration of table handlers. 
    But for ValueErrornow, this is convenient.
    """

    def __init__(self,*args,**kwds):
        """
        Constructor
        """
        self._info=None
        #
        self._reinitialize(kwds)


    def _reinitialize(self,kwds):
        if kwds is None:
           return
        self._data=None
        self._filename=None
        self._range=None
        self._format=None
        self._set=None
        self._param=None
        self._index=None
        for key in kwds:
          if key not in ["set","format","index","param","data","filename","range"]:
             raise ValueError, "Unknown keyword '"+key+"' when initializing TableData object"
          setattr(self,"_"+key,kwds[key])

    def open(self,filename=None):
        """
        Open the table
        """
        if filename is not None:
           self._filename=filename
        if self._filename is None:
           raise IOError, "No filename specified"
        if not os.path.exists(self._filename):
           raise IOError, "Cannot find file: \""+self._filename+"\""
        tmp = self._filename.split(".")
        if len(tmp) == 1:
           raise IOError, "Unknown file type: \""+self._filename+"\""
        self._type=tmp[-1]
        if self._type == "tab":
           self._open_tab()
        elif self._type == "xls":
           self._open_xls()
        elif self._type == "mdb":       #pragma:nocover
           self._open_mdb()
        else:
           raise IOError, "Unknown file type: \""+self._filename+"\""


    def read(self,range=None, keywords=None):
        """
        Read data from the table
        """
        self._reinitialize(keywords)
        if range is not None:
           self._range=range
        if self._type == "tab":
           self._read_tab()
        elif self._type == "xls":
           self._read_xls()
        elif self._type == "mdb":       #pragma:nocover
           self._read_mdb()


    def close(self):
        """
        Close the table
        """
        if self._type == "tab":
           self._close_tab()
        elif self._type == "xls":
           self._close_xls()
        elif self._type == "mdb":
           self._close_mdb()            #pragma:nocover


    def _open_tab(self):
        self.INPUT = open(self._filename,"r")

    def _read_tab(self):
        tmp=[]
        for line in self.INPUT.readlines():
          line=line.strip()
          tokens = re.split("[\t ]+",line)
          if tokens != ['']:
             tmp.append(tokens)
        if len(tmp) == 0:
           raise IOError, "Empty *.tab file"
        elif len(tmp) == 1:
           self._info = ["param",self._param,":=",tmp[0][0]]
        else:
           self._set_data(tmp[0], tmp[1:])

    def _close_tab(self):
        self.INPUT.close()
        

    def _open_xls(self):
        self.sheet = None
        if self._data is not None:
           self.sheet = self._data
        else:
           try:
              self.sheet = ExcelSpreadsheet(self._filename)
           except pyutilib.ApplicationError:
              raise

    def _read_xls(self):
        if self.sheet is None:
           return
        tmp = self.sheet.get_range(self._range, raw=True)
        if type(tmp) in (int,long,float):
           self._info = ["param",self._param,":=",tmp]
        else:
           self._set_data(tmp[0], tmp[1:])

    def _close_xls(self):
        if self._data is None and not self.sheet is None:
           del self.sheet


    def _open_mdb(self):
        pass                #pragma:nocover

    def _read_mdb(self):
        pass                #pragma:nocover

    def _close_mdb(self):
        pass                #pragma:nocover


    def data(self):
        return self._info


    def clear(self):
        self._info = None


    def _set_data(self, headers, rows):
        if self._set is not None:
           if self._format is None:
              self._info = ["set",self._set,":="]
              for row in rows:
                self._info = self._info + list(row)
           elif self._format is "array":
              self._info = ["set",self._set, ":"]
              self._info = self._info + list(headers[1:])
              self._info = self._info + [":="]
              for row in rows:
                self._info = self._info + list(row)
           else:
              raise ValueError, "Unknown set format: "+self._format

        elif self._index is not None and self._param is None:
           self._info = ["param",":",self._index,":"]
           self._info = self._info + map(str,list(headers[1:]))
           self._info.append(":=")
           for row in rows:
             self._info = self._info + list(row)

        elif self._index is not None and self._param is not None:
           self._info = ["param",":",self._index,":"]
           if type(self._param) is str:
              self._info = self._info + [self._param]
           elif type(self._param) is tuple:
              self._info = self._info + list(self._param)
           else:
              self._info = self._info + self._param
           self._info.append(":=")
           for row in rows:
             self._info = self._info + list(row)

        elif self._param is not None and self._format is not None:
           if self._format is "transposed_array":
              self._info = ["param",self._param,"(tr)",":"] + map(str,list(headers[1:]))
           elif self._format is "array":
              self._info = ["param",self._param,":"] + map(str,list(headers[1:]))
           else:
              raise ValueError, "Unknown parameter format: "+self._format
           self._info.append(":=")
           for row in rows:
             self._info = self._info + list(row)

        else:
           if len(headers) == 1:
              self._info = ["set",headers[0],":="]
              for row in rows:
                self._info = self._info + list(row)
           else:
              self._info = ["param",":"]
              if self._param is None:
                 self._info = self._info + map(str,list(headers[1:]))
              elif type(self._param) is str:
                 self._info = self._info + [self._param]
              else:
                 self._info = self._info + list(self._param)
              self._info.append(":=")
              for row in rows:
                self._info = self._info + list(row)

