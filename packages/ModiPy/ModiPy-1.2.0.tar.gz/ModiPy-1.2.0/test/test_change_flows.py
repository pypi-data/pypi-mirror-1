##
## $Id$
##
##COPYRIGHT##

"""
Test the way change dependencies flow and interact.
"""

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error, defer

from modipy.options import ChangeOptions
from modipy.confloader import ConfigLoader, ChangeController
from modipy.provisioner import Provisioner
from modipy.change import Change
from modipy.device import Device

from test_provisioner import win, fail, changefail

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)

class DependencyTest(unittest.TestCase):
    """
    Test various types of change dependencies.
    """
    def setUp(self):

        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '--debug=%s' % logging._levelNames[log.level].lower() ])
        self.cfgldr = ConfigLoader()
        self.cfgldr.options = optparser.options
        self.controller = ChangeController(self.cfgldr)
        
        self.prov = Provisioner('testing', autobackout=True)
        self.device = Device('testdev')

        self.exec_order = []

    def change_ran(self, prov, device, ns, **kwargs):
        self.exec_order.append(ns['change.name'])
        return defer.succeed(None)

    def change_backed_out(self, results, prov, device, ns, **kwargs):
        self.exec_order.append(ns['change.name'])
        return defer.succeed(None)
    
    def add_success_funcs(self, change):
        """
        Add the functions required to make a change succeed
        its implementation, with the full swag of checks.
        """
        change.pre_apply_check = win
        change.apply = self.change_ran
        change.post_apply_check = win
        change.pre_backout_check = win
        change.backout = self.change_backed_out
        change.post_backout_check = win

    def add_fail_backout_ok_funcs(self, change):
        """
        Add the functions required to make a change fail
        its implementation, but back out ok.
        """
        change.pre_apply_check = win
        change.apply = changefail
        change.pre_backout_check = win
        change.backout = win
        change.post_backout_check = win

    def add_fail_backout_fail(self, change):
        """
        Add the functions required to make a change fail
        its implementation, and also fail backout
        """
        change.pre_apply_check = win
        change.apply = changefail
        change.pre_backout_check = win
        change.backout = changefail

    def add_change(self, changename, fail=False):
        """
        Add a change named 'changename' to the test
        setup. Return the change object.
        """
        change = Change(changename)
        change.devices.append( Device('localhost') )
        change.provisioner = self.prov
        self.cfgldr.changes[change.name] = change
        self.cfgldr.pending_changes.append(change)

        if fail is False:
            self.add_success_funcs(change)

        change.has_backout = lambda: True

        return change

class TestForwardsDependencies(DependencyTest):
    """
    Test various types of change dependencies when
    applied in standard 'forwards' mode.
    """

    def test_serial_1change_success(self):
        """
        1 change, no dependencies
        """
        change1 = self.add_change('change1')

        def finished(ignored):
            self.failUnlessEqual(self.exec_order, ['change1'])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

    def test_serial_2change_success(self):
        """
        2 changes, in order, both succeed
        """
        change1 = self.add_change('change1')
        change2 = self.add_change('change2')

        change2.add_prereq(change1)
        
        def finished(ignored):
            self.failUnlessEqual(self.exec_order, ['change1', 'change2'])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

    def test_serial_2change_reverse_success(self):
        """
        2 changes, in reverse order, both succeed
        """
        change1 = self.add_change('change1')
        change2 = self.add_change('change2')

        change1.add_prereq(change2)
        
        def finished(ignored):
            self.failUnlessEqual(self.exec_order, ['change2', 'change1'])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d
    
    def test_serial_4changes_success(self):
        """
        4 changes, in order, all succeed
        """
        change1 = self.add_change('change1')
        change2 = self.add_change('change2')
        change3 = self.add_change('change3')
        change4 = self.add_change('change4')
        
        change2.add_prereq(change1)
        change3.add_prereq(change2)
        change4.add_prereq(change3)
                
        def finished(ignored):
            self.failUnlessEqual(self.exec_order,
                                 ['change1',
                                  'change2',
                                  'change3',
                                  'change4',
                                  ])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

    def test_2_circular(self):
        """
        2 changes, with circular dependency, so impossible
        """
        change1 = self.add_change('change1')
        change2 = self.add_change('change2')

        change2.add_prereq(change1)
        change1.add_prereq(change2)
        
        def finished(ignored):
            self.failUnlessEqual(self.exec_order, [])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

    def test_4changes_2trees(self):
        """
        4 changes, in 2 parallel dependencies
        """
        change1 = self.add_change('change1')
        change2 = self.add_change('change2')
        change3 = self.add_change('change3')
        change4 = self.add_change('change4')
        
        change2.add_prereq(change1)
        change4.add_prereq(change3)
                
        def finished(ignored):
            self.failUnlessEqual(self.exec_order,
                                 ['change1',
                                  'change3',
                                  'change2',
                                  'change4',
                                  ])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

    def test_5changes_2trees(self):
        """
        5 changes, in 2 parallel dependencies after the 1st change
        """
        change1 = self.add_change('change1')
        change2 = self.add_change('change2')
        change3 = self.add_change('change3')
        change4 = self.add_change('change4')
        change5 = self.add_change('change5')

        # swap the order around a bit to make sure
        # we don't succeed by accident:
        #         ---change1---
        #        /             \
        #    change3         change5
        #       |               |
        #    change4         change2
        #
        # resulting in: change1, change3, change5, change2, change4
        # It isn't change2, change4 at the end, because
        # change2 was defined first, which is how the controller
        # searches for pending changes.

        change3.add_prereq(change1)
        change5.add_prereq(change1)
        change4.add_prereq(change3)
        change2.add_prereq(change5)
        
        def finished(ignored):
            self.failUnlessEqual(self.exec_order,
                                 ['change1',
                                  'change3',
                                  'change5',
                                  'change2',
                                  'change4',
                                  ])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

    def test_complex_tree(self):
        """
        Test a multi-branch tree
        """
        # A more complex tree structure:
        #
        #        begin
        #          |             
        #        branch1------        
        #          |          \       
        #       change1       change14
        #        /    \           \
        #   change7    change18   alan
        #     |            |       |
        #   change12    change41   |
        #      \        /      \   |
        #        meetup         fnord
        #          |            /
        #       ---+---        /
        #     /         \     /
        #   wibble      beatrice
        #

        begin = self.add_change('begin')
        branch1 = self.add_change('branch1')
        change1 = self.add_change('change1')
        change14 = self.add_change('change14')
        change7 = self.add_change('change7')
        change18 = self.add_change('change18')
        alan = self.add_change('alan')
        change12 = self.add_change('change12')
        change41 = self.add_change('change41')
        meetup = self.add_change('meetup')
        fnord = self.add_change('fnord')
        wibble = self.add_change('wibble')
        beatrice = self.add_change('beatrice')
        
        beatrice.add_prereq(fnord)
        beatrice.add_prereq(meetup)
        wibble.add_prereq(meetup)
        meetup.add_prereq(change12)
        meetup.add_prereq(change41)
        
        fnord.add_prereq(change41)
        fnord.add_prereq(alan)

        change12.add_prereq(change7)
        change41.add_prereq(change18)

        change7.add_prereq(change1)
        change18.add_prereq(change1)
        alan.add_prereq(change14)

        change1.add_prereq(branch1)
        change14.add_prereq(branch1)        

        branch1.add_prereq(begin)
        
        def finished(ignored):
            self.failUnlessEqual(self.exec_order,
                                 ['begin',
                                  'branch1',
                                  'change1',
                                  'change14',
                                  'change7',
                                  'change18',
                                  'alan',
                                  'change12',
                                  'change41',
                                  'meetup',
                                  'fnord',
                                  'wibble',
                                  'beatrice',
                                  ])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

class TestBackoutDependencies(DependencyTest):
    """
    Test various types of change dependencies when
    applied in standard 'backout' mode.
    """
    def setUp(self):

        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '-b', '--debug=%s' % logging._levelNames[log.level].lower() ])
        self.cfgldr = ConfigLoader()
        self.cfgldr.options = optparser.options
        self.controller = ChangeController(self.cfgldr)
        
        self.prov = Provisioner('testing', autobackout=True)
        self.device = Device('testdev')

        self.exec_order = []

    def test_serial_1change_backout(self):
        """
        1 change, no dependencies
        """
        change1 = self.add_change('change1')

        d = self.controller.do_changes(None)
        return d

    def test_serial_2change_backout(self):
        """
        2 changes, in order, both succeed
        """
        change1 = self.add_change('change1')
        change2 = self.add_change('change2')

        change2.add_prereq(change1)
        
        def finished(ignored):
            self.failUnlessEqual(self.exec_order, ['change2', 'change1'])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d

    def test_complex_tree_backout(self):
        """
        Test a multi-branch tree
        """
        # A more complex tree structure:
        #
        #        begin
        #          |             
        #        branch1------        
        #          |          \       
        #       change1       change14
        #        /    \           \
        #   change7    change18   alan
        #     |            |       |
        #   change12    change41   |
        #      \        /      \   |
        #        meetup         fnord
        #          |            /
        #       ---+---        /
        #     /         \     /
        #   wibble      beatrice
        #

        begin = self.add_change('begin')
        branch1 = self.add_change('branch1')
        change1 = self.add_change('change1')
        change14 = self.add_change('change14')
        change7 = self.add_change('change7')
        change18 = self.add_change('change18')
        alan = self.add_change('alan')
        change12 = self.add_change('change12')
        change41 = self.add_change('change41')
        meetup = self.add_change('meetup')
        fnord = self.add_change('fnord')
        wibble = self.add_change('wibble')
        beatrice = self.add_change('beatrice')
        
        beatrice.add_prereq(fnord)
        beatrice.add_prereq(meetup)
        wibble.add_prereq(meetup)
        meetup.add_prereq(change12)
        meetup.add_prereq(change41)
        
        fnord.add_prereq(change41)
        fnord.add_prereq(alan)

        change12.add_prereq(change7)
        change41.add_prereq(change18)

        change7.add_prereq(change1)
        change18.add_prereq(change1)
        alan.add_prereq(change14)

        change1.add_prereq(branch1)
        change14.add_prereq(branch1)        

        branch1.add_prereq(begin)
        
        def finished(ignored):
            self.failUnlessEqual(self.exec_order,
                                 [
                                  'wibble',
                                  'beatrice',
                                  'meetup',
                                  'fnord',
                                  'alan',
                                  'change12',
                                  'change41',
                                  'change14',
                                  'change7',
                                  'change18',
                                  'change1',
                                  'branch1',
                                  'begin',
                                  ])
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d
