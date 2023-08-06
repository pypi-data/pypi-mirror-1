##
## $Id: test_provisioner.py 98 2009-07-04 07:35:19Z daedalus $
##
##COPYRIGHT##

"""
Test base Provisioner class
"""

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error, defer

from modipy.device import Device
from modipy.provisioner import Provisioner
#from modipy.provisioner_command import CommandProvisioner
from modipy.change import Change, ChangeConditionFailure
from change_stub import ChangeStub

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)

class ChangeStubFail(Exception):
    """
    Raised when we force failure through a stub change.
    """

def win(*args, **kwargs):
    """
    A simple function that succeeds
    """
    log.debug("win!")
    return defer.succeed(None)

def fail(*args, **kwargs):
    """
    A simple function that fails
    """
    log.debug("fail!")
    return defer.fail( ChangeStubFail("FAIL") )

def changefail(*args, **kwargs):
    """
    Simulate a change condition failure
    """
    log.debug("changefail!")
    return defer.fail( ChangeConditionFailure("FAIL") )

class TestProvisionerBase(unittest.TestCase):

    def setUp(self):
        pass

    def test_instanciate(self):
        """
        Test creating a Provisioner
        """
        prov = Provisioner('testing')

    def test_instanciate_noname(self):
        """
        Test creating a Provisioner with no arguments
        """
        self.failUnlessRaises( TypeError, Provisioner )

    def test_instanciate_noname(self):
        """
        Test creating a Provisioner with no arguments
        """
        self.failUnlessRaises( TypeError, Provisioner )
        prov = Provisioner('testing')

class TestProvisioner(unittest.TestCase):        
    """
    Basic testing of provisioner functions and control flow.
    """
    def setUp(self):
        self.prov = Provisioner('testing', autobackout=True)
        self.device = Device('testdev')
        self.change = Change('blah')
        self.ns = {}
        pass

    #
    # Test just the apply phase
    #
    def test_pre_apply_success(self):
        """
        Test a change that will succeed its pre_apply_check
        """
        self.change.pre_apply_check = win
        self.prov.do_pre_apply_check(None, self.device, self.change, self.ns)

    def test_pre_apply_fail(self):
        """
        Test a change that will fail its pre_apply_check
        """
        self.change.pre_apply_check = fail
        d = self.prov.do_pre_apply_check(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)

    def test_pre_apply_changefail(self):
        """
        Fail pre_apply condition check 
        """
        self.change.pre_apply_check = changefail
        d = self.prov.do_pre_apply_check(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeConditionFailure)
        
    def test_apply_fail_pre_apply(self):
        """
        Fail apply_change at the pre_apply_check phase
        """
        self.change.pre_apply_check = fail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

    def test_apply_fail(self):
        """
        Fail apply_change at the apply phase
        """
        self.change.pre_apply_check = win
        self.change.apply = fail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

    def test_apply_win_post_apply_fail(self):
        """
        Fail apply_change at the apply phase
        """
        self.change.pre_apply_check = win
        self.change.apply = win
        self.change.post_apply_check = fail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

class TestProvisionerBackout(unittest.TestCase):

    def setUp(self):
        self.prov = Provisioner('testing', autobackout=True)
        self.device = Device('testdev')
        self.change = Change('blah')
        def has_backout():
            return True
        self.change.has_backout = has_backout

        self.ns = {}
        pass

    #
    # Test just the backout phase
    #
    def test_backout_success(self):
        """
        Test backout_change succeeds
        """
        self.change.pre_backout_check = win
        self.change.backout = win
        self.change.post_backout_check = win
        d = self.prov.backout_change(None, self.device, self.change, self.ns)
        return d

    def test_pre_backout_fail(self):
        """
        Test pre-backout fails
        """
        self.change.pre_backout_check = fail
        d = self.prov.backout_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

    def test_pre_backout_changefail(self):
        """
        Test pre-backout check fails condition check
        """
        self.change.pre_backout_check = changefail
        d = self.prov.backout_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeConditionFailure)
        return d

    def test_backout_fail(self):
        """
        Test backout_change fails
        """
        self.change.pre_backout_check = win
        self.change.backout = fail
        d = self.prov.backout_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d
    
    def test_backout_changefail(self):
        """
        Test backout_change fails condition check
        """
        self.change.pre_backout_check = win
        self.change.backout = changefail
        d = self.prov.backout_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeConditionFailure)
        return d

    def test_backout_post_fail(self):
        """
        Test backout_change fails in post-check
        """
        self.change.pre_backout_check = win
        self.change.backout = win
        self.change.post_backout_check = fail
        d = self.prov.backout_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

    def test_backout_post_fail(self):
        """
        Test backout_change fails condition check in post-check
        """
        self.change.pre_backout_check = win
        self.change.backout = win
        self.change.post_backout_check = changefail
        d = self.prov.backout_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeConditionFailure)
        return d

class TestProvisionerApplyBackout(unittest.TestCase):

    def setUp(self):
        self.prov = Provisioner('testing', autobackout=True)
        self.device = Device('testdev')
        self.change = Change('blah')
        def has_backout():
            return True
        self.change.has_backout = has_backout

        self.change.pre_apply_check = win
        self.change.apply = changefail
        #self.change.post_apply_check = win

        self.ns = {}
        pass

    #
    # Now do full apply_change testing through to backout
    #
    def test_pre_backout_fail(self):
        """
        Fail apply_change at pre-backout stage
        """
        self.change.pre_backout_check = fail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

    def test_pre_backout_changefail(self):
        """
        Fail apply_change at pre-backout condition check
        """
        self.change.pre_backout_check = changefail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeConditionFailure)
        return d

    def test_backout_fail(self):
        """
        Fail apply_change at backout stage
        """
        self.change.pre_backout_check = win
        self.change.backout = fail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

    def test_backout_changefail(self):
        """
        Fail apply_change at backout condition check
        """
        self.change.pre_backout_check = win
        self.change.backout = changefail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeConditionFailure)
        return d

    def test_post_backout_fail(self):
        """
        Fail apply_change at post-backout stage
        """
        self.change.pre_backout_check = win
        self.change.backout = win
        self.change.post_backout_check = fail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeStubFail)
        return d

    def test_post_backout_changefail(self):
        """
        Fail apply_change at post-backout condition check
        """
        self.change.pre_backout_check = win
        self.change.backout = win
        self.change.post_backout_check = changefail
        d = self.prov.apply_change(None, self.device, self.change, self.ns)
        self.failUnlessFailure(d, ChangeConditionFailure)
        return d
