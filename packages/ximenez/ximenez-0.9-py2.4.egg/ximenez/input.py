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

"""Define ``InputAware`` mixin.

$Id: input.py 45 2008-01-19 17:05:45Z damien.baty $
"""

try:
    import readline
except ImportError:
    pass ## No support for 'readline'.
    ## FIXME: auto-completion features will not work. Do we have to
    ## take care of this?
import logging
from getpass import getpass
from types import StringType


## We define wrappers around ``raw_input`` and ``getpass.getpass`` so
## that we can fake input in our tests (see ``tests.fakeinput``).
def xim_raw_input(prompt=None):
    return raw_input(prompt)

def xim_getpass(prompt=None):
    return getpass(prompt)


## FIXME: would be nice to better format text (e.g. print errors in
## bold red).
class InputAware:
    """Mixin class which defines input-related methods."""
    _input = {}
    _input_info = ()
    _multiple_input = False


    def getInput(self, cl_input=None):
        """Get input from the user or from the command line argument
        if ``cl_input`` is not empty.

        The default handling of ``cl_input`` supposes that it is
        composed by a ';;'-separated list of ``key=value``
        pairs. E.g.::

            path=file.txt;;userid=bob

        will result in the following ``_input`` mapping::

            {'path': 'file.txt',
             'userid': 'bob'}

        Errors are not catched and will therefore raise exceptions.
        """
        if cl_input:
            for pair in cl_input.split(';;'):
                key, value = pair.split('=')
                self._input[key] = value
        else:
            if self._multiple_input:
                self._input = self.askForMultipleInput()
            else:
                self._input = self.askForInput()


    def getInputInfo(self):
        """Return a tuple of mappings which describes information
        needed by the collector.

        The mappings looks like::

            {'name': <string>,
             'prompt': <string>,
             'required': <boolean>,
             'default': <string>,
             'hidden': <boolean>,
             'validators': <sequence of strings or callables>,
            }

        where:

        - ``name`` is the name of the argument;

        - ``prompt`` is the string which will be displayed to the
          user;

        - ``required`` is an optional boolean which tells whether or
          not the user input is required. Default is ``False``;

        - ``default`` is a default value given to the argument if no
          value is given (though only if it is not reduired);

        - ``hidden`` is an optional boolean which tells whether the
          user input has to be hidden (e.g. for a password). Default
          is ``False``;

        - ``validators`` is an optional sequence of validators. Each
          validator may be either a string (which should be a method
          of the object calling ``getInput()``) or a callable (a
          function, a lambda expression, etc.)

        FIXME: we could also have a 'vocabulary' key which would:
        - enforce the value to be in a restricted set of values
        - provide completion feature
        """
        return self._input_info


    def askForInput(self, input_info=None):
        """Ask user for input, based on the needed informations which
        are in ``input_info`` or returned by ``getInputInfo()`` if the
        former is ``None``.

        **WARNING:** this method does **not** store the user input in
        the object. It only returns it.
        """

        def _validate(validators, value):
            """Run ``validators`` on ``value``."""
            for validator in validators:
                error = False
                if type(validator) == StringType:
                    validate = getattr(self, validator, None)
                    if validate is None:
                        error = True
                    elif not validate(value):
                        return False
                elif callable(validator):
                    if not validator(value):
                        return False
                if error:
                    logging.error('Could not infer what to do with '\
                                  'this validator: %s', validator)
            return True

        if input_info is None:
            input_info = self.getInputInfo()
        user_input = {}
        for info in input_info:
            while 1:
                ask = xim_raw_input
                if info.get('hidden'):
                    ask = xim_getpass
                value = ask(info['prompt'])
                if not value and not info.get('required') and \
                        info.get('default'):
                    value = info['default']
                if value or not info.get('required'):
                    if _validate(info.get('validators', ()), value):
                        user_input[info['name']] = value
                        break
        return user_input


    def askForMultipleInput(self):
        """Ask user for more than one input, until (s)he presses
         ``^C``.
        """
        user_input = []
        while True:
            try:
                user_input.append(self.askForInput())
            except KeyboardInterrupt:
                break
        return user_input
