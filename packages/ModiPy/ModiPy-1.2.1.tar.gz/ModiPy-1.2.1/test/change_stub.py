"""
A stub of the Change class, used for testing purposes.
"""
import logging


import re
import time
import datetime

from zope.interface import Interface, implements
from twisted.internet import defer

from modipy.namespace import create_namespace
from modipy.change import Change

from modipy import debug
log = logging.getLogger('modipy')

class ChangeStub(Change):
    """
    A stubbed version of the actual change class,
    that strips out some of the complex code to
    test other classes.
    """
