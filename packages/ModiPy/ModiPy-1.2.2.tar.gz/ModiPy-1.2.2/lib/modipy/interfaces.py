#$Id: interfaces.py 98 2009-07-04 07:35:19Z daedalus $

"""
ModiPy interfaces
"""
from zope.interface import Interface, implements

import logging
import debug
log = logging.getLogger('modipy')


class IProvisioner(Interface):
    """
    Defines the Provisioner interface
    """

    def __init__(self, name='', namespace={}):
        """
        """

    def perform_change(self, ignored, change):
        """
        Applies a change to the devices the change is defined to affect.
        """

    def apply_change(self, device, change):
        """
        Apply a change to a specific device.
        """

    def backout_change(self, device, change):
        """
        Back out a change that was applied to a specific device.
        """

