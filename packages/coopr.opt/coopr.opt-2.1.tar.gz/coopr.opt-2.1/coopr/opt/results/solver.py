#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['SolverInformation', 'SolverStatus', 'TerminationStatus']

from container import *
from pyutilib.enum import Enum


SolverStatus = Enum('error', 'warning', 'ok', 'aborted')
TerminationStatus = Enum('maxIterations', 'minFunctionValue', 'minStepLength', 'unbounded', 'globallyOptimal', 'locallyOptimal',
                            'optimal', 'bestSoFar', 'feasible', 'infeasible',
                            'stoppedByLimit', 'unsure', 'error', 'other')



class BranchAndBoundStats(MapContainer):

    def __init__(self):
        MapContainer.__init__(self)
        self.declare('number of bounded subproblems')
        self.declare('number of created subproblems')


class BlackBoxStats(MapContainer):

    def __init__(self):
        MapContainer.__init__(self)
        self.declare('number of function evaluations')
        self.declare('number of gradient evaluations')
        self.declare('number of iterations')


class SolverStatistics(MapContainer):

    def __init__(self):
        MapContainer.__init__(self)
        self.declare("branch_and_bound", value=BranchAndBoundStats(), active=False)
        self.declare("black_box", value=BlackBoxStats(), active=False)


class SolverInformation(MapContainer):

    def __init__(self):
        MapContainer.__init__(self)
        self.declare('solver_ID')
        self.declare('status', value=SolverStatus.ok)
        self.declare('return_code')
        self.declare('message')
        self.declare('user_time', type=ScalarType.time)
        self.declare('system_time', type=ScalarType.time)
        self.declare('termination_condition', value=TerminationStatus.unsure)
        self.declare('termination_message')
        self.declare('statistics', value=SolverStatistics(), active=False)

