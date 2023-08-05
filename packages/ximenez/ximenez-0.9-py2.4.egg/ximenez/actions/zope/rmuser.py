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

"""Define ``ZopeUserRemover``, a plug-in which connects to Zope
instances via XML-RPC and tries to remove an user.

$Id: rmuser.py 42 2007-12-01 16:00:28Z damien.baty $
"""

import logging

from ximenez.actions.action import Action
from ximenez.shared import ConnectionException
from ximenez.shared.zope import ZopeInstance
from ximenez.shared.zope import UnauthorizedException
from ximenez.shared.zope import UserDoNoExistException


def getInstance():
    """Return an instance of ZopeUserRemover."""
    return ZopeUserRemover()


class ZopeUserRemover(Action):
    """An action which removes an user from a collection of Zope
    instances, via XML-RPC.
    """

    _input_info = ()

    def getInput(self, cl_input=None):
        """Get input from the user."""
        if cl_input:
            ## Default handling of command line input.
            Action.getInput(self, cl_input)
            return

        ask = self.askForInput
        self._input.update(ask(({'name': 'user',
                                 'prompt': 'User id to remove: ',
                                 'required': True
                                 },)
                               ))

        self._input.update(ask(({'name': 'manager',
                                 'prompt': 'Manager username: ',
                                 'required': True
                                 },
                                {'name': 'manager_pwd',
                                 'prompt': 'Manager password: ',
                                 'required': True,
                                 'hidden': True
                                 },)
                                ))


    def execute(self, instances):
        """Change the password of an user on each item of ``instances``.

        ``instances`` is supposed to be a sequence of ``ZopeInstance``
        instances or ``<host>:<port>`` strings.
        """
        manager = self._input['manager']
        manager_pwd = self._input['manager_pwd']
        user = self._input['user']

        for instance in instances:
            try:
                instance.removeUser(user, manager, manager_pwd)
                logging.info('Removed "%s" on "%s".', user, instance)
            except ConnectionException:
                msg = 'Could not connect to "%s".'
                logging.error(msg, instance)
            except UnauthorizedException:
                msg = '"%s" is not authorized to remove user on "%s".'
                logging.error(msg, manager, instance)
            except UserDoNoExistException:
                msg = '"%s" does not exist on "%s".'
                logging.error(msg, user, instance)
            except:
                logging.error('Could not remove "%s" from "%s" '\
                              'because of an unexpected exception.',
                              user, instance, exc_info=True)
