##
## $Id$
##
##COPYRIGHT##

"""
Test the NetApp provisioner
"""

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error

from modipy.netapp import ZAPIProvisioner
from modipy.change_command import CommandChange, ExpectSet
from modipy.device import Device

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)

class TestZAPI(unittest.TestCase):

    def setUp(self):
        """
        Create the basic provisioning setup
        """
        self.prov = ZAPIProvisioner('test_zapi')
        device = Device('localhost')

        impl_xml = etree.Element('command')
        impl_expectset = ExpectSet(impl_xml)

        impl_expectset.commands = [
            ( None, 'echo hello' ),
            ( None, 'sleep 5; echo $?' ),
            ( None, 'fred' ),
            ( 'hell', 'echo found hello! hurray!'),
            ( 'hurr', None ),
            ]

        backout_xml = etree.Element('command')
        backout_expectset = ExpectSet(backout_xml)

        backout_expectset.commands = [
            ( None, 'echo "I am backing out"' ),
            ( None, 'sleep 5; echo $?' ),
            ( None, 'echo "backout successful!"' ),
            ]

        # FIXME: This doesn't actually run anything.
        self.change = CommandChange('ssh_test',
                                    devices=[device, ],
                                    impl=impl_expectset,
                                    backoutset_t=backout_expectset)

    def tearDown(self):
        pass

    def test_connection_failed(self):
        """
        Test handling of connection failure when attempting to contact a NetApp
        """
        d = self.prov.zapi_request(None, 'localhost', 'fail')
        self.failUnlessFailure(d, error.ConnectionRefusedError)
        return d
