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

"""Define various utility functions.

$Id: utils.py 26 2007-11-23 22:36:07Z damien.baty $
"""

import imp
import os.path


def getPluginInstance(plugin, kind=None):
    """Retrieve a plug-in instance from ``plugin``.

    ``plugin`` may be:

    - the path (file path) to a Python module which defines a plug-in.

    - a (possibly dotted) module name from the set of built-in Ximenez
    plug-ins. In this case, ``kind`` must be either ``actions`` or
    ``collectors` (because these are the names of the related
    sub-packages in Ximenez).
    """
    if os.path.exists(plugin):
        module = imp.load_source('plugin', plugin)
    else:
        if not kind:
            raise ImportError('Plugin-in kind is missing.')
        module_path = '.'.join(('ximenez', kind, plugin))
        module = __import__(module_path)
        for component in module_path.split('.')[1:]:
            module = getattr(module, component)

    return module.getInstance()
