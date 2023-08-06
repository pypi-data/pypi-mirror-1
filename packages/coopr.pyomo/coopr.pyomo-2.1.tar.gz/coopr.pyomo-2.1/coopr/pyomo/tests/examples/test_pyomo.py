#
# Test the Pyomo command-line interface
#

import unittest
import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep
scriptdir = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))+os.sep

from coopr.pyomo import *
import pyutilib.services
import pyutilib.subprocess
import pyutilib.th
import coopr.pyomo.main_script as main
import StringIO 
from pyutilib.misc import setup_redirect, reset_redirect

if os.path.exists(sys.exec_prefix+os.sep+'bin'+os.sep+'coverage'):
    executable=sys.exec_prefix+os.sep+'bin'+os.sep+'coverage -x '
else:
    executable=sys.executable

class Test(pyutilib.th.TestCase):

    def run(self, result=None):
        """
        Run the tests if GLPK is available
        """
        if pyutilib.services.registered_executable("glpsol") is None:
            return
        pyutilib.th.TestCase.run(self, result)

    def pyomo(self, cmd, **kwds):
        args=re.split('[ ]+',cmd)
        if 'file' in kwds:
            OUTPUT=kwds['file']
        else:
            OUTPUT=StringIO.StringIO()
        setup_redirect(OUTPUT)
        os.chdir(currdir)
        main.run(list(args))
        reset_redirect()
        if not 'file' in kwds:
            return OUTPUT.getvalue()
        
    def test1(self):
        """Simple execution of 'pyomo'"""
        self.pyomo('pmedian.py pmedian.dat', file=currdir+'test1.out')
        self.failUnlessFileEqualsBaseline(currdir+"test1.out", currdir+"test1.txt")

    def test2(self):
        """Run pyomo with bad --model-name option value"""
        output=self.pyomo('--model-name=dummy pmedian.py pmedian.dat')
        self.failUnlessEqual(output.strip(),"Exiting pyomo: Neither 'dummy' nor 'create_model' are available in module pmedian.py")

    def test3(self):
        """Run pyomo with model that does not define model object"""
        output=self.pyomo('pmedian1.py pmedian.dat')
        self.failUnlessEqual(output.strip(),"Exiting pyomo: Neither 'model' nor 'create_model' are available in module pmedian1.py")

    def test4(self):
        """Run pyomo with good --model-name option value"""
        self.pyomo('--model-name=MODEL pmedian1.py pmedian.dat', file=currdir+'test4.out')
        self.failUnlessFileEqualsBaseline(currdir+"test4.out", currdir+"test1.txt")

    def test5(self):
        """Run pyomo with create_model function"""
        self.pyomo('pmedian2.py pmedian.dat', file=currdir+'test5.out')
        self.failUnlessFileEqualsBaseline(currdir+"test5.out", currdir+"test1.txt")

    def test6(self):
        """Run pyomo with help-components option"""
        self.pyomo('--help-components', file=currdir+'test6.out')
        self.failUnlessFileEqualsBaseline(currdir+"test6.out", currdir+"test6.txt")


if __name__ == "__main__":
   unittest.main()
