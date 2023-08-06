
import os.path
import re
from TableData import TableData
from coopr.pyomo.base.plugin import DataManagerRegistration


class TextTable(TableData):

    def __init__(self):
        TableData.__init__(self)

    def open(self):
        if self.filename is None:
            raise IOError, "No filename specified"
        if not os.path.exists(self.filename):
            raise IOError, "Cannot find file '%s'" % self.filename
        self.INPUT = open(self.filename, 'r')

    def close(self):
        self.INPUT.close()
        
    def read(self):
        tmp=[]
        for line in self.INPUT:
            line=line.strip()
            tokens = re.split("[\t ]+",line)
            if tokens != ['']:
                tmp.append(tokens)
        if len(tmp) == 0:
            raise IOError, "Empty *.tab file"
        elif len(tmp) == 1:
            self._info = ["param",self.options.param,":=",tmp[0][0]]
        else:
            self._set_data(tmp[0], tmp[1:])
        return True



DataManagerRegistration("tab", TextTable, "Manage IO with ASCI tables.")

