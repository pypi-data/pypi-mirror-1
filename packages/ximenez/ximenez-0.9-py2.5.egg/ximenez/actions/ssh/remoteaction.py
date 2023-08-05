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

"""Define ``SSHRemote``, a plug-in which can execute a command
on a remote host via SSH.

$Id: remoteaction.py 42 2007-12-01 16:00:28Z damien.baty $
"""

import os
import logging

from ximenez.actions.action import Action
from ximenez.shared import ConnectionException


def getInstance():
    """Return an instance of ``SSHRemote``."""
    return SSHRemote()


class SSHRemote(Action):
    """Connect to remote hosts via SSH, execute a command and return
    its output.
    """

    _input_info = ({'name': 'command',
                    'prompt': 'Command: ',
                    'required': True}, )


    def getInput(self, cl_input=None):
        """Get input from the user if what was provided in the command
        line (available in ``cl_input``) was not sufficient.

        If a value is given in the command line (``cl_input``), we
        suppose it is the command to execute.
        """
        if cl_input:
            self._input['command'] = cl_input
        else:
            ## Back to the default implementation
            Action.getInput(self, cl_input)


    def execute(self, sequence):
        """Connect to each host of ``sequence`` and execute a
        command.
        """
        command = self._input['command']
        for host in sequence:
            try:
                output = host.execute(command)
                logging.info('Executing "%s" on "%s":%s%s',
                         command, host, os.linesep, output)
            except ConnectionException:
                logging.error('Could not connect to "%s".' % host)
