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

"""Define ``Readlines`` collector, which read lines from a file.

$Id: readlines.py 18 2007-11-17 16:04:12Z damien.baty $
"""

from ximenez.collectors.collector import Collector


def getInstance():
    """Return an instance of ``ReadLines``."""
    return ReadLines()


class ReadLines(Collector):
    """A very simple collector which asks for the path of a file and
    returns a tuple containing each line of this file.
    """

    _input_info = ({'name': 'path',
                    'prompt': 'Path of the file: ',
                    'required': True
                    },
                   )


    def getInput(self, cl_input=None):
        """Get input from the user if what was provided in the command
        line (available in ``cl_input``) was not sufficient.

        If a value is given in the command line (``cl_input``), we
        suppose it is the path of the file.
        """
        if cl_input:
            self._input['path'] = cl_input
        else:
            ## Back to the default implementation
            Collector.getInput(self, cl_input)


    def collect(self):
        """Return lines of the file at ``path`` (without "end of line"
        characters), as a tuple.
        """
        path = self._input['path']
        lines = open(path, 'r').readlines()
        return [line.rstrip('\n\r') for line in lines]
