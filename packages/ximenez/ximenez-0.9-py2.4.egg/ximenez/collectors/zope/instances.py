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

"""Define ``ZopeInstances``, which can collect Zope instances.

$Id: instances.py 8 2007-11-10 13:06:44Z damien.baty $
"""

from ximenez.collectors.collector import Collector
from ximenez.shared.zope import ZopeInstance


def getInstance():
    """Return an instance of ``ZopeInstances``."""
    return ZopeInstances()


class ZopeInstances(Collector):
    """A collector which returns instances of Zope servers.

    It asks for the location of the host (which can be its IP or its
    name) and the port which it listens HTTP connections on.

    Returns a tuple of ``ZopeInstance`` instances.
    """

    _input_info = ({'name': 'host',
                    'prompt': 'Host: ',
                    'required': True},
                   {'name': 'port',
                    'prompt': 'HTTP port: ',
                    'required': True},
                   )
    _multiple_input = True


    def collect(self):
        """Return a tuple of ``ZopeInstance`` instances."""
        return [ZopeInstance(item['host'],
                             item['port']) for item in self._input]
