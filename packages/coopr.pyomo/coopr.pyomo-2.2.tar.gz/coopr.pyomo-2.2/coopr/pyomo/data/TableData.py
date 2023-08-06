#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['TableData']

from pyutilib.misc import Options
from process_data import _process_data

class TableData(object):
    """
    An object that imports data from a table in an external data source.
    """

    def __init__(self):
        """
        Constructor
        """
        self._info=None
        self._data=None

    def initialize(self, filename, **kwds):
        self.filename = filename
        self.options = Options(**kwds)

    def open(self, filename):
        """
        Open the table
        """
        pass

    def read(self):
        """
        Read data from the table
        """
        pass

    def close(self):
        """
        Close the table
        """
        pass

    def process(self, model, data, default):
        """
        Return the data that was extracted from this table
        """
        return _process_data(self._info, model, data, default)

    def clear(self):
        """
        Clear the data that was extracted from this table
        """
        self._info = None

    def _set_data(self, headers, rows):
        if not self.options.set is None:
           if self.options.format is None:
              self._info = ["set",self.options.set,":="]
              for row in rows:
                self._info = self._info + list(row)
           elif self.options.format is "set_array":
              self._info = ["set",self.options.set, ":"]
              self._info = self._info + list(headers[1:])
              self._info = self._info + [":="]
              for row in rows:
                self._info = self._info + list(row)
           else:
              raise ValueError, "Unknown set format: "+self.options.format

        elif self.options.index is not None and self.options.param is None:
           self._info = ["param",":",self.options.index,":"]
           self._info = self._info + map(str,list(headers[1:]))
           self._info.append(":=")
           for row in rows:
             self._info = self._info + list(row)

        elif self.options.index is not None and self.options.param is not None:
           self._info = ["param",":",self.options.index,":"]
           if type(self.options.param) is str:
              self._info = self._info + [self.options.param]
           elif type(self.options.param) is tuple:
              self._info = self._info + list(self.options.param)
           else:
              self._info = self._info + self.options.param
           self._info.append(":=")
           for row in rows:
             self._info = self._info + list(row)

        elif self.options.param is not None and self.options.format is not None:
           if self.options.format is "transposed_array":
              self._info = ["param",self.options.param,"(tr)",":"] + map(str,list(headers[1:]))
           elif self.options.format is "array":
              self._info = ["param",self.options.param,":"] + map(str,list(headers[1:]))
           else:
              raise ValueError, "Unknown parameter format: "+self.options.format
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
              if self.options.param is None:
                 self._info = self._info + map(str,list(headers[1:]))
              elif type(self.options.param) is str:
                 self._info = self._info + [self.options.param]
              else:
                 self._info = self._info + list(self.options.param)
              self._info.append(":=")
              for row in rows:
                self._info = self._info + list(row)

