#
# Unit Tests for util/misc
#
#

import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
cooprdir = dirname(abspath(__file__))+"/../.."
currdir = dirname(abspath(__file__))+os.sep

import unittest
from nose.tools import nottest
import coopr.opt
import coopr.plugins.mip
import coopr
import pyutilib.services
import pyutilib.component.core


class TestWriter(coopr.opt.AbstractProblemWriter):

    def __init__(self, name=None):
        coopr.opt.AbstractProblemWriter.__init__(self,name)
    

class TestReader(coopr.opt.AbstractResultsReader):

    def __init__(self, name=None):
        coopr.opt.AbstractResultsReader.__init__(self,name)
    

class TestSolver(coopr.opt.OptSolver):

    def __init__(self, **kwds):
        kwds['type'] = 'stest_type'
        kwds['doc'] = 'TestSolver Documentation'
        coopr.opt.OptSolver.__init__(self,**kwds)

    def enabled(self):
        return False


class OptFactoryDebug(unittest.TestCase):

    def run(self, result=None):
        self.stest_plugin = coopr.opt.SolverRegistration("stest", TestSolver)
        self.wtest_plugin = coopr.opt.WriterRegistration("wtest", TestWriter)
        self.rtest_plugin = coopr.opt.ReaderRegistration("rtest", TestReader)
        unittest.TestCase.run(self,result)
        self.stest_plugin.deactivate()
        self.rtest_plugin.deactivate()
        self.wtest_plugin.deactivate()

    def setUp(self):
        pyutilib.services.TempfileManager.tempdir = currdir

    def tearDown(self):
        pyutilib.services.TempfileManager.clear_tempfiles()

    def test_solver_factory(self):
        """
        Testing the coopr.opt solver factory with MIP solvers
        """
        ans = coopr.opt.SolverFactory()
        ans.sort()
        tmp = ['_mock_asl', '_mock_cbc', '_mock_cplex', '_mock_glpk', '_mock_pico', 'cbc', 'cplex', 'glpk', 'pico', 'stest', 'asl']
        tmp.sort()
        self.failUnless(set(tmp) <= set(ans), msg="Set %s is not a subset of set %s" %(tmp,ans))

    def test_solver_instance(self):
        """
        Testing that we get a specific solver instance
        """
        ans = coopr.opt.SolverFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.SolverFactory("_mock_pico")
        self.failUnlessEqual(type(ans), coopr.plugins.mip.MockPICO)
        ans = coopr.opt.SolverFactory("_mock_pico", name="mymock")
        self.failUnlessEqual(type(ans), coopr.plugins.mip.MockPICO)
        self.failUnlessEqual(ans.name,  "mymock")

    def test_solver_registration(self):
        """
        Testing methods in the solverwriter factory registration process
        """
        ep = pyutilib.component.core.ExtensionPoint(coopr.opt.ISolverRegistration)
        service = ep.service("_mock_pico")
        self.failUnlessEqual(service.type(), "_mock_pico")

    def test_writer_factory(self):
        """
        Testing the coopr.opt writer factory with MIP writers
        """
        factory = coopr.opt.WriterFactory()
        self.failUnless(set(['wtest']) <= set(factory))

    def test_writer_instance(self):
        """
        Testing that we get a specific writer instance

        Note: this simply provides code coverage right now, but
        later it should be adapted to generate a specific writer.
        """
        ans = coopr.opt.WriterFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.WriterFactory("wtest")
        self.failIfEqual(ans, None)
        ans = coopr.opt.WriterFactory("wtest", "mywriter")
        self.failIfEqual(ans, None)
        self.failIfEqual(ans.name, "mywriter")

    def test_writer_registration(self):
        """
        Testing methods in the writer factory registration process
        """
        ep = pyutilib.component.core.ExtensionPoint(coopr.opt.IWriterRegistration)
        service = ep.service("wtest")
        self.failUnlessEqual(service.type(), "wtest")


    def test_reader_factory(self):
        """
        Testing the coopr.opt reader factory
        """
        ans = coopr.opt.ReaderFactory()
        #self.failUnlessEqual(len(ans),4)
        self.failUnlessEqual(set(ans), set(["osrl","rtest", "sol","yaml"]))

    def test_reader_instance(self):
        """
        Testing that we get a specific reader instance
        """
        ans = coopr.opt.ReaderFactory("none")
        self.failUnlessEqual(ans, None)
        ans = coopr.opt.ReaderFactory("osrl")
        self.failUnlessEqual(type(ans), coopr.opt.reader.OS.ResultsReader_osrl)
        ans = coopr.opt.ReaderFactory("osrl", "myreader")
        self.failUnlessEqual(type(ans), coopr.opt.reader.OS.ResultsReader_osrl)
        self.failUnlessEqual(ans.name, "myreader")

    def test_reader_registration(self):
        """
        Testing methods in the reader factory registration process
        """
        ep = pyutilib.component.core.ExtensionPoint(coopr.opt.IReaderRegistration)
        service = ep.service("rtest")
        self.failUnlessEqual(service.type(), "rtest")

if __name__ == "__main__":
   unittest.main()

