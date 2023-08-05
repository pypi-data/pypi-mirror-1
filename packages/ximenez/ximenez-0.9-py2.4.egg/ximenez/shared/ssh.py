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

"""Define various classes and functions related to SSH.

$Id: ssh.py 42 2007-12-01 16:00:28Z damien.baty $
"""

from popen2 import popen3

from ximenez.shared import ConnectionException


DEFAULT_PORT = '22'

class SSHRemoteHost(object):
    """A class which represents an SSH remote host."""
    def __init__(self, host, port=None, user=None):
        self.host = host
        self.port = port or DEFAULT_PORT
        self.user = user


    def __repr__(self):
        representation = ':'.join((self.host, self.port))
        if self.user:
            representation = '%s@%s' % (self.user, representation)
        return representation


    def execute(self, command):
        """Execute ``command`` on the remote host via SSH and return the
        output.

        This method takes care of escaping ``command`` if needed.
        """
        host = self.host
        if self.user:
            host = '%s@%s' % (self.user, host)
        command = escapeShellCommand(command)
        cmd = 'ssh -p %s %s %s' % (self.port, host, command)
        stdout, stdin, stderr = popen3(cmd)
        stdout = stdout.read()
        stderr = stderr.read()
        if stderr.startswith('ssh: %s:' % self.host):
            raise ConnectionException()
        output = stdout + stderr
        output = output.strip()
        return output


def escapeShellCommand(command,
                       special_chars=""";&|!><~*{}[]?()$\\`"""):
    """Escape special shell characters from ``command``."""
    ## This is probaly slower than using a regexp, but definitely more
    ## readable.
    escaped = ''
    for c in command:
        if c in special_chars:
            escaped += "\\"
        escaped += c
    return escaped
