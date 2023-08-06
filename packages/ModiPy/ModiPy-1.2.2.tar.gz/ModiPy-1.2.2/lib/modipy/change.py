"""
A changeset is a sequence of changes that can be applied to a managed element.
A changeset will move the element from one state, A, to a destination state, B.
A changeset may contain other changesets. These changesets will be implemented
in a specific order.
The successful implementation of a changeset must be testable.
If the test fails, implementation of the changeset has failed, and a backout can
be executed.
A changeset contains the necessary backouts.

If a sub-changeset fails implementation, the containing changeset also fails.

Imagine the following changeset:

useradd justin

This adds a user to the system. If something goes wrong, how do we back out? 
Default backout behaviour is to alert a human that something went wrong.

Backout may depend on the exact failure. The 'did it work' test should permit
selecting from a list of possible backout procedures, depending on the failure
that was detected.

This example would be a "Add User" changeset, and could be different on different
destination systems.

Note that a "Remove User" changeset would be different from the backout procedure
for a failed "Add User" changeset.

For a changeset that runs a sequence of commands (a CommandChangeset, perhaps?),
the default behaviour should be to detect if an individual command in the sequence
failed, and report the error to the backout method detection code. This will
provide the most generic way of testing for failure without having to run a mini-audit
after each command is executed. However, if such paranoid auditing is required, you
could implement the changeset as a series of changesets, rather than a single,
multi-command changeset. This would provide much finer grained error detection and
possible correction capabilities.

A changeset is a set of changes to be applied to a set of devices.
A change can be applied to multiple devices, eg: loading the same configuration file onto all 70 hosts.
Does the 'load configuration file to host list' change happen all at once, or as part of a sequence
of changes? How do the changes inter-relate? Contrast "Change all 70 hosts, then do the next thing", to
"Change the first host, then do this other thing, then change the next host".

A Change is the minimum transaction size. This is the smallest element that can be applied,
or backed out. So, to implement the above scenarios, you could:

- Define a Change that should be applied to a device list. The provisioning method may be different
  (ssh vs rsh) but only to a certain degree. A ZAPI commandset is fundamentally different to an ssh/rsh
  commandset, for example.
- Define a Change that should be applied to a device list of length 1.
- Define the order that changes should occur in.

So.. first we define a list of devices and their attributes (ssh key locations, etc). This would be
a single, global area for all devices/entities under change management.

Then, we define a changeset, which is a list of changes. Each change defines the device(s) it applies to,
and how to apply the change to it.
"""
import logging
import debug

import re
import time
import datetime

log = logging.getLogger('modipy')

from zope.interface import Interface, implements
from twisted.internet import defer

from interfaces import IProvisioner
from base import XMLConfigurable
from namespace import create_namespace

CHANGE_STATE = {
    'success': 0,
    'pending': 1,
    'partial_failure': 2,
    'total_failure': 3,
    'backout_ok': 4,
    'backout_failed': 5,
    'retry': 6,

    # This state is used when a retry has been scheduled, but
    # has not yet been executed.
    'retry_pending': 7, 

    # Similar to success, but wasn't actually run.
    'skipped': 8,

    }

class UserBailout(Exception):
    """
    User denied a change command from executing in Authoritarian mode.
    This causes the program to bail out complete at exactly that point.
    """

class ChangeConditionFailure(Exception):
    """
    Raised if an expectset condition fails eval()
    """

class NoCommands(Exception):
    """
    Raised if there are no commands to run, and there should be
    """

class ChangeResult:
    """
    The result of running a change.
    """
    def __init__(self, results=None):
        """
        @param results: whatever is passed as the results from the Provisioner.
        """
        self.results = results

class Change(XMLConfigurable):
    """
    The base Change class.
    """

    # The Provisioner interface that this change requires in order to
    # be able to use the Provisioner. Changes and Provisioners are
    # coupled based on the kinds of actions the change requires its
    # provisioners to perform, and what results it expects the
    # provisioner to return
    provisioner_interface = IProvisioner

    optional_tags = [ 'preimpl',
                      'impl',
                      'postimpl',
                      'preapply',
                      'apply',
                      'postapply',
                      ]
    
    def __init__(self, name, devices=[],
                 pre_impl=None,
                 impl=None,
                 post_impl=None,
                 pre_backout=None,
                 backoutset=None,
                 post_backout=None,
                 pre_requisites=[],
                 serial_mode=True,
                 backout_all=False,
                 on_fail_continue=False,
                 on_fail_retry=False,
                 max_retries=3,
                 retry_delay=5,
                 nopause=False,
                 **kwargs):

        self._state = None
        self.name = name

        self.provisioner = None

        # must use a copy or weird things happen
        self.devices = devices[:]
        self.serial_mode = serial_mode
        self.backout_all = backout_all
        self.on_fail_continue = on_fail_continue
        self.on_fail_retry = on_fail_retry
        self.max_retries = max_retries
        self.retries = 0
        self.retry_delay = retry_delay
        self.pre_impl = pre_impl
        self.impl = impl
        self.post_impl = post_impl
        self.pre_backout = pre_backout
        self.backoutset = backoutset
        self.post_backout = post_backout
        self.pre_requisites = pre_requisites[:]

        self.nopause = nopause
        self.noop = False
        self.namespace = kwargs

        # Used for backout order tracking
        self.children = []
        
        self.state('pending')

        pass

    def __repr__(self):
        return '<%s: %s>' % ( self.__class__, self.name )

    def copy(self):
        """
        Create a copy of myself.
        """
        newchange = self.__class__('Copy of %s' % self.name,
                                   self.devices,
                                   self.pre_impl,
                                   self.impl,
                                   self.post_impl,
                                   self.pre_backout,
                                   self.backoutset,
                                   self.post_backout,
                                   self.pre_requisites,
                                   self.serial_mode,
                                   self.backout_all,
                                   self.on_fail_continue,
                                   self.on_fail_retry,
                                   self.retry_delay,
                                   self.max_retries,
                                   self.nopause,                                   
                                  )

        # set the namespace as a copy of mine
        if self.namespace is not None:
            newchange.namespace = self.namespace.copy()
            pass

        return newchange

    # Hide the internal state dictionary
    def state(self, value=None):
        if value is None:
            for key, value in CHANGE_STATE.items():
                if value == self._state:
                    return key
                pass
            # if we get this far, we've somehow gotten
            # into an invalid state!
            log.critical("Change entered invalid state somehow")
            raise ValueError("Invalid change state: %s", self._state)
            pass
        else:
            log.debug("setting change state to: %s", value)
            self._state = CHANGE_STATE[value]
        
    def do_pause(self):
        """
        Do a pause action.
        This waits for user input before continuing.
        """
        isok = raw_input("Continue? (y/n)[n]> ")
        if isok.startswith('y'):
            log.debug("Ok! Let's continue!")
        else:
            log.info("Bailing out at your command.")
            raise UserBailout("Bailing out at your command")

    def fetch_namespace(self, provisioner):
        """
        Build a unified namespace merging my namespace with the
        device, provisioner and global namespaces.
        """
        log.info("Fetching namespace...")
        namespace = self.namespace

    def can_retry(self):
        """
        Check to see if this change is allowed to retry after failing.
        """
        if self.on_fail_retry:
            log.debug("Onfail-retry is enabled")
            if self.max_retries < 0:
                log.debug("Change '%s' is set to retry forever.", self.name)
                return True

            elif self.retries < self.max_retries:
                log.debug("Retries: %d is less than retry max: %s. Will retry change.", self.retries, self.max_retries)
                self.retries += 1
                return True

            else:
                log.debug("Too many retries for change. Will not retry again.")
            pass
        return False

    def check_results(self, result, conditions, namespace={}):
        """
        Check namespace elements against a set of conditions.
        """
        namespace = self.process_results(result, namespace)

        self.check_conditions(result, conditions, namespace)

    def process_results(self, results, namespace):
        """
        Process the results and return a unified namespace, and
        potentially modified conditions.
        This function must be defined for every change type, as it
        depends on the results returned by the provisioner used for
        these kinds of changes.
        """
        namespace['results'] = results
        return namespace

    def check_conditions(self, result, conditions, namespace):
        """
        Check all the conditions against the results returned.
        """
        log.debug("condition checking result: %s against conditions: %s", result, conditions)
        log.debug("  with namespace: %s", namespace)
        if result is None:
            raise ValueError("command result is: None")

        # FIXME: It would be handy to be able to provide an error string
        # to print via log.error() if the condition fails.
        for cond in conditions:
            # perform a string substitution on the condition first
            cond = cond % namespace
            log.debug("checking condition: %s", cond)
            
            # Create a real dict out of what may be a Namespace object
            # Add some useful modules on top of any variables already in it.
            ns = {}
            ns['re'] = re
            ns['time'] = time
            ns['datetime'] = datetime
            ns.update(namespace)
            try:
                ok = eval( cond, ns, {} )
            except AttributeError, e:
                log.error("Attribute error on condition '%s': %s", cond, e)
                raise ChangeConditionFailure(e)

            if not ok:
                log.error("%s: condition failed: %s", self.name, cond)
                log.error("change result:\n%s", namespace['results'])
                raise ChangeConditionFailure("change failed condition check: %s" % cond)
            else:
                log.debug("condition check passed")

    def parse_namespace(self, node):
        """
        Parse a namespace child element of a change element
        """
        log.debug("Change has a namespace defined.")
        self.namespace = create_namespace(node)

    def parse_prereq(self, node):
        """
        This doesn't set up the relationship. That is handled
        later by the ConfLoader, because only it has the
        master list of all the changes, so this does nothing
        but allow the <prereq/> tag to be present within a
        <change/> definition.
        """
        # The only way for this method to work would be to provide
        # all changes with a reference to the config loader, which
        # is rather heavy handed, so we just let the confloader do
        # the work on our behalf.
        pass

    def pre_apply_check(self, provisioner, device, namespace):
        """
        Perform any pre-implementation checks you may need to perform
        before attempting to implement the change.
        """
        raise NotImplementedError
    
    def apply(self, provisioner, device, namespace):
        """
        Implement the change via the provisioner.

        @param provisioner: A L{Provisioner} instance that this change
        should be applied via.
        """
        raise NotImplementedError
    
    def post_apply_check(self, results, provisioner, device, namespace):
        """
        Test that the change was successfully implemented.
        @param result: Holds a result structure that was
        returned from the apply().

        @returns: True on success, False otherwise
        """
        raise NotImplementedError

    def pre_backout_check(self, provisioner, device, namespace):
        """
        Perform any pre-backout checks you may need to perform
        before attempting to backout the change.
        """
        raise NotImplementedError
    
    def backout(self, results, provisioner, device, namespace):
        """
        Back out this change via the provisioner.

        @param result: The result of a change apply() that failed.
        """
        raise NotImplementedError
    
    def post_backout_check(self, results, provisioner, device, namespace):
        """
        Test that the backout worked.

        @returns: True on success, False otherwise
        """
        raise NotImplementedError

    def has_backout(self):
        """
        See if the change has backout steps defined.

        @returns: True if backout steps exist, False otherwise
        """
        return False
    
    def add_prereq(self, change):
        """
        Add a change as a pre-requisite for this one.
        """
        # A pre-requesite is a parent node in a tree.
        # We also need to be able to find nodes that
        # have no children, so we want to track that
        # as well.
        if change in self.pre_requisites:
            raise ValueError("Change '%s' added as a pre-requisite to '%s' more than once." % (change, self))
        else:
            self.pre_requisites.append(change)
            pass
        change.add_child(self)

    def add_child(self, change):
        log.debug("Added %s as a child of %s", change, self)
        self.children.append(change)

    def has_children(self):
        """
        Does the change have children?
        """
        if len(self.children) > 0:
            return True
