#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


__all__ = ['PyomoMIPConverter']

from coopr.opt.base import *
from pico import PicoMIPConverter

from pyutilib.plugin.core import *
from pyutilib.plugin.config import *
from pyutilib.plugin.executables import *
import pyutilib.services

class PyomoMIPConverter(ManagedSingletonPlugin):

    implements(IProblemConverter)

    cmd = ExtensionPoint(IExternalExecutable)
    pico_converter = PicoMIPConverter()

    def __init__(self,**kwds):
        ManagedSingletonPlugin.__init__(self,**kwds)

    def can_convert(self, from_type, to_type):
        """Returns true if this object supports the specified conversion"""
        #
        # Return True for specific from/to pairs
        #
        if from_type == ProblemFormat.pyomo and to_type == ProblemFormat.nl:
            return True
        if from_type == ProblemFormat.pyomo and to_type == ProblemFormat.cpxlp:
            return True
        if from_type == ProblemFormat.pyomo and to_type == ProblemFormat.mps:
            return True
        return False

    def apply(self, *args):
        """
        Generate a NL or LP file from Pyomo, and then do subsequent
        conversions.
        """

        if args[1] is ProblemFormat.cpxlp:
            problem_filename = pyutilib.services.TempfileManager.create_tempfile(suffix = '.pyomo.lp')
            (problem_filename, varmap) = args[2].write(filename=problem_filename,format=ProblemFormat.cpxlp)
            return (problem_filename,),None # no map file is necessary
        elif args[1] is ProblemFormat.mps:
            # TBD: We don't support a variable map file when going from NL to MPS within the PICO converter.
            problem_filename = pyutilib.services.TempfileManager.create_tempfile(suffix = '.pyomo.nl')
            (problem_filename, varmap) = args[2].write(filename=problem_filename,format=ProblemFormat.nl)
            ans = self.pico_converter.apply(ProblemFormat.nl,ProblemFormat.mps,problem_filename)
            os.remove(problem_filename)
            return ans
        elif args[1] is ProblemFormat.nl:
            problem_filename = pyutilib.services.TempfileManager.create_tempfile(suffix = '.pyomo.nl')
            (problem_filename, symbol_map) = args[2].write(filename=problem_filename,format=ProblemFormat.nl)
            return (problem_filename,),symbol_map # map file is necessary

