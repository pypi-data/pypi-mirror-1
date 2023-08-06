"""
Provisioners contact remote devices and apply changes to them.

Should be implemented as a Protocol/Factory style thing to fit
with the async mechanism. A Provisioner is an interface applied
to a Factory that creates a, for example, ssh session with a
remote site.
"""
from zope.interface import Interface, implements

from twisted.internet import defer, reactor
from twisted.python import log as tlog
from twisted.internet.error import ProcessDone, ProcessTerminated, AlreadyCancelled, AlreadyCalled

from change import ChangeConditionFailure
from change import UserBailout, CHANGE_STATE

import logging
import traceback

import debug
log = logging.getLogger('modipy')

from twisted.internet.base import DelayedCall
DelayedCall.debug = True

class NoTargetsError(Exception):
    """
    Raised when a change is detected that has no targets
    and isn't in NOOP mode.
    """

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

class Provisioner:
    """
    A Provisioner performs the actual execution of Changesets. It could, for example,
    connect to a remote system via SSH and then execute the Changeset Actions.
    """

    implements( IProvisioner, )

    def __init__(self, name='', namespace={}, authoritarian=False, autobackout=False, **kwargs):
        self.name = name
        self.connectedDevice = None
        self.namespace = namespace
        self.authoritarian = authoritarian
        self.autobackout = autobackout

        self.change_ok = {}
        self.change_failed = {}
        self.backout_ok = {}
        self.backout_failed = {}

        self.delayed_retry = {}

    def parse_config_node(self, node):
        pass

    def perform_change(self, ignored, change, namespace={}, backout=False):
        """
        A wrapper around the internal _perform_change function, in
        order to enable a callLater functionality.
        """
        d = defer.Deferred()
        if change.state == CHANGE_STATE['retry']:
            change.state = CHANGE_STATE['retry_pending']
            log.info("Change '%s' scheduled to retry in '%d' seconds", change.name, change.retry_delay)
            reactor.callLater(change.retry_delay, self.perform_delayed_change, ignored, d, change, namespace, backout )
            pass
        
        else:
            log.debug("CHANGE WILL EXECUTE IMMEDIATELY")
            reactor.callLater(0, self.perform_delayed_change, ignored, d, change, namespace, backout )
            pass
        
        return d

    def perform_delayed_change(self, ignored, d, change, namespace, backout):
        """
        Calls back the deferred 'd' that is passed in, and immediately
        executes the change. This function is called after some sort of
        delay, usually via reactor.callLater()
        """
        # Set up the callback chain so that the results from the actual _perform_change
        # are passed to the deferred set up before the reactor.callLater().
        # This will fire the callback or errback for the deferred 'd' when
        # the processing has completed.
        newd = self.do_perform_change(ignored, change, namespace, backout)
        newd.chainDeferred(d)

    def do_perform_change(self, ignored, change, namespace={}, backout=False):
        """
        Perform a change on one or more (potentially) remote entities.

        @param namespace: The global namespace passed in to the provisioner.
               This gets merged with the provisioner, device and change namespaces.
        """
        #d = defer.succeed(None)        
        log.debug("perform change with namespace: %s", namespace)
        
        # get the list of devices the change should be applied to
        devices = change.devices
        
        # If this list is empty, the change has no targets, and
        # isn't in noop mode, it's a mistake. Die so the
        # user can fix this.

        if len(devices) == 0 and change.noop is False:
            d = defer.fail( NoTargetsError("No targets specified for change '%s', and it's not in NOOP mode." % change.name) )
            d.addErrback(self.change_failure, change, namespace)
            return d

        if change.serial_mode:

            # apply the change to each device one after the other,
            log.debug("change %s will be performed on devices: %s", change.name, devices)

            d = defer.succeed(None)
            for device in devices:
                d.addCallback(self.setup_device_change, device, change, namespace, backout=backout)
                pass
            d.addCallbacks(self.change_complete_success, self.change_failure, callbackArgs=(change, namespace), errbackArgs=(change, namespace) )
            #d.addCallback(self.change_complete_success, change, namespace)
            #d.addErrback(self.change_failure, change, namespace)
            return d
        
        else:
            # Apply changes to all devices at the same dependency
            # level all at once. This will be faster than serialised mode,
            # though with so much going on, it can be challenging to debug

            # Link all devices together in a DeferredList
            dlist = []
            for device in devices:
                d = self.setup_device_change(device, change, namespace, backout=backout)
                dlist.append(d)
                pass

            # Collect all the deferreds together so we only succeed if they
            # all succeed, and we fail if any of them fail.
            dl = defer.DeferredList(dlist, fireOnOneErrback=True)
            dl.addCallback(self.change_complete_success, change, namespace)
            dl.addErrback(self.change_failure, change, namespace)
            return dl

    def setup_device_namespace(self, device, change, namespace={}):
        """
        Set up a per device namespace for the change
        """
        namespace['provisioner.name'] = self.name
        namespace['provisioner.type'] = self.__class__.__name__

        namespace['change.name'] = change.name
        namespace['change.type'] = change.__class__.__name__

        namespace['device.name'] = device.name
        namespace['device.fqdn'] = device.fqdn
        namespace['device.ipaddress'] = device.get_ipaddress()

        log.debug("updating with my namespace")
        namespace.update(self.namespace)

        log.debug("updating with change namespace")
        namespace.update(change.namespace)

        log.debug("updating with device namespace")
        namespace.update(device.namespace)
        return namespace

    def setup_device_change(self, ignored, device, change, namespace, backout):
        """
        Do the change for the device
        """
        log.debug("performing change '%s' on device '%s'", change.name, device)
        namespace = self.setup_device_namespace(device, change, namespace)

        if backout:
            # Just do the backout portion
            #d.addCallback(self.backout_change, device, change, namespace)
            d = self.backout_change(None, device, change, namespace)
        else:
            log.debug("applying change with namespace: %s", namespace)
            
            #d.addCallback(self.apply_change, device, change, namespace)

            d = self.apply_change(None, device, change, namespace)
            pass

        # When the change is finished for the device, disconnect from it
        #d.addCallback(self.disconnect, device)
        #d.addErrback(self.disconnect, device)
        return d

    def apply_change(self, ignored, device, change, namespace={}):
        """
        Apply the change to a device
        """
        # connect to the entity that is having the change applied to it
        d = self.connect(device, namespace)
        d.addCallback(self.do_pre_apply_check, device, change, namespace)
        d.addCallbacks(self.pre_apply_success, self.pre_apply_failed, callbackArgs=(device, change, namespace), errbackArgs=(device, change, namespace))
        #d.addCallback(self.pre_apply_success, device, change, namespace)
        #d.addErrback(self.pre_apply_failed, change, namespace)
        return d

    def change_apply_success(self, result, device, change, namespace):
        """
        Change was applied successfully.
        """
        log.debug("change applied to device '%s' successfully." % device)
        log.debug("result: %s", result)
        # mark the device as having had the change applied to it
        self.change_ok[device] = change

        # do the post-change checking
        return change.test_apply_success(self, device, result, namespace)

    def change_apply_failed(self, failure, device, change, namespace):

        log.error("Change '%s' failed to apply: %s", change.name, failure.value)

        # If we want to bail out, bail now
        e = failure.check( UserBailout )
        if e:
            return defer.fail(failure)

        # If it's a ChangeCondition that failed, we can
        # do some other processing of it.
        e = failure.check( ChangeConditionFailure )
        if e:
            self.change_failed[device] = failure
            change.set_state('total_failure')
            log.error("Set change state to total failure")

            d = self.backout_change(None, device, change, namespace)

            if change.on_fail_continue:
                log.info("Attempting to continue, despite failure...")
                change.set_state('partial_failure')
                pass

            elif change.backout_all:
                for device in self.change_ok.keys():
                    d.addCallback( self.backout_change, device, change, namespace )

                    pass
                pass
            return d

        else:
            # Anything else is a fatal error, so pass the failure up
            return failure

    def change_failure(self, failure, change, namespace):
        log.debug("Change failure for '%s': %s", change.name, failure.value)
        if log.level == logging.DEBUG:
            tlog.err(failure)
        if change.state in [ CHANGE_STATE['pending'], CHANGE_STATE['retry'], CHANGE_STATE['retry_pending'] ]:
            # If the change is marked as 'on_fail: retry', let it retry
            if change.can_retry():
                change.state = CHANGE_STATE['retry']
            else:
                change.state = CHANGE_STATE['total_failure']

        elif change.state in [ CHANGE_STATE['backout_failed' ],
                               CHANGE_STATE['total_failure' ],
                               ]:
            pass
                               
        else:
            log.error("change_failure unhandled change state: %s", change.state)
            raise ValueError("Unhandled change state: %s" % change.state)

        # Propogate a UserBailout failure
        if failure.type == UserBailout:
            return failure
        
        #tlog.err(failure)

    def change_complete_success(self, result, change, namespace):
        if change.state in [ CHANGE_STATE['pending'], CHANGE_STATE['retry'], ] :
            change.state = CHANGE_STATE['success']
            log.info("Change '%s' was a success!", change.name)
            
        elif change.state == CHANGE_STATE['backout_ok']:
            log.debug("Backout successful.")

        else:
            log.info("change_complete_success in weird state: %s", change.state)
            pass
        

            
    def do_pre_apply_check(self, result, device, change, namespace):
        # perform pre-implementation checks
        log.info("Doing pre-apply check for change '%s' on device '%s'", change.name, device)
        return change.pre_apply_check(self, device, namespace)

    def pre_apply_success(self, result, device, change, namespace):
        log.info("Pre-apply check passed for change '%s' on device '%s'", change.name, device)
        d = self.do_apply(result, device, change, namespace)
        d.addCallback(self.change_apply_success, device, change, namespace)
        d.addErrback(self.change_apply_failed, device, change, namespace)
        return d

    def pre_apply_failed(self, failure, device, change, namespace):
        log.error("Pre-apply check failed for change '%s' on device '%s'", change.name, device)
        #tlog.err(failure)
        raise failure

    def do_apply(self, result, device, change, namespace):
        """
        Apply the actual change
        """
        log.info("Applying change '%s' to device '%s'", change.name, device)
        return change.apply(self, device, namespace)

    def backout_change(self, ignored, device, change, namespace):
        """
        Back out a change that was applied to a device.
        """
        # If auto-backout is not enabled, pause before attempting backout
        if not self.autobackout:
            log.info("About to back out change '%s'.", change.name)
            change.do_pause()
            
        log.info("Backing out change '%s' from device '%s'", change.name, device)
        d = change.backout(self, device, namespace)
        d.addCallback(change.test_backout_success, self, device, namespace)
        d.addCallback(self.backout_success, device, change, namespace)
        d.addErrback(self.backout_failure, device, change, namespace)
        return d

    def backout_success(self, ignored, device, change, namespace):
        log.info("Successfully backed out change: '%s' from device '%s'", change.name, device)
        change.state = CHANGE_STATE['backout_ok']
        self.backout_ok[device] = change

    def backout_failure(self, failure, device, change, namespace):
        log.critical("Backout of change '%s' failed for device '%s'!", change.name, device)
        change.state = CHANGE_STATE['backout_failed']
        self.backout_failed[device] = change
        #tlog.err(failure)
        return failure

    def connect(self, device, namespace):
        """
        The default Provisioner doesn't connect, as it assumes a connection
        will be made for each change step, perhaps for each substep within
        a change.
        If you only want to connect once for the entire change session,
        override this method in your subclass.
        """
        return defer.succeed(None)

    def disconnect(self, ignored, device):
        """
        The default Provisioner doesn't connect, so disconnect
        has no effect.
        """
        log.debug("disconnecting from %s" % device)
        return defer.succeed(None)

    def check_authoritarian(self):
        """
        If we're in authoritarian mode, wait for confirmation
        that we should execute the command.
        """
        if self.authoritarian:
            log.debug("Authoritarian mode. Waiting for ok to proceed...")
            isok = raw_input("Issue command (y/n)[n]?> ")
            if isok.startswith('y'):
                log.debug("Ok! Let's continue!")
            else:
                log.info(" Bailing out at your command.")
                raise UserBailout("Bailing out at your command")
                return
            pass
