#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = [ 'IReaderRegistration', 'ReaderRegistration',
            'IResultsReader', 'AbstractResultsReader',
            'ReaderFactory' ]

from pyutilib.component.core import *
from pyutilib.component.config import *


class IReaderRegistration(Interface):
    """An interface for accessing"""

    def create(self, name=None):
        """Create a reader, optionally specifying the name"""

    def type(self):
        """The type of reader supported by this service"""


def ReaderFactory(name=None, reader_name=None):
    ep = ExtensionPoint(IReaderRegistration)
    if name is None:
        names = map(lambda x:x.name, ep())
        names.sort()
        return names
    service = ep.service(name)
    if service is None:
        return None
    return service.create(reader_name)


class ReaderRegistration(Plugin):

    implements(IReaderRegistration)

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


class IResultsReader(Interface):
    """Interface for classes that can read optimization results."""


class AbstractResultsReader(ManagedPlugin):
    """Base class that can read optimization results."""

    implements(IResultsReader)

    def __init__(self, results_format):
        ManagedPlugin.__init__(self)
        self.format=results_format

    def __call__(self, filename, res=None): #pragma:nocover
        raise TypeError, "Method __call__ undefined in reader for format "+str(self.format)

