#
# $Id: provisioner_command.py 98 2009-07-04 07:35:19Z daedalus $
#
##COPYRIGHT##

"""
Command based provisioning, which breaks out into a shell in order
to run a command-line that will somehow connect to a remote device
and allow shell style commands to be run on it.
"""

import re

from zope.interface import Interface, implements
from twisted.internet import defer, reactor
from twisted.internet import protocol
from twisted.internet.error import ProcessDone, ProcessTerminated, AlreadyCancelled, AlreadyCalled

import util

from provisioner import IProvisioner, Provisioner
from change import ChangeResult, UserBailout

import logging
import debug
log = logging.getLogger('modipy')

class ICommandProvisioner(IProvisioner):
    """
    The interface that all CommandChange compatible Provisioners must implement
    """
    
    def run_commands(self, status, device, expectset, namespace):
        """
        Run a series of commands, provided as an expectset.
        This will be called from a Deferred, which will supply 'status',
        which may be ignored.
        A namespace containing a dictionary of useful values will
        also be provided, which can be added to as required. This is used,
        for example, in Condition processing.
        """
        pass

class CommandProvisioner(Provisioner):
    """
    A command provisioner provides methods for implementing command changes on
    remote devices.
    """
    implements(ICommandProvisioner)
    
    command_re = re.compile(r'^(?P<start>.*)["\'](?P<quoted>.*)["\'](?P<end>.*)$')

    def parse_config_node(self, node):
        Provisioner.parse_config_node(self, node)
        pass

    def __init__(self, name, namespace={},
                 authoritarian=False, autobackout=False,
                 sessionlog=None,
                 command_timeout=300):
        Provisioner.__init__(self, name, namespace,
                             authoritarian=authoritarian,
                             autobackout=autobackout,
                             sessionlog=sessionlog)
        self.command_timeout = int(command_timeout)

    def split_command(self, cmdstring):
        """
        Split a command string, returning everything before
        a quoted section, the quoted section, and then everything
        afterwards.
        """
        cmd_split = []
        m = self.command_re.match(cmdstring)
        if m:
            cmd_split.append( m.group('quoted') )
            cmd_split.extend(m.group('end').split())

            splitpart = self.split_command(m.group('start'))
            splitpart.extend(cmd_split)
            cmd_split = splitpart
            return cmd_split

        return cmdstring.split()

    def run_commands(self, ignored, device, expectset, namespace):
        """
        Execute an expectset of commands on the device, returning the results of the command.

        @returns: (return_code, results) where
          return_code: is the exit code of the command, as an integer
          results: is a string containing anything printed to the subprocess
        """
        log.debug("Executing expectset: %s" % expectset)
        return defer.succeed( CommandChangeResult((0, '')) )

class CommandChangeResult(ChangeResult):

    def __init__(self, result=None):
        ChangeResult.__init__(self, result)

        self.exitcode = result[0]
        self.cmdoutput = result[1]

    def __str__(self):
        return "%s: %s" % (self.exitcode, self.cmdoutput)

    def __repr__(self):
        return "%s: exitcode: %s" % (self.__class__.__name__, self.exitcode)

    
class ConnectingProvisioner(CommandProvisioner):
    """
    A ConnectingProvisioner runs a command to connect to the remote device
    and then runs a series of commands by sending them to the remote
    device via STDIN, and receives the output from STDOUT and STDERR.
    """
    required_tags = CommandProvisioner.required_tags + [ 'connect_command', ]
    optional_tags = CommandProvisioner.optional_tags + []

    def parse_config_node(self, node):
        """
        Deals with additional configuration that I may be provided with.
        """
        CommandProvisioner.parse_config_node(self, node)
        # parse command definition
        if node.tag == 'connect_command':
            self.conn_cmd = str(node.text)
            log.debug("Set provisioner connecting command to: %s", self.conn_cmd)

    def connect(self, device, namespace):
        self.connectedDevice = device
        
        self.connecting_d = defer.Deferred()
        self.connection_timeout_d = reactor.callLater(5, self.connection_timeout, device)

        log.debug("connecting to device '%s'", device)

        # Do variable substitution on the connect command
        cmdstring = str(util.substituteVariables(self.conn_cmd, namespace))
        cmd = self.split_command(cmdstring)
        
#         cmd = [ '/usr/bin/ssh',
#                 '-T',
#                 '-o','BatchMode=yes',
#                 '-i','/home/daedalus/.ssh/localconnect',
#                 'localhost' ]
        self.ep = ExpectProtocol(self, self.sessionlog)
        log.debug("spawning process: %s", cmd)
        self.p = reactor.spawnProcess(self.ep, cmd[0], cmd, usePTY=True )

        return self.connecting_d

    def connection_timeout(self, device):
        """
        This gets called if my connection via the child process doesn't
        complete within a certain timeout value.
        """
        log.error("Connection to child timed out!")
        self.ep.transport.loseConnection()
        self.connecting_d.errback( Exception("Connection to '%s' timed out" % device.name) )

    def connection_success(self):
        """
        This gets called by the child when it finishes connecting.
        Cancel the timeout and notify waiting things that the connection
        completed successfully.
        """
        log.debug("successfully connected to child")
        self.connection_timeout_d.cancel()
        log.debug("sent timeout cancel")
        self.connecting_d.callback(self)

    def childConnectFailure(self):
        """
        This gets called when the connection fails
        """
        log.error("connection by child failed")
        #self.connection_timeout_d.cancel()
        self.connecting_d.errback(ValueError("Child connection failure!"))

    def childCommandFailure(self, error):
        """
        Called when the child command fails for some reason that
        is probably related to the command used for connecting.
        """
        self.connecting_d.errback(error)        

    def run_commands(self, ignored, device, expectset, namespace, delay=0):
        """
        Delay is optional. Used to run the command after a delay.
        """
        log.debug('running commands on remote host: %s' % expectset)

        # Check to see if I'm connected. If not, connect first.
        if getattr(self, 'ep', None) is None:
            def connected(ignored, d):
                log.info("unconnected delayed command")
                reactor.callLater(delay, self.run_delayed_command, d, expectset, namespace)
                #return self.ep.run_remote_commands(expectset, namespace)
            d = self.connect(device, namespace)
            d.addCallback(connected, d)
            return d

        else:
            d = defer.Deferred()
            log.info("connected delayed command")
            reactor.callLater(delay, self.run_delayed_command, d, expectset, namespace)
            #return self.ep.run_remote_commands(expectset, namespace)
            return d

        # Run the command using the ExpectProtocol
        #return defer.succeed( (0, '', '') )

    def run_delayed_command(self, d, expectset, namespace):
        """
        Runs a possibly delayed command, and chains the callbacks
        to the original Deferred.
        """
        newd = self.ep.run_remote_commands(expectset, namespace)
        newd.chainDeferred(d)
        
    def disconnect(self, ignored, device):
        """
        Called when the provisioner is no longer required.
        """
        self.ep.transport.loseConnection()

    def all_commands_failure(self, failure, deferred_key, namespace):
        """
        Some kind of failure in the commands occurred.
        """
        errorstr = "%s: %s" % (namespace['exitcode'], namespace['command.output'])
        log.error("Command failed: %s", errorstr)
        self.all_commands_defer[deferred_key].errback( failure )

    def change_failure(self, failure, change, namespace):
        """
        Override base class in order to disconnect when the change is
        finished.
        """
        # disconnect from the remote device
        if getattr(self, 'ep', None) is not None:
            self.ep.transport.loseConnection()
        Provisioner.change_failure(self, failure, change, namespace)

    def change_complete_success(self, result, change, namespace):
        # disconnect from the remote device
        self.ep.transport.loseConnection()
        Provisioner.change_complete_success(self, result, change, namespace)
    
class ExpectProtocol(protocol.Protocol):
    """
    The ExpectProtocol allows you to supply a series of
    expect/send pairs that will be used to handle the
    processing of received data.

    Each expect/send pair is a tuple of the form:
    (expect_re, send_string), where:

    expect_re: is a regular expression that will be used
    by the re module to parse received data. Each time
    dataReceived() is triggered, the data is added to a
    buffer, which is matched against the re. If a match is
    successful, the corresponding send_dict is processed to
    generate the data to send in response, and the receive
    buffer is emptied.
    If a match is unsuccessful, execution returns to wait
    for more data.

    send_string: is a series of octets to send in response
    to the expect string that was received. % operator replacement
    is possible using %(name)s syntax, with the (name) values
    being populated from the previous expect re.match operation.
    """

    def __init__(self, provisioner, sessionlog):
        
        self.parent = provisioner
        self.sessionlog = sessionlog
        self.saidHello = False
        self.waitingForCommand = None
        self.databuf = ''
        self.data_wait_timeout = None

        self.cmdoutput = ''
        self.expectset = None
        # Commands are assumed to succeed unless the expect string
        # cannot be found.
        self.exitcode = 0

    def connectionMade(self):
        """
        Called when the connection to the remote entity is
        made, whatever it is.
        """
        log.debug("Connected to remote thing! Hurray!")
        self.parent.connection_success()

    def childConnectionLost(self, fd):
        log.debug("Lost connection to child process fd %s" % fd)

    def childDataReceived(self, fd, data):
        log.debug("received data from child process %s: >%s<" % (fd, data) )

        self.got_data(data)
        # ignore stuff from STDERR?
        #if fd == 2:
        #    pass

    def outReceived(self, data):
        """
        Alternate version of childDataReceived() for PTYProcess, rather
        than something that allows full control of child file descriptors.
        """
        self.got_data(data)
        
    def got_data(self, data):
        """
        Generic function used when data is received from the child process,
        whatever kind of subprocess it is.
        """
        #log.debug("data: %s" % data)
        self.databuf += data
        if self.sessionlog is not None:
            self.sessionlog.write(data)
            self.sessionlog.flush()            
            pass
        #log.debug("databuf: >%s<" % self.databuf)
        self.do_expect_processing()

#         # force any unexpected errors to call the errback
#         except Exception, e:
#             try:
#                 log.error("Exception in childDataReceived(): %s: %s", e.__class__, e)
#                 self.waitingForCommand.errback(e)
#             except defer.AlreadyCalledError:
#                 pass
            
    def processEnded(self, status_object):
        log.debug("process ended: %s" % status_object)

        if isinstance(status_object.value, ProcessDone):
            log.debug("process exited ok")
            self.exitcode = 0

        elif isinstance(status_object.value, ProcessTerminated):
            errmsg = "process did not exit ok: %s" % status_object.value.exitCode
            log.debug(errmsg)
            self.exitcode = status_object.value.exitCode
            #self.parent.childCommandFailure(ValueError(errmsg))

    def connectionFinished(self, status):
        self.parent.childConnected()

    def processExited(self, reason):
        pass

    def run_remote_commands(self, expectset, namespace):
        """
        Run a set of commands, using expect processing to do it.
        """
        self.namespace = namespace
        
        log.debug("running remote commands: %s", expectset)
        self.expectset = expectset.copy()
        self.waitingForCommand = defer.Deferred()
        self.do_expect_processing()
        return self.waitingForCommand

    def do_expect_processing(self):

        if self.expectset is None:
            return

        #log.debug("doing expect processing: %s", self.expectset.commands)
        # loop over the commands, breaking out if we need to
        while 1:
            try:
                log.debug("fetching next expectset tuple...")
                expr, cmdstring, timeout = self.expectset.pop_command()
                if timeout == -1:
                    timeout = self.parent.command_timeout

                log.debug("Seeking: %s", expr)

            except IndexError:
                log.debug("No more commands to run.")
                self.cmdoutput += self.databuf
                self.databuf = ''

                # This can sometime happen when extra, spurious data is
                # received after we've finished what we wanted to do.
                # We just ignore that.
                try:
                    self.waitingForCommand.callback( CommandChangeResult((self.exitcode, self.cmdoutput)))
                except defer.AlreadyCalledError:
                    pass

                # All done, so exit out of the loop
                return
            # See if we need to wait for an expression
            if expr is None:
                self.process_command(cmdstring)
            else:
                # There is an expression, so process it.
                expr = str(util.substituteVariables(expr, self.namespace))
                if not self.find_expect(expr, cmdstring, timeout):
                    break

    def process_command(self, cmdstring):
        """
        Process the command associated with an expect.
        """
        if cmdstring is None:
            log.debug("no command. nothing to do")
            # No command, so nothing to do.
            pass
        else:
            try:
                cmdstring = str(util.substituteVariables(cmdstring, self.namespace))
                log.debug("No expression to wait for. Running command '%s' immediately." % cmdstring)
            except Exception, e:
                self.waitingForCommand.errback(e)
            self.issue_command(cmdstring)
            
    def find_expect(self, expr, cmdstring, timeout):
        """
        See if we can find the expect expression.
        """
        #log.debug("checking for '%s' in databuf[len %d]: %s", expr, len(self.databuf), self.databuf)
        if len(self.databuf) == 0:
            # No data yet, so wait
            self.wait_for_expect(expr, cmdstring, timeout)
            return False

        # Match in multi-line mode, and '.' character matches \n
        re_expr = re.compile(expr)
        match = re_expr.search(self.databuf)
        log.debug("match object is: %s", match)
        if match:
            # check the current recv buffer to see if the expect string is a match
            log.debug("Found expr '%s' in databuf! Yay!" % expr)

            if getattr(self, 'data_wait_timeout', None) is not None:
                log.debug("Found expected string. cancelling timeout.")
                self.data_wait_timeout.cancel()
                del self.data_wait_timeout
                pass

            # reset the databuffer whenever we match something to everything
            # that comes after the matched part.
            log.debug("Match end is at: %d", match.end())
            self.cmdoutput += self.databuf[:match.end()]
            self.databuf = self.databuf[match.end():]

            self.process_command(cmdstring)

            # We found something, so let caller know
            return True

        # The expression wasn't found, so we put the command back on the
        # stack and wait for more data to trigger this processing again.
        else:
            self.wait_for_expect(expr, cmdstring, timeout)
            return False

    def wait_for_expect(self, expr, cmdstring, timeout):
        """
        Can't find the expect expression yet, so wait for it
        until a timeout.
        """
        log.debug("cannot find '%s' in databuf. Waiting for more data..." % expr)
        self.expectset.push_command(expr, cmdstring, timeout)

        # Set a timeout. If the timeout value is 0, disable the timeout.
        if timeout > 0:
            if getattr(self, 'data_wait_timeout', None) is None:
                log.debug("Setting timeout value to: %d", timeout)
                self.data_wait_timeout = reactor.callLater(timeout, self.data_wait_too_long)
            pass
            
    def issue_command(self, cmdstring):
        """
        Write the command to the remote device.
        """
        self.parent.check_authoritarian()
        
        log.debug("running command: %s" % cmdstring)
        self.transport.writeSomeData('%s\n' % cmdstring)
        # This may well get recorded anyway if the session echos
#         if self.sessionlog is not None:
#             self.sessionlog.write('%s\n' % cmdstring)
#             self.sessionlog.flush()
    def data_wait_too_long(self):
        """
        We have waited for data for too long, so return an error
        """
        self.waitingForCommand.errback( ValueError("Timed out waiting for expect string.") )

class MultiConnectingProvisioner(ConnectingProvisioner):
    """
    A provisioner that runs a command that sets up the connection to
    the remote device for each and every command that needs to be run.
    The command to be run is appended to the connecting command.
    It is designed to be run with something like ssh, eg:
    ssh remotehost <command1>
    ssh remotehost <command2>
    """

    def __init__(self, name='', namespace={}, authoritarian=False, autobackout=False, command_timeout=300):

        ConnectingProvisioner.__init__(self, name, namespace, authoritarian, autobackout, command_timeout)
        # Set up a deferred dictionary, keyed to uniquely identify a set
        # of commands (ExpectSet) running on given device
        self.all_commands_defer = {}

    def parse_config_node(self, node):
        """
        Deals with additional configuration that I expect to be provided with.
        """
        ConnectingProvisioner.parse_config_node(self, node)
        # parse command definition
        if node.tag == 'command':
            self.command = str(node.text)
            log.debug("Set provisioner command to: %s", self.command)

    def connect(self, device, namespace):
        """
        Don't actually connect, but take note of the device.
        """
        self.device = device
        self.p = None
        self.ep = None
        # perform variable substitution on the command

##         self.cmd = [ '/usr/bin/ssh',
##                      '-T',
##                      '-o', 'BatchMode=yes',
##                      '-i','/home/daedalus/.ssh/localconnect',
##                      ]
##        self.cmd.append('%s' % str(device))

        #log.debug("Set up command to run: %s", self.cmd)
        log.debug("Provisioner ready for device: %s", device)
        return defer.succeed(None)
    
    def run_commands(self, ignored, device, expectset, namespace):
        """
        Run each command, one after the other.
        """
        log.debug("inside provisioner running expectset: %s" % expectset)
        self.cmdoutput = ''
        self.exitcode = None

        # Set up a sequential chain of commands, specific to this combination of
        # device and expectset.
        # This is important because it allows a single Provisioner object to
        # be simultaneously running multiple Changes that are not dependent on
        # one another without accidentally calling back the wrong Deferred.
        deferred_key = (device, expectset)
        self.all_commands_defer[deferred_key] = defer.Deferred()

        d = defer.succeed(None)
        for (expr, cmdstring, timeout) in expectset.commands:

            try:
                # Perform variable substitution on the command string
                log.debug("determining commandstring from template: %s", cmdstring)
                cmdstring = str(util.substituteVariables(cmdstring, namespace))
                log.debug("commandstring is: %s", cmdstring)

                # add the cmdstring to the namespace
                namespace['command.send'] = cmdstring

                log.debug("Determining command base from template: %s", self.command)
                command = str(util.substituteVariables(self.command, namespace))

            except KeyError, e:
                log.error("KeyError in commands: %s" % e)
                self.all_commands_defer.errback( e )
                return self.all_commands_defer[deferred_key]
            
            #log.debug("checking expr: %s" % expr)
            log.debug("cmdstring is: %s" % command)
            if command is not None:
                log.debug("splitting command: %s", command)
                cmd = self.split_command(command)
                log.debug("command is: %s", cmd)
                # FIXME: The next command in the list should only get
                # added to the chain if the previous one succeeds.
                d.addCallback(self.spawn_command, cmd, self.command_timeout)
                d.addCallbacks(self.command_completed, self.command_failed, callbackArgs=(namespace,), errbackArgs=(namespace,))
                pass
            pass

        d.addCallbacks(self.all_commands_done, self.all_commands_failure, callbackArgs=(deferred_key, namespace,), errbackArgs=(deferred_key, namespace,))
        return self.all_commands_defer[deferred_key]

    def spawn_command(self, ignored, cmd, timeout=300):
        """
        Run the command in a sub-process, returning a deferred that
        will fire based on the results.
        """
        log.debug("spawning command...")
        self.waitingForCommand = defer.Deferred()

        self.check_authoritarian()
        log.debug("running command remotely: %s" % cmd)

        # FIXME: This is using a shared resource. May clobber things when
        # running in non-sequential mode!
        self.ep = SingleCommandProtocol(self, timeout)
        self.p = reactor.spawnProcess(self.ep, cmd[0], cmd)
        log.debug("Spawned process: %s", self.p)

        return self.waitingForCommand

    def command_completed(self, result, namespace):
        """
        When the command is completed, add its output to a
        global resultset. This sets the exitcode to the
        exitcode of the last command that completed, and
        """
        log.debug("a command has completed with result: %s", result)

        self.exitcode = result[0]
        self.cmdoutput += result[1]
        log.debug("current results: exit '%d', output: %s", self.exitcode, self.cmdoutput)
        
    def command_failed(self, failure, namespace):
        """
        If a command failed, pass the failure up the Deferred chain.
        Don't consume the error.
        FIXME: This should probably be a deferred list or similar.
        """
        # Don't log here, or the same error will log once for
        # every command in the chain. This is sortof recurive due
        # to the way the deferred are chained together above in
        # the d.addCallback(self.spawn_command) setup
        
        #self.all_commands_defer.errback( Exception(errorstr) )
        return failure
    
    def all_commands_done(self, result, deferred_key, namespace):
        """
        Called when all the commands have completed.
        """
        log.debug("All commands have finished.")
        
        self.all_commands_defer[deferred_key].callback( CommandChangeResult( (self.exitcode, self.cmdoutput) ) )
        
    def all_commands_failure(self, failure, deferred_key, namespace):
        """
        Some kind of failure in the commands occurred.
        """
        errorstr = "%s: %s" % (self.exitcode, self.cmdoutput)
        log.error("Command failed: %s", errorstr)
        log.error("process is: %s", self.p)
        log.error("eprocess is: %s", self.ep)
        self.all_commands_defer[deferred_key].errback( failure )

class CommandFailure(Exception):
    """
    Used to contain sub-process errors.
    """

class SingleCommandProtocol(protocol.Protocol):
    """
    Used to run a single command in a sub-process.
    """
    
    def __init__(self, provisioner, timeout_after=300):

        self.parent = provisioner
        self.databuf = ''
        self.exitCode = None
        self.timeout_after = timeout_after

    def connectionMade(self):
        #log.debug("Pretend connection made! Hurray!")

        # FIXME: provide a way to set this via the config file
        self.timeout = reactor.callLater(self.timeout_after, self.timedOut)
        pass
    
    def childConnectionLost(self, fd):
        #log.debug("Lost connection to child process fd %s" % fd)
        pass

    def childDataReceived(self, fd, data):
        #log.debug("received data from child process %s: >%s<" % (fd, data) )
        self.databuf += data
        #log.debug("databuf: >%s<" % self.databuf)

    def processEnded(self, status_object):
        log.debug("process ended: %s" % status_object)
        try:
            if isinstance(status_object.value, ProcessDone):
                log.debug("process exited ok: %s" % status_object.value.exitCode)
                self.exitCode = 0
                self.timeout.cancel()
                self.parent.waitingForCommand.callback( (self.exitCode, self.databuf) )
            
            elif isinstance(status_object.value, ProcessTerminated):
                log.debug("process did not exit ok: %s: [%s: %s] %s" % (status_object.value.exitCode, status_object.value.signal, status_object.value.status, self.databuf))
                self.exitCode = status_object.value.exitCode
                self.timeout.cancel()
                self.parent.waitingForCommand.callback( (self.exitCode, self.databuf) )
                pass

        except AlreadyCalled, AlreadyCancelled:
            pass
                
        except Exception, e:
            log.error("Exception raised during end of process processing. That's quite bad.")
            raise
##             traceback.print_exc(e)
##             self.timeout.cancel()
##             self.parent.waitingForCommand.errback( e )

    def timedOut(self):
        # FIXME: If the command times out, we need to ignore anything that comes
        # back from the process, or we'll notify of error conditions more than once
        # I'm hoping the AlreadyCalled an AlreadyCancelled catch above will take care of this.
        log.error("Timed out waiting for command to exit")
        self.transport.loseConnection()
        self.parent.waitingForCommand.errback( (1, '%s: command timeout' % self.__class__) )

