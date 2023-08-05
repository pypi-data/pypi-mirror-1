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

"""Define ``Action`` abstract class.

$Id: action.py 8 2007-11-10 13:06:44Z damien.baty $
"""

from ximenez.input import InputAware


class Action(object, InputAware):
    """The purpose of action plug-ins is to... do things.

    ``Action`` is an abstract class which real action plug-ins must
    subclass.
    """

    def execute(self, sequence):
        """Execute an action on ``sequence`` (whose type of items
        depends on the collector being used).

        This method **must** be implemented.
        """
        raise NotImplementedError
