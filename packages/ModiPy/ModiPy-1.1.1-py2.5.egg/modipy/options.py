# $Id$
#
#
# ModiPY is Copyright (c) Justin Warren 2007
# ModiPY is licensed under the LGPL. See the LICENSE file for details.
#
__revision__ = '$Revision: 1.61 $'

"""
Options used by commandline programs
"""
import os
import sys
import optparse
import socket

import logging
import debug
from twisted.python import log as tlog

log = logging.getLogger('modipy')

class BaseOptions(optparse.OptionParser):
    """
    Base options common to all programs.
    """
    def __init__(self, *args, **kwargs):
        """
        Initialise a base level options parser.
        """
        optparse.OptionParser.__init__(self, **kwargs)

        help_license = 'Display the license agreement and exit.'
        help_debug = "Set the output debug level to: debug, info, warn, error, or critical."
#        help_logfile = "Log to specified file instead of default logfile"
#        help_no_logfile = "Disable logging to logfile"
        
        self.add_option('', '--license',       dest='license', action='store_true', help=help_license)    
        self.add_option('', '--debug',         dest='debug', type='choice', choices=('debug', 'info', 'warn', 'error', 'critical'), metavar='LEVEL', default='info', help=help_debug)
#        self.add_option('', '--logfile',       dest='logfile', type='string', help=help_logfile)
#        self.add_option('', '--no-logfile',       dest='no-logfile', action='store_true', default=False, help=help_no_logfile)

        self.addOptions()

    def addOptions(self):
        """
        Override this method in subclasses to add more options.
        This enables multiple inheritence from the common base class.
        """
        pass
        
    def parseOptions(self, argv=sys.argv[1:]):
        """
        Emulate the twisted options parser API.
        """
        options, args = self.parse_args(argv)
        self.options = options
        self.args = args
        self.postOptions()

    def postOptions(self):
        """
        Perform post options parsing operations.
        """
        # Set standard logging level
        log.setLevel(logging._levelNames.get(self.options.debug.upper(), logging.INFO))
        if self.options.license:
            print license.long
            sys.exit(1)
            pass

class ChangeOptions(BaseOptions):
    """
    Options for change management.
    """

    def addOptions(self):
        help_authoritarian = "Authoritarian mode. Confirm every change command."
        help_configfile = "The configuration file to load"
        help_loadonly = "Load the configuration file and exit. Used to test parsing."
        help_backout = "Run only the backout portion of the changes."
        help_autobackout = "Enable automatic backout of failed changes."
        help_nopause = "Ignore any pauses in changes."
        
        self.add_option('-a', '--authoritarian',  dest='authoritarian', action='store_true', default=False, help=help_authoritarian)        
        self.add_option('-b', '--backout',  dest='backout', action='store_true', default=False, help=help_backout)        
        self.add_option('-c', '--configfile', dest='configfile', type='string', help=help_configfile)
        self.add_option('', '--autobackout', dest='autobackout', action='store_true', default=False, help=help_autobackout)
        self.add_option('', '--nopause', dest='nopause', action='store_true', default=False, help=help_nopause)
        self.add_option('', '--loadonly', dest='loadonly', action='store_true', default=False, help=help_loadonly)

    def check_values(self, options, args):
        """
        Post parsing checking of values.
        """
        if not options.configfile:
            self.error("Configuration file not specified.")
            pass

        return options, args
