# $Id: debug.py 98 2009-07-04 07:35:19Z daedalus $
#
##COPYRIGHT##

__version__ = '$Revision: 98 $'

import logging
import logging.handlers
import sys

#FORMAT = "%(asctime)s %(levelname)7s [%(thread)x] (%(module)s) %(message)s"
#FORMAT = "%(asctime)s %(levelno)2s (%(module)s) %(message)s"        
FORMAT = "%(asctime)s %(levelname)7s: %(message)s"
formatter = logging.Formatter(FORMAT, '%Y-%m-%d %H:%M:%S')

stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(formatter)

class LocalLogger(logging.Logger):
    
    def __init__(self, name):
        level = logging.INFO
        logging.Logger.__init__(self, name, level)
        self.addHandler(stdoutHandler)
        return
    pass

def add_file_handler(filename):
    handler = logging.handlers.RotatingFileHandler(filename=filename, maxBytes=10e6, backupCount=10)
    handler.setFormatter(formatter)
    log = logging.getLogger('modipy')
    log.addHandler(handler)
    
logging.setLoggerClass(LocalLogger)
