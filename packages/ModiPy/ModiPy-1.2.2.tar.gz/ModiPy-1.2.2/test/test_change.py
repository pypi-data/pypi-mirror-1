##
## $Id: test_change.py 98 2009-07-04 07:35:19Z daedalus $
##
##COPYRIGHT##

"""
Test the base Change class
"""

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error

from modipy.options import ChangeOptions
from modipy.confloader import ConfigLoader, ChangeController
from modipy.change_command import CommandChange, ExpectSet
from modipy.provisioner import NoTargetsError
from modipy.provisioner_command import CommandProvisioner
from modipy.device import Device

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)

class TestChange(unittest.TestCase):

    def setUp(self):

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

    def test_change_notarget(self):
        """
        Verify that a change with no targets generates some sort of
        warning or failure.
        """
        # blank change with nothing much in it
        change = CommandChange('testing',
                               )
        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '--debug=%s' % logging._levelNames[log.level].lower() ])
        cfgldr = ConfigLoader()
        cfgldr.options = optparser.options

        cfgldr.changes[change.name] = change
        controller = ChangeController(cfgldr)

        d = controller.do_changes(None)
        return d

    def test_change_preimpl_fails(self):
        """
        Test a single change that fails preimpl.
        """
        # blank change with nothing much in it
        change = CommandChange('testing',
                               )
        def fail(change, provisioner, namespace):
            raise ValueError("Manual failure test.")

        change.pre_apply_check = fail
        
        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '--debug=%s' % logging._levelNames[log.level].lower() ])
        cfgldr = ConfigLoader()
        cfgldr.options = optparser.options

        cfgldr.changes[change.name] = change
        controller = ChangeController(cfgldr)

        d = controller.do_changes(None)
        return d
        

class TestConfigLoader(unittest.TestCase):
    """
    ConfigLoader specific tests.
    """

class TestChangeController(unittest.TestCase):

    def setUp(self):
        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '--debug=%s' % logging._levelNames[log.level].lower() ])
        self.cfgldr = ConfigLoader()
        self.cfgldr.options = optparser.options

        self.controller = ChangeController(self.cfgldr)

    def test_get_available_changes(self):
        """
        Fetch all available changes.
        """
        # blank change with nothing much in it
        change = CommandChange('testing',
                               )
        provisioner = CommandProvisioner('testprov')
        change.provisioner = provisioner
        self.cfgldr.changes[change.name] = change
        self.cfgldr.pending_changes.append(change)

        changes = self.cfgldr.get_available_changes()
        log.debug("changes are: %s", changes)

        self.failUnlessEqual( len(changes), 1)

    def test_no_target(self):
        """
        Test attempting to run a change with no targets
        """
        # blank change with nothing much in it
        change = CommandChange('testing')
        #change.noop = True
        provisioner = CommandProvisioner('testprov')
        change.provisioner = provisioner
        self.cfgldr.changes[change.name] = change
        self.cfgldr.pending_changes.append(change)

        d = change.provisioner.perform_change(None, change, self.cfgldr.global_namespace)

        # FIXME: Can't catch the failure for some reason?
        self.failUnlessFailure( d, NoTargetsError )
        return d

    def test_noop_change(self):
        """
        Test fetching changelist when only 1 exists
        """
        # blank change with nothing much in it
        change = CommandChange('testing')
        
        change.noop = True
        provisioner = CommandProvisioner('testprov')
        change.provisioner = provisioner
        self.cfgldr.changes[change.name] = change
        self.cfgldr.pending_changes.append(change)
        d = self.controller.do_changes(None)
        return d
