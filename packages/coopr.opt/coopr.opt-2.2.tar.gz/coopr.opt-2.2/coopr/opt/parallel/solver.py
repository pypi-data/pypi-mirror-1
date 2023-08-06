#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


__all__ = ['AsynchronousSolverManager', 'SolverManagerRegistration', 'SolverManagerFactory']

import pyutilib.component.core
import pyutilib.component.config
from manager import *


#
# An interface for AsynchronousSolverManager objects
#
class ISolverManager(pyutilib.component.core.Interface):
    pass


class ISolverManagerRegistration(pyutilib.component.core.Interface):

    def create(self, name=None):
        """Create a manager, optionally specifying the name"""

    def type(self):
        """The type of manager supported by this service"""


def SolverManagerFactory(name=None, instance_name=None):
    ep = pyutilib.component.core.ExtensionPoint(ISolverManagerRegistration)
    if name is None:
        return map(lambda x:x.name, ep())
    service = ep.service(name)
    if service is None:
        return None
    return service.create(instance_name)


class SolverManagerRegistration(pyutilib.component.core.Plugin):

    pyutilib.component.core.implements(ISolverManagerRegistration)

    def __init__(self, type, cls):
        self.name = type
        self._type = type
        self._cls = cls

    def type(self):
        return self._type

    def create(self, name=None):
        if name is None:
            return self._cls()
        return self._cls(name=name)



class AsynchronousSolverManager(AsynchronousActionManager, pyutilib.component.config.ManagedPlugin):

    pyutilib.component.core.implements(ISolverManager)

    def __init__(self, **kwds):
        AsynchronousActionManager.__init__(self)
        pyutilib.component.config.ManagedPlugin.__init__(self, **kwds)

    def solve(self, *args, **kwds):
        return self.execute(*args, **kwds)



