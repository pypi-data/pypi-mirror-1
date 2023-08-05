## Copyright (c) 2007 Damien Baty
##
## This file is part of Ximenez.
##
## Ximenez is free software; you can redistribute it and/or modify it
## under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## Ximenez is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see
## <http://www.gnu.org/licenses/>.

"""Define ``ZopeInstancesReadlines``, which can collect Zope instances
that are listed in a file.

$Id: readlines.py 30 2007-11-25 16:46:12Z damien.baty $
"""

from ximenez.shared.zope import ZopeInstance
from ximenez.collectors.misc.readlines import ReadLines as BaseReadlinesCollector


def getInstance():
    """Return an instance of ``ZopeInstancesReadlines``."""
    return ZopeInstancesReadlines()


class ZopeInstancesReadlines(BaseReadlinesCollector):
    """A collector which returns instances of Zope servers that are
    listed in a file.

    It asks for the pathname of the file whose lines should have the
    following format::

        <host>:<port>

    Returns a tuple of ``ZopeInstance`` instances.
    """

    def collect(self):
        """Return a tuple of ``ZopeInstance`` objects."""
        instances = []
        for line in BaseReadlinesCollector.collect(self):
            host, port = line.split(':')
            port = port.strip()
            instances.append(ZopeInstance(host, port))
        return instances
