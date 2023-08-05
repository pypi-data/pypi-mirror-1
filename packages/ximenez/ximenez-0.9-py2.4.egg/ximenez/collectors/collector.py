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

"""Define ``Collector`` abstract class.

$Id: collector.py 8 2007-11-10 13:06:44Z damien.baty $
"""

from ximenez.input import InputAware


class Collector(object, InputAware):
    """The purpose of a collector is to collect information.

    ``Collector`` is an abstract class which real collector plug-ins
    must subclass.
    """

    def collect(self):
        """Collect informations and return a tuple of items (the type
        of these items depends on the purpose of this collector).

        This method **must** be implemented.
        """
        raise NotImplementedError
