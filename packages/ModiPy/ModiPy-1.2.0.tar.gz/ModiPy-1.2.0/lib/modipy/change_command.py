#
# $Id$
#
# Command based changes. These are pairs with command based provisioners
#
from change import Change, NoCommands
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
    
    def __init__(self, node=None):
        """
        Create an ExpectSet based on an XML node in the configuration.
        """
        self.commands = []
        self.conditions = []
        self.pause = False

        # A marker to indicate that all expect processing has completed.
        self.complete = False

        if node is not None:
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

            # reverse the commands and conditions so we have a stack implementation
            self.commands.reverse()
            self.conditions.reverse()
            #log.debug("built expectset: %s", (self.commands, self.conditions, self.pause))
            pass

    def copy(self):
        """
        Return a copy of this expectset
        """
        newset = ExpectSet()
        newset.commands = self.commands[:]
        newset.conditions = self.conditions[:]
        newset.pause = self.pause
        newset.complete = self.complete

        return newset

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
            timeout = int(expectNodes[0].attrib.get('timeout', -1))

        elif len(expectNodes) > 1:
            log.error(">0 expectNodes found: %s", expectNodes)
            raise ValueError("More than one 'expect' tag found!")

        else:
            expect_str = None
            timeout = 10

        sendNodes = element.findall('send')
        if len(sendNodes) == 1:
            send_str = sendNodes[0].text
            # If the node is present, but empty, that's the
            # same as wanting to send a newline. We always send
            # a newline at the end of a command, so this is
            # just an empty string.
            if send_str is None:
                send_str = ''

        elif len(sendNodes) > 1:
            log.error(">0 sendNodes found: %s", sendNodes)
            raise ValueError("More than one 'send' tag found!")

        else:
            send_str = None
            pass
        
        #log.debug("returning: %s, %s", expect_str, send_str)
        return (expect_str, send_str, timeout)

    def parse_condition(self, node):
        """
        Parse a condition node, and add it 
        """
        return node.text

    def pop_command(self):
        """
        Implement the expectset commandstack
        """
        expr, cmdstring, timeout = self.commands.pop()
        return expr, cmdstring, timeout

    def push_command(self, expr, cmdstring, timeout):
        """
        Push the command tuple onto the stack
        """
        self.commands.append( (expr, cmdstring, timeout) )

    def has_commands(self):
        if len(self.commands) > 0:
            return True

class CommandChange(Change):
    """
    A CommandChange implements a change by using a supplied
    CommandProvisioner to execute the change by running a
    sequence of commands on the Provisioner target.
    """
    #implements( IChange, )

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
                pass
            
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
    
    def post_apply_check(self, results, provisioner, device, namespace):
        log.debug("checking change post-apply. results: %s", results)
        return self.run_expectset(provisioner, device, self.post_impl, namespace)

    def has_backout(self):
        """
        We can only back out if we have a backout set
        """
        if self.backoutset is not None:
            return True

    def pre_backout_check(self, provisioner, device, namespace):
        """
        Back out a change from a device.
        """
        log.debug("Running pre-backout check")
        return self.run_expectset(provisioner, device, self.pre_backout, namespace)
        
    def backout(self, results, provisioner, device, namespace):
        """
        Back out a change from a device.
        """
        log.debug("Running backout")
        if self.backoutset is None:
            return defer.fail(NoCommands('No backout commands. Cannot backout change.') )
        
        return self.run_expectset(provisioner, device, self.backoutset, namespace)

    def post_backout_check(self, results, provisioner, device, namespace):
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
