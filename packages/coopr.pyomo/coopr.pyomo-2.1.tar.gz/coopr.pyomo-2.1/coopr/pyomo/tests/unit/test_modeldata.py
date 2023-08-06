#
# Unit Tests for ModelData objects
#

import unittest
import os
import sys
from os.path import abspath, dirname
coopr_dir=dirname(dirname(abspath(__file__)))+os.sep+".."+os.sep+".."
sys.path.insert(0, coopr_dir)
from coopr.pyomo import *
import coopr

currdir=dirname(abspath(__file__))+os.sep
example_dir=coopr_dir+os.sep+"example"+os.sep+"pyomo"+os.sep+"tutorials"+os.sep+"tab"+os.sep

try:
  from win32com.client.dynamic import Dispatch
  _win32com=True
except:
  _win32com=False #pragma:nocover


class PyomoTableData(unittest.TestCase):

    def run(self, result=None):
        """ Disable the tests if win32com is not available """
        if not _win32com:
           return
        unittest.TestCase.run(self,result)

    def setUp(self):
        pass

    def construct(self,filename):
        pass

    def test_read_set(self):
        td = TableData(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls",range="TheRange",set="X")
        try:
           td.open()
           td.read()
           td.close()
           self.failUnlessEqual( td.data(), ['set', 'X', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
           pass

    def test_read_set2(self):
        td = TableData(range="TheRange",set="X")
        try:
           td.open(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls")
           td.read()
           td.close()
           self.failUnlessEqual( td.data(), ['set', 'X', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
           pass

    def test_read_param1(self):
        td = TableData(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls",range="TheRange")
        try:
          td.open()
          td.read()
          td.close()
          self.failUnlessEqual( td.data(), ['param', ':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
          pass

    def test_read_param2(self):
        td = TableData(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls",range="TheRange",index="X")
        try:
          td.open()
          td.read()
          td.close()
          self.failUnlessEqual( td.data(), ['param', ':', 'X', ':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
          pass

    def test_read_param3(self):
        td = TableData(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls",range="TheRange",index="X", param="a")
        try:
          td.open()
          td.read()
          td.close()
          self.failUnlessEqual( td.data(), ['param', ':', 'X', ':', 'a', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
          pass

    def test_read_param4(self):
        td = TableData(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls",range="TheRange",index="X", param=("a","b"))
        try:
          td.open()
          td.read()
          td.close()
          self.failUnlessEqual( td.data(), ['param', ':', 'X', ':', 'a', 'b', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
          pass

    def test_read_array1(self):
        td = TableData(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls",range="TheRange",param="X", format="array")
        try:
          td.open()
          td.read()
          td.close()
          self.failUnlessEqual( td.data(), ['param', 'X', ':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
          pass

    def test_read_array2(self):
        td = TableData(filename=coopr_dir+"\\test\\acro\\unit\\Book1.xls",range="TheRange",param="X",format="transposed_array")
        try:
          td.open()
          td.read()
          td.close()
          self.failUnlessEqual( td.data(), ['param', 'X', '(tr)',':', 'bb', 'cc', 'dd', ':=', 'A1', 2.0, 3.0, 4.0, 'A5', 6.0, 7.0, 8.0, 'A9', 10.0, 11.0, 12.0, 'A13', 14.0, 15.0, 16.0])
        except coopr.ApplicationError:
          pass

    def test_error1(self):
        td = TableData(filename="bad")
        try:
            td.open()
            self.fail("Expected IOError because of bad file")
        except IOError:
            pass

    def test_error2(self):
        td = TableData()
        try:
            td.open()
            self.fail("Expected IOError because no file specified")
        except IOError:
            pass

    def test_error3(self):
        td = TableData(filename=currdir+"display.txt")
        try:
            td.open()
            self.fail("Expected IOError because of bad file type")
        except IOError:
            pass

    def test_error4(self):
        td = TableData(filename=currdir+"dummy")
        try:
            td.open()
            self.fail("Expected IOError because of bad file type")
        except IOError:
            pass

    def test_error5(self):
        td = TableData(filename=example_dir+"D.tab", param="D", format="foo")
        td.open()
        try:
            td.read()
            self.fail("Expected IOError because of bad format")
        except ValueError:
            pass

    def test_error7(self):
        td = TableData(filename=example_dir+"D.tab", set="D", format="foo")
        td.open()
        try:
            td.read()
            self.fail("Expected IOError because of bad format")
        except ValueError:
            pass



class PyomoModelData(unittest.TestCase):

    def test_md1(self):
        md = ModelData()
        md.add_table(example_dir+"A.tab")
        try:
            md.read()
            self.fail("Must specify a model")
        except ValueError:
            pass
        model=Model()
        try:
            md.read(model)
            self.fail("Expected IOError")
        except IOError:
            pass
        model.A=Set()

    def test_md2(self):
        md = ModelData()
        md.add_data_file(currdir+"data1.dat")
        model=Model()
        model.A=Set()
        md.read(model)

    def test_md3(self):
        md = ModelData()
        md.add_data_file(currdir+"data2.dat")
        model=Model()
        model.A=Set()
        try:
            md.read(model)
            self.fail("Expected error because of extraneous text")
        except IOError:
            pass

    def test_md4(self):
        md = ModelData()
        md.add_data_file(currdir+"data3.dat")
        model=Model()
        model.A=Set()
        model.B=Set()
        model.C=Set()
        md.read(model)

    def test_md5(self):
        md = ModelData()
        md.add_data_file(currdir+"data4.dat")
        model=Model()
        model.A=Set()
        try:
            md.read(model)
        except ValueError:
            pass

    def test_md6(self):
        md = ModelData()
        md.add_data_file(currdir+"data5.dat")
        model=Model()
        model.A=Set()
        try:
            md.read(model)
        except ValueError:
            pass

    def test_md7(self):
        md = ModelData()
        md.add_table(currdir+"data1.tab")
        model=Model()
        try:
            md.read(model)
            self.fail("Expected IOError")
        except IOError:
            pass

    def test_md8(self):
        md = ModelData()
        md.add_data_file(currdir+"data6.dat")
        model=Model()
        model.A=Set()
        try:
            md.read(model)
            self.fail("Expected IOError")
        except IOError:
            pass

    def test_md9(self):
        md = ModelData()
        md.add_data_file(currdir+"data7.dat")
        model=Model()
        model.A=Set()
        model.B=Param(model.A)
        md.read(model)

    def test_md10(self):
        md = ModelData()
        md.add_data_file(currdir+"data8.dat")
        model=Model()
        model.A=Param(within=Boolean)
        model.B=Param(within=Boolean)
        md.read(model)


if __name__ == "__main__":
   unittest.main()

