#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = [ 'IWriterRegistration', 'WriterRegistration',
            'IProblemWriter', 'AbstractProblemWriter',
            'WriterFactory' ]

from pyutilib.component.core import *
from pyutilib.component.config import *


class IWriterRegistration(Interface):
    """An interface for accessing"""

    def create(self, name=None):
        """Create a writer, optionally specifying the name"""

    def type(self):
        """The type of writer supported by this service"""


def WriterFactory(name=None, writer_name=None):
    ep = ExtensionPoint(IWriterRegistration)
    if name is None:
        names = map(lambda x:x.name, ep())
        names.sort()
        return names
    service = ep.service(name)
    if service is None:
        return None
    return service.create(writer_name)


class WriterRegistration(Plugin):

    implements(IWriterRegistration)

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


class IProblemWriter(Interface):
    """Interface for classes that can write optimization problems."""


class AbstractProblemWriter(ManagedPlugin):
    """Base class that can write optimization problems."""

    implements(IProblemWriter)

    def __init__(self, problem_format): #pragma:nocover
        ManagedPlugin.__init__(self)
        self.format=problem_format

    def __call__(self, model, filename): #pragma:nocover
        raise TypeError, "Method __call__ undefined in writer for format "+str(self.format)

