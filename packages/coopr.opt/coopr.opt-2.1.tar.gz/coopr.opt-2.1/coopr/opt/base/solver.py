#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['ISolverRegistration', 'SolverRegistration',
            'IOptSolver', 'OptSolver', 'SolverFactory']

import os
import sys
from convert import convert_problem
from formats import ResultsFormat, ProblemFormat
import results
from coopr.opt.results import SolverResults, SolverStatus

from pyutilib.enum import Enum
from pyutilib.plugin.core import *
from pyutilib.plugin.config import *
import pyutilib.common
import pyutilib.misc


class ISolverRegistration(Interface):
    """An interface for accessing"""

    def create(self, name=None):
        """Create a solver, optionally specifying the name"""

    def type(self):
        """The type of solver supported by this service"""


class SolverRegistration(Plugin):

    implements(ISolverRegistration)

    def __init__(self, type, cls):
        self.name = type
        self._type = type
        self._cls = cls

    def type(self):
        return self._type

    def create(self, **kwds):
        return self._cls(**kwds)


def SolverFactory(solver_name=None, **kwds):
    ep = ExtensionPoint(ISolverRegistration)
    if solver_name is None:
        names = map(lambda x:x.name, ep())
        names.sort()
        return names
    service = ep.service(solver_name)
    if service is None:
        ##print "Unknown solver=" + solver_name + " - no plugin registered for this solver type"
        return None
    else:
        return ep.service(solver_name).create(**kwds)


class IOptSolver(Interface):
    """Interface class for creating optimization solvers"""

    def available(self, exception_flag=True):
        """Determine if this optimizer is available."""

    def solve(self, *args, **kwds):
        """Perform optimization and return an SolverResults object."""

    def reset(self):
        """Reset the state of an optimizer"""

    def set_options(self, istr):
        """Set the options in the optimizer from a string."""


class OptSolver(ManagedPlugin):
    """A generic optimization solver"""

    implements(IOptSolver)

    def __init__(self, **kwds):
        """ Constructor """
        ManagedPlugin.__init__(self,**kwds)
        #
        # The 'type' is the class type of the solver instance
        #
        if "type" in kwds:
            self.type = kwds["type"]
        else:                           #pragma:nocover
            raise PluginError, "Expected option 'type' for OptSolver constructor"
        #
        # The 'name' is either the class type of the solver instance, or a
        # assigned name.
        #
        if "name" in kwds:
            self.name = kwds["name"]
        else:
            self.name = self.type
        if "doc" in kwds:
            self._doc = kwds["doc"]
        else:
            if self.type is None:           # pragma:nocover
                self._doc = ""
            elif self.name == self.type:
                self._doc = "%s OptSolver" % self.name
            else:
                self._doc = "%s OptSolver (type %s)" % (self.name,self.type)
        declare_option("options", cls=DictOption, section=self.name, doc=self._doc)
        if 'options' in kwds:
            for key in kwds['options']:
                setattr(self.options,key,kwds['options'][key])
        self._symbol_map=None
        self._problem_format=None
        self._results_format=None
        self._valid_problem_formats=[]
        self._valid_result_formats={}
        self.results_reader=None
        self.problem=None
        self._assert_available=False

        # a fairly universal solver feature, at least when dealing
        # with problems containing integers. promoted to a base class
        # attribute to allow each sub-solver to automatically write
        # out the appropriate option. default is None, meaning
        # unassigned. currently not allowing the mipgap to be over-ridden
        # via an argument to the solve() method, mainly because we don't
        # want to persistence of this parameter to be violated.
        self.mipgap = None

    def available(self, exception_flag=True):
        """ True if the solver is available """
        if self._assert_available:
            return True
        tmp = self.enabled()
        if exception_flag and not tmp:
            raise pyutilib.common.ApplicationError, "OptSolver plugin %s is disabled" % self.name
        return tmp

    def warm_start_capable(self):
       """ True is the solver can accept a warm-start solution """
       return False

    def solve(self, *args, **kwds):
        """ Solve the problem """
        self._presolve(*args, **kwds)
        self._apply_solver()
        result = self._postsolve()
        result.symbol_map = self._symbol_map
        return result

    def _presolve(self, *args, **kwds):
        self.available()
        self._timelimit=None
        self.tee=None
        for key in kwds:
          if key == "pformat":
             self._problem_format=kwds[key]
          elif key == "rformat":
             self._results_format=kwds[key]
          elif key == "logfile":
             self.log_file=kwds[key]
          elif key == "solnfile":
             self.soln_file=kwds[key]
          elif key == "timelimit":
             self._timelimit=kwds[key]
          elif key == "tee":
             self.tee=kwds[key]
          elif key == "options":
             self.set_options(kwds[key])
          elif key == "available":
             self._assert_available=True
          else:
             raise ValueError, "Unknown option="+key+" for solver="+self.type

        (self._problem_files,self._problem_format,self._symbol_map) = self._convert_problem(args, self._problem_format, self._valid_problem_formats)
        if self._results_format is None:
           self._results_format= self._default_results_format(self._problem_format)
        #
        # Disabling this check for now.  A solver doesn't have just _one_ results format.
        #
        #if self._results_format not in self._valid_result_formats[self._problem_format]:
        #   raise ValueError, "Results format `"+str(self._results_format)+"' cannot be used with problem format `"+str(self._problem_format)+"' in solver "+self.name
        if self._results_format == ResultsFormat.soln:
            self.results_reader = None
        else:
            self.results_reader = results.ReaderFactory(self._results_format)

    def _apply_solver(self):
        """The routine that performs the solve"""
        raise NotImplementedError       #pragma:nocover
        
    def _postsolve(self):
        """The routine that does solve post-processing"""
        return self.results
        
    def _convert_problem(self, args, pformat, valid_pformats):
        #
        # If the problem is not None, then we assume that it has already
        # been appropriately defined.  Either it's a string name of the
        # problem we want to solve, or its a functor object that we can
        # evaluate directly.
        #
        if self.problem is not None:
           return (self.problem,ProblemFormat.colin_optproblem,None)
        #
        # Otherwise, we try to convert the object explicitly.
        #
        return convert_problem(args, pformat, valid_pformats)

    def _default_results_format(self, prob_format):
        """Returns the default results format for different problem
            formats.
        """
        return ResultsFormat.results

    def reset(self):
        """
        Reset the state of the solver
        """
        pass

    def set_options(self, istr):
        istr = istr.strip()
        if istr is '':
            return
        tokens = pyutilib.misc.quote_split('[ ]+',istr)
        for token in tokens:
            index = token.find('=')
            if index is -1:
                raise ValueError, "Solver options must have the form option=value"
            try:
                val = eval(token[(index+1):])
            except:
                val = token[(index+1):]
            setattr(self.options, token[:index], val)
            
            
    
