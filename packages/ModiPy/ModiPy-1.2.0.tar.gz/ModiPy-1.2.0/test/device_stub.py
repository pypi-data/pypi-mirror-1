"""
A stub of the Device class, used for testing purposes.
"""
import logging


import re
import time
import datetime

from zope.interface import Interface, implements
from twisted.internet import defer

from modipy.device import Device

from modipy import debug
log = logging.getLogger('modipy')

class DeviceStub(Device):
    """
    A stubbed version of the actual change class,
    that strips out some of the complex code to
    test other classes.
    """
    def get_ipaddress(self):
        return ""
