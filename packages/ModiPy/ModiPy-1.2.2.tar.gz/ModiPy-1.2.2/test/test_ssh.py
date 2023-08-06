##
##
##
## Test ssh provisioning

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error

from modipy.provisioner_ssh import SSHProvisioner
from modipy.change_command import CommandChange, ExpectSet
from modipy.device import Device

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)

class TestSSHProvision(unittest.TestCase):

    def setUp(self):
        """
        Create the basic provisioning setup
        """
        self.prov = SSHProvisioner()
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

    def test_list_users(self):
        raise unittest.SkipTest("SSH implementation still very alpha.")
        return self.prov.perform_change(None, self.change)
        pass
