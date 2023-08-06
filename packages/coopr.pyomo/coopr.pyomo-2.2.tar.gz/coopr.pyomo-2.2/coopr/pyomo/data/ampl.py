
import os.path
import re
from pyutilib.misc import Options, quote_split
from coopr.pyomo.base.plugin import DataManagerRegistration
from process_data import _process_data

class AmplDataCommands(object):

    def __init__(self):
        self._info = []

    def initialize(self, filename, **kwds):
        self.filename = filename
        self.options = Options(**kwds)

    def open(self):
        if self.filename is None:
            raise IOError, "No filename specified"
        if not os.path.exists(self.filename):
            raise IOError, "Cannot find file '%s'" % self.filename
        self.INPUT = open(self.filename, 'r')

    def close(self):
        self.INPUT.close()
        
    def read(self):
        """
        Create a table of tuples to values, based on data from a file.
        We assume that this data is defined in a format that is
        compatible with AMPL.
        """
        global Filename
        Filename = self.filename
        global Lineno
        Lineno = 0
        cmd=""
        status=True
        for line in self.INPUT:
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
                  self._info.append(quote_split("[\t ]+",item))
             cmd = ""
        if cmd != "":
            raise IOError, "ERROR: There was unprocessed text at the end of the data file!: \"" + cmd + "\""
            self.INPUT.close()
        self.INPUT.close()
        return status

    def process(self, model, data, default):
        """
        Return the data that was extracted from this table
        """
        for item in self._info:
            _process_data(item, model, data, default)

    def clear(self):
        self._info = []



DataManagerRegistration("dat", AmplDataCommands, "Import data with AMPL data commands.")

