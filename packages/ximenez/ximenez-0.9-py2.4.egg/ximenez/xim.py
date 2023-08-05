#!/usr/bin/env python
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

"""Main file for Ximenez.

$Id: xim.py 46 2008-01-19 17:07:27Z damien.baty $
"""

import sys
import time
import getopt
import socket
import logging

from ximenez.utils import getPluginInstance


USAGE = """\
Standard usage: %s -c <collector> -a <action>

-h, --help
  Display help and exit.

-v, --version
  Display version and exit.

-c <collector>
  Use <collector> plug-in.

--ci <input>
  Provide input to te collector plug-in.

-a <action>
  Use <action> plug-in.

--ai <input>
  Provide input to the action plug-in.

-o <output-file>, --outfile <output-file>
  Log to <output-file>.

See the documentation for further details.""" % sys.argv[0]

## Logging settings
LOGGING_LEVEL = logging.INFO
LOGGING_FORMAT = '%(asctime)s %(levelname)-8s %(message)s'
LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

## Global socket timout. Can be overriden by plug-ins, if needed.
DEFAULT_TIMEOUT = 3
socket.setdefaulttimeout(DEFAULT_TIMEOUT)

__version__ = '0.9'


def main():
    """Collect informations and execute action."""
    try:
        options, args = getopt.getopt(sys.argv[1:],
                                      'hva:c:o:',
                                      ['help', 'version',
                                       'output=',
                                       'ai=', 'ci='])
    except getopt.GetoptError:
        print USAGE
        sys.exit(1)

    action = None
    collector = None
    action_input = None
    collector_input = None
    output_path = None
    for option, value in options:
        if option == '-a':
            action = value
        elif option == '-c':
            collector = value
        elif option == '--ai':
            action_input = value
        elif option == '--ci':
            collector_input = value
        elif option in ('-o', '--output'):
            output_path = value
        elif option in ('-h', '--help'):
            print USAGE
            sys.exit(0)
        elif option in ('-v', '--version'):
            print __version__
            sys.exit(0)

    ## A collector and an action are both required.
    if not action or not collector:
        print 'Error: wrong arguments.'
        print USAGE
        sys.exit(1)

    ## Set logger settings
    log_settings = {'level': LOGGING_LEVEL,
                    'format': LOGGING_FORMAT,
                    'datefmt': LOGGING_DATE_FORMAT}
    if output_path is not None:
        log_settings['filename'] = output_path
    logging.basicConfig(**log_settings)

    ## Retrieve an instance of the collector plug-in.
    try:
        collector = getPluginInstance(collector, 'collectors')
    except ImportError:
        logging.critical('Could not import "%s" collector plug-in. '\
                         'Got the following exception:',
                         collector, exc_info=True)
        sys.exit(1)

    ## Retrieve an instance of the action plug-in.
    try:
        action = getPluginInstance(action, 'actions')        
    except ImportError:
        logging.critical('Could not import "%s" action plug-in. '\
                         'Got the following exception:',
                         action, exc_info=True)
        sys.exit(1)

    ## Do the job.
    start_time = time.time()
    logging.info("Started Ximenez session: '%s'." % ' '.join(sys.argv[1:]))
    collector.getInput(collector_input)
    sequence = collector.collect()
    logging.info('Collected %d items.' % len(sequence))
    action.getInput(action_input)
    action.execute(sequence)
    elapsed = time.time() - start_time
    logging.info('Executed action in %d seconds.' % elapsed)


if __name__ == "__main__":
    main()
