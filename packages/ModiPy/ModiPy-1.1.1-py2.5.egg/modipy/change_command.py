#
# $Id$
#
# Command based changes. These are pairs with command based provisioners
#
from change import IChange, Change, NoCommands
from provisioner_command import ICommandProvisioner

from zope.interface import implements
from twisted.internet import defer, reactor
from twisted.python import log as tlog

import logging
import debug
log = logging.getLogger('modipy')

class ExpectSet:
    """
    A generic 'expect set' class.
    The basic expectset has 3 pieces:
    - A series of <command/>s, which consist of an optional <expect/>, (which
      defines a string to wait before before sending the paired <send/>)
      paired with a <send/> which defines the command to
      send to the remote device.
    - Zero or more <condition/>s, which define Python expressions that
      are evaluated against the namespace that results from running the
      expectset.
    - A <pause/>, which pauses execution pending user input (y/n)
    """
    known_children = [ 'command', 'condition', 'pause' ]
    
    def __init__(self, node):
        """
        Create an ExpectSet based on an XML node in the configuration.
        """
        self.commands = []
        self.conditions = []
        self.pause = False
        
        for child in node.xpath('*'):
            if child.tag not in self.known_children:
                raise ValueError("'%s' is an unknown child nodename of '%s'" % (child.tag, node.tag))
            else:
                if child.tag == 'command':
                    expect_tuple = self.parse_command(child)
                    self.commands.append(expect_tuple)

                elif child.tag == 'condition':
                    self.conditions.append( self.parse_condition(child) )

                elif child.tag == 'pause':
                    self.pause = True
                pass
            
            pass

        #log.debug("built expectset: %s", (self.commands, self.conditions, self.pause))

    def parse_command(self, element):
        """
        Parse a command element to extract the expect/send pairs.
        """
        if element.tag != 'command':
            raise ValueError("element is not a command node")

        # find the expect string, if it exists
        expectNodes = element.findall('expect')
        if len(expectNodes) == 1:
            expect_str = expectNodes[0].text

        elif len(expectNodes) > 1:
            log.error(">0 expectNodes found: %s", expectNodes)
            raise ValueError("More than one 'expect' tag found!")

        else:
            expect_str = None

        sendNodes = element.findall('send')
        if len(sendNodes) == 1:
            send_str = sendNodes[0].text

        elif len(sendNodes) > 1:
            log.error(">0 sendNodes found: %s", sendNodes)
            raise ValueError("More than one 'send' tag found!")

        else:
            send_str = None
            pass
        
        #log.debug("returning: %s, %s", expect_str, send_str)
        return (expect_str, send_str)

    def parse_condition(self, node):
        """
        Parse a condition node, and add it 
        """
        return node.text

class CommandChange(Change):
    """
    A CommandChange implements a change by using a supplied
    CommandProvisioner to execute the change by running a
    sequence of commands on the Provisioner target.

    There are several phases to change processing:
    * Pre-change checking. This phase runs checks to see if
      the change should even start.
    * Change implementation. This runs the actual change.
    * Post-change verification. This makes sure the change
      did what it was supposed to do.
    * Backout. This backs out the change if it fails to get
      implemented correctly, or if post-change verification fails.
    
    """
    implements( IChange, )

    provisioner_interface = ICommandProvisioner

    def run_expectset(self, provisioner, device, expectset, namespace):
        """
        Execute an expectset and verify it against the conditions, if any.
        """
        log.debug("running expectset: %s", expectset)

        if expectset is None:
            return defer.succeed(None)
        else:
            if expectset.pause:
                if self.nopause:
                    return defer.succeed(None)
                else:
                    log.info("Pausing...")
                    self.do_pause()
                    return defer.succeed(None)
            
            # If this change has an iterator, configure the iteration values
            # into the namespace and set up a callback chain to run the
            # commands in order.
            if getattr(self, 'iterator', None) is not None:
                log.debug("I am iterating some commands!")

                d = defer.succeed(None)
                
                for ns in self.iterator:
                    log.debug("Adding namespace entry of: %s", ns)

                    # Make sure we only update a copy, so that this
                    # update isn't permanent
                    newnamespace = ns.copy()
                    newnamespace.update(namespace)
                    log.debug("Namespace is now: %s", newnamespace)

                    d.addCallback(provisioner.run_commands, device, expectset, newnamespace)
                    d.addCallback(self.check_results, expectset.conditions, newnamespace)
                    pass

                return d

            else:
                d = provisioner.run_commands(None, device, expectset, namespace)
                d.addCallback(self.check_results, expectset.conditions, namespace)
                return d

    def _process_results(self, result, namespace):

        namespace['result'] = result

        return namespace

    def check_conditions(self, result, conditions, namespace):
        """
        A CommandChange has an additional check: if conditions
        is empty, it adds a check for the command exitcode.
        """
        if len(conditions) == 0:
            conditions = [ 'results.exitcode == 0', ]

        Change.check_conditions(self, result, conditions, namespace)

    def run_commands_failure(self, failure):
        """
        Called if the command fails utterly to run, such as with connection problems.
        """
        log.error("Command failure: %s: %s")
        return failure
        
    def pre_apply_check(self, provisioner, device, namespace):
        log.debug("running pre_apply_check")
        return self.run_expectset(provisioner, device, self.pre_impl, namespace)

    def apply(self, provisioner, device, namespace):
        """
        Use provisioner to implement me.
        """
        return self.run_expectset(provisioner, device, self.impl, namespace)
    
    def test_apply_success(self, provisioner, device, results, namespace):
        log.debug("testing success of change. results: %s", results)
        return self.run_expectset(provisioner, device, self.post_impl, namespace)

    def backout(self, provisioner, device, namespace):
        """
        Back out a change from a device.
        """
        log.debug("Running backout")
        if self.backoutset is None:
            return defer.fail(NoCommands('No backout commands. Cannot backout change.') )
        
        return self.run_expectset(provisioner, device, self.backoutset, namespace)

    def test_backout_success(self, results, provisioner, device, namespace):
        log.debug("testing success of backout. results: %s", results)
        return self.run_expectset(provisioner, device, self.post_backout, namespace)

    def parse_preimpl(self, node):
        """
        When passed a 'preimpl' node, parse it and add it to my commands.
        """
        self.pre_impl = self.create_expectset(node)

    def parse_impl(self, node):
        """
        When passed a 'impl' node, parse it and add it to my commands.
        """
        self.impl = self.create_expectset(node)

    def parse_postimpl(self, node):
        """
        When passed a 'postimpl' node, parse it and add it to my commands.
        """
        self.post_impl = self.create_expectset(node)

    def parse_prebackout(self, node):
        """
        When passed a 'prebackout' node, parse it and add it to my commands.
        """
        self.pre_backout = self.create_expectset(node)

    def parse_backout(self, node):
        """
        When passed a 'backout' node, parse it and add it to my commands.
        """
        self.backoutset = self.create_expectset(node)

    def parse_postbackout(self, node):
        """
        When passed a 'postbackout' node, parse it and add it to my commands.
        """
        self.post_backout = self.create_expectset(node)

    def create_expectset(self, node):
        return ExpectSet(node)
