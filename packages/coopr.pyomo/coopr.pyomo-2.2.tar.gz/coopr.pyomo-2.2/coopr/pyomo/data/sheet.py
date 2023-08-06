
import os.path
from TableData import TableData
from pyutilib.excel import ExcelSpreadsheet
from coopr.pyomo.base.plugin import DataManagerRegistration

class SheetTable(TableData):

    def __init__(self):
        TableData.__init__(self)

    def open(self):
        if self.filename is None:
            raise IOError, "No filename specified"
        if not os.path.exists(self.filename):
            raise IOError, "Cannot find file '%s'" % self.filename
        self.sheet = None
        if self._data is not None:
            self.sheet = self._data
        else:
            try:
                self.sheet = ExcelSpreadsheet(self.filename)
            except pyutilib.ApplicationError:
                raise

    def read(self):
        if self.sheet is None:
            return
        tmp = self.sheet.get_range(self.options.range, raw=True)
        if type(tmp) in (int,long,float):
            self._info = ["param",self.options.param,":=",tmp]
        else:
            self._set_data(tmp[0], tmp[1:])
        return True

    def close(self):
        if self._data is None and not self.sheet is None:
            del self.sheet


DataManagerRegistration("xls", SheetTable, "Manage IO with Excel XLS files.")

