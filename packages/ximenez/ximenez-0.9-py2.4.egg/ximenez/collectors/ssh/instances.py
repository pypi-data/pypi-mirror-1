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

"""Define ``SSHRemoteHostInstances``, which can collect SSH remote
hosts.

$Id: instances.py 13 2007-11-13 23:32:22Z damien.baty $
"""

from ximenez.shared.ssh import SSHRemoteHost
from ximenez.collectors.collector import Collector


def getInstance():
    """Return an instance of ``SSHRemoteHostInstances``."""
    return SSHRemoteHostInstances()


class SSHRemoteHostInstances(Collector):
    """A collector which returns instances of SSH remote hosts.

    It asks for the location of the host (which can be its IP or its
    name) and the port that it listens on (which defaults to 22).

    Returns a tuple of ``SSHRemoteHost`` instances.
    """

    _input_info = ({'name': 'host',
                    'prompt': 'Host: ',
                    'required': True},
                   {'name': 'port',
                    'prompt': 'Port: ',
                    'default': '22',
                    'required': False},
                   )
    _multiple_input = True


    def collect(self):
        """Return a tuple of ``SSHRemote`` instances."""
        return [SSHRemoteHost(item['host'],
                              item['port']) for item in self._input]
