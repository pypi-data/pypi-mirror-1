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

"""Define ``SSHRemoteHostsReadlines``, which can collect SSH remote
hosts instances that are listed in a file.

$Id: readlines.py 12 2007-11-13 23:31:33Z damien.baty $
"""

from ximenez.shared.ssh import SSHRemoteHost
from ximenez.collectors.misc.readlines import ReadLines as BaseReadlinesCollector


def getInstance():
    """Return an instance of ``SSHRemoteHostsReadlines``."""
    return SSHRemoteHostsReadlines()


class SSHRemoteHostsReadlines(BaseReadlinesCollector):
    """A collector which returns instances of SSH remote hosts that
    are listed in a file.

    It asks for the pathname of the file, whose lines should have the
    following format::

        <host>[:<port>]

    ``<port>`` is optional. If not given, it is supposed to be the
    default SSH port (22).

    This method returns a tuple of ``SSHRemoteHost`` instances.
    """

    def collect(self):
        """Return a tuple of ``SSHRemoteHost`` instances."""
        instances = []
        for line in BaseReadlinesCollector.collect(self):
            if ':' not in line:
                host = line.strip()
                port = None
            else:
                host, port = line.split(':')
                port = port.strip()
            instances.append(SSHRemoteHost(host, port))
        return instances
