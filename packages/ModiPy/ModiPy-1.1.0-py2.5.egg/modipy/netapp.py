#!/usr/bin/python
#
# $Id
#

"""
This module provides Network Appliance specific classes, most notably
a ZAPIProvisioner that implements a Provisioner for Network Appliance
equipment through the use of the NetApp ZAPI.
"""
import os
import sys
import re
import base64

from zope.interface import Interface, implements

from twisted.internet import defer, reactor
from twisted.internet import protocol, ssl
from twisted.python import log as tlog
from twisted.web import http, error, client

from lxml import etree
from StringIO import StringIO

import logging
import debug
log = logging.getLogger('modipy')

from provisioner import IProvisioner, Provisioner
from change import Change, ChangeConditionFailure, UserBailout
from change_command import ExpectSet, CommandChange
from zapi import ZAPITool
import util

class IZAPIProvisioner(IProvisioner):
    pass

class ZAPIProvisioner(Provisioner):
    """
    A ZAPIProvisioner uses HTTP (or HTTPS) to contact a NetApp
    and issue commands to it.
    """
    zapi_request_header = """<?xml version='1.0' encoding='utf-8' ?>
<!DOCTYPE netapp SYSTEM 'file:/etc/netapp_filer.dtd'>
<netapp xmlns='http://www.netapp.com/filer/admin' version='1.0'>
"""
    zapi_request_footer = r"</netapp>"
    zapi_request_path = "/servlets/netapp.servlets.admin.XMLrequest_filer"

    implements(IZAPIProvisioner)

    def __init__(self, name='', namespace={}, authoritarian=False, autobackout=False, command_timeout=300):
        """
        Create a new ZAPIProvisioner.
        """
        # FIXME: May not be required
        Provisioner.__init__(self, name, namespace, authoritarian, autobackout)
        self.command_timeout = 300

        # Set up a deferred dictionary, keyed to uniquely identify a set
        # of commands (ExpectSet) running on given device
        self.all_commands_defer = {}

        # Similarly, key up a series of zapi requests that are outstanding
        # so we can parse the results before returning them via .callback()
        self.zapi_defer = {}

        self.zapi_tool = ZAPITool()

    def zapi_request(self, ignored, device, command, timeout=30):
        """
        Issue a ZAPI request to a device.
        """
        self.authority_check(command)
        log.debug("issuing command: %s", command)
        return self.zapi_tool.zapi_request(device, command, timeout=timeout)
            
    def zapi_system_command(self, ignored, device, command, timeout=30):
        """
        Run a commandline command via ZAPI.
        """
        self.authority_check(command)
        log.debug("issuing command: %s", command)
        return self.zapi_tool.zapi_system_command(device, command, timeout=timeout)

    def zapi_get_file(self, ignored, device, filename, root='/vol/vol0'):
        self.authority_check("getfile: %s" % '/'.join(root, filename))
        return self.zapi_tool.get_file(device, filename, root=root)

    def zapi_put_file(self, ignored, device, localpath, remotepath, root='/vol/vol0', offset=0, overwrite=True):
        """
        Put a local file 'localpath' onto the Filer as 'root/remotepath'
        """
        self.authority_check("putfile: %s to %s" % (localpath, '/'.join(root, filename)))
        # load the local data in
        data = open(localpath, 'r').read()
        return self.zapi_tool.put_file(device, remotepath, data, root=root, offset=offset, overwrite=overwrite)
    
    def zapi_test(self, device):
        """
        Run a test ZAPI query on whatever device I'm connected to
        """
        return self.zapi_system_command(device, 'uptime')
        #return self.zapi_request(device, "<system-get-version/>")

    def run_commands(self, ignored, device, expectset, namespace):

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

        # If we have ordinary commands, use the system-cli mechanism for running them
        if len(expectset.commands) > 0:
            log.debug("Running <system-cli/> commands...")

            for (expr, cmdstring) in expectset.commands:

                try:
                    # Perform variable substitution on the command string
                    log.debug("determining commandstring from template: %s", cmdstring)
                    cmdstring = str(util.substituteVariables(cmdstring, namespace))
                    log.debug("commandstring is: %s", cmdstring)

                    # add the cmdstring to the namespace
                    namespace['command.send'] = cmdstring

                except KeyError, e:
                    log.error("KeyError in commands: %s" % e)
                    self.all_commands_defer.errback( e )
                    return self.all_commands_defer[deferred_key]

                d.addCallback(self.zapi_system_command, device, cmdstring, self.command_timeout)
                d.addCallbacks(self.command_completed, self.command_failed, callbackArgs=(namespace,), errbackArgs=(namespace,) )
                pass
            pass

        # If we have zapi based commands, pass them directly to the zapi-request mechanism
        elif len(expectset.zapi_commands) > 0:
            log.debug("Running zapi commands: %s", expectset.zapi_commands)

            for cmdxml in expectset.zapi_commands:

                cmdxml = str(util.substituteVariables(cmdxml, namespace))
                # split the xml into the actual commands
                cmdnode = etree.fromstring( cmdxml, etree.XMLParser(ns_clean=True))
                if cmdnode.tag == 'zapicommand':
                    cmdstring = etree.tostring(cmdnode[0])
                    log.debug("cmdstring: %s", cmdstring)
                    try:
                        # Perform variable substitution on the command string
##                         log.debug("determining commandstring from template: %s", cmdstring)
##                         cmdstring = str(util.substituteVariables(cmdstring, namespace))
##                         log.debug("commandstring is: %s", cmdstring)

                        # add the cmdstring to the namespace
                        namespace['command.send'] = cmdstring

                    except KeyError, e:
                        log.error("KeyError in commands: %s" % e)
                        self.all_commands_defer.errback( e )
                        return self.all_commands_defer[deferred_key]

                    d.addCallback(self.zapi_request, device, cmdstring, self.command_timeout)
                    d.addCallbacks(self.command_completed, self.command_failed, callbackArgs=(namespace,), errbackArgs=(namespace,) )

                elif cmdnode.tag == 'getfile':
                    log.info("Getting file!")
                    # get the variables we need
                    remotepath_node = cmdnode.find('remotepath')
                    remotepath = remotepath_node.text
                    filer_root = remotepath_node.attrib.get('root', '/vol/vol0')
                    
                    localpath_node = cmdnode.find('localpath')
                    if localpath_node is None:
                        localpath = remotepath
                        local_absolute = False
                        create_pathtree = True
                    else:
                        localpath = localpath_node.text
                        local_absolute = bool(localpath_node.attrib.get('absolute', False))
                    
                    log.debug("remotepath: %s", remotepath)
                    log.debug("filer_root: %s", filer_root)
                    
                    d.addCallback(self.zapi_get_file, device, remotepath)
                    d.addCallback(self.zapi_file_received, device, remotepath, localpath, local_absolute)
                    d.addCallbacks(self.command_completed, self.command_failed, callbackArgs=(namespace,), errbackArgs=(namespace,) )
                    
                elif cmdnode.tag == 'putfile':
                    log.info("Putting file!")

                    # get the variables we need
                    localpath_node = cmdnode.find('localpath')
                    localpath = localpath_node.text

                    remotepath_node = cmdnode.find('remotepath')
                    remotepath = remotepath_node.text
                    filer_root = remotepath_node.attrib.get('root', '/vol/vol0')
                    append = remotepath_node.attrib.get('append', False)
                    overwrite = remotepath_node.attrib.get('overwrite', True)
                    offset = int(remotepath_node.attrib.get('offset', 0))
                    
                    log.debug("localpath: %s", localpath)
                    log.debug("remotepath: %s", remotepath)
                    log.debug("filer_root: %s", filer_root)
                    if append:
                        offset = -1
                        overwrite = True

                    log.debug("append: %s, offset: %s", append, offset)
                    log.debug("overwrite: %s", overwrite)
                    
                    d.addCallback(self.zapi_put_file, device, localpath, remotepath, filer_root, offset, overwrite)
                    d.addCallback(self.zapi_file_sent, device, remotepath, localpath)
                    d.addCallbacks(self.command_completed, self.command_failed, callbackArgs=(namespace,), errbackArgs=(namespace,) )
                    pass
                pass
            pass

        # Set up callbacks for when all commands are finished.
        # If no commands are run, this will get called with success immediately.
        d.addCallbacks(self.all_commands_done, self.all_commands_failure, callbackArgs=(deferred_key, namespace,), errbackArgs=(deferred_key, namespace,))
            
        return self.all_commands_defer[deferred_key]

    def zapi_file_received(self, (results, filedata), device, remotepath, localpath, absolute=False):
        """
        File data is received for a remote file. Save it locally in localpath
        """
        log.debug("Got file data for '%s': %s", remotepath, filedata)
        log.debug("saving data to: '%s', absolute: %s", localpath, absolute)
        
        # Save the file data to a local file.
        # If absolute is not set, save it to a file relative to the current working directory
        if not absolute:
            log.debug("cwd: %s", os.getcwd())
            localpath = os.path.join(os.getcwd(), device.name, localpath.lstrip('/'))
            log.debug("joined: %s", localpath)
            pass
        log.debug("saving data to: '%s', absolute: %s", localpath, absolute)            
        try:
            os.makedirs(os.path.dirname(localpath))
            fd = open(localpath, 'w')
            fd.write(filedata)
            fd.close()
        except IOError, e:
            log.error("Cannot write data to local file '%s': %s", localpath, e)
            raise
        
        return results

    def zapi_file_sent(self, result, device, remotepath, localpath):
        """
        Called when the file has been sent to the remote device.
        """
        log.debug("file sent with result: %s", result)
        return result

    def command_completed(self, result, namespace):
        """
        When the command is completed, add its output to a
        global resultset. This sets the exitcode to the
        exitcode of the last command that completed, and
        """
        log.debug("a command has completed with result: %s (%s)", result, result.status)
        return result
        
    def command_failed(self, failure, namespace):
        """
        If a command failed, pass the failure up the Deferred chain.
        Don't consume the error.
        """
        #self.all_commands_defer.errback( Exception(errorstr) )
        return failure

    def all_commands_done(self, result, deferred_key, namespace):
        """
        Called when all the commands have completed.
        """
        log.debug("All commands have finished.")
        self.all_commands_defer[deferred_key].callback( result )
        
    def all_commands_failure(self, failure, deferred_key, namespace):
        """
        Some kind of failure in the commands occurred.
        """
        self.all_commands_defer[deferred_key].errback( failure )

    def authority_check(self, command):
        """
        Check to see if we should proceed or not
        """
        if self.authoritarian:
            log.debug("Authoritarian mode. Waiting for ok to proceed...")
            sys.stdout.write("Command is: %s\n" % command)
            isok = raw_input("Issue command (y/n)[n]?> ")
            if isok.startswith('y'):
                log.debug("Ok! Let's continue!")
            else:
                log.info(" Bailing out at your command.")
                raise UserBailout("Bailing out at your command")
                return


class ZAPIExpectSet(ExpectSet):

    known_children = ExpectSet.known_children + ['zapicommand', 'getfile', 'putfile' ]

    def __init__(self, node):
        log.debug("known children: %s", self.known_children)
        ExpectSet.__init__(self, node)

        # FIXME: Might want make this more generic and do a kind of
        # for cmd in known_children:
        #    for cmdelem in node.xpath('%s/*' % cmd):
        # thing.. and then deal with the individual commands within
        # the specific provisioner

        self.zapi_commands = []

        for child in self.known_children:
            for cmd in node.xpath('%s' % child):
                log.debug("zapicmd: %s", cmd)
                log.debug("Adding a zapi command to the expectset: %s", etree.tostring(cmd))
                self.zapi_commands.append(etree.tostring(cmd))
                pass
            pass
        

class ZAPIChange(CommandChange):
    """
    A ZAPIChange is a ZAPI specific change, which shares much in common with
    a standard CommandChange.
    """

    provisioner_interface = IZAPIProvisioner
    
    def create_expectset(self, node):
        return ZAPIExpectSet(node)

    def check_conditions(self, result, conditions, namespace):
        if len(conditions) == 0:
            conditions = [ "results.status == 'passed'", ]

        try:
            Change.check_conditions(self, result, conditions, namespace)
        except ChangeConditionFailure, f:
            if result.status == 'failed':
                log.error("  ZAPI Error: %s: %s", result.errno, result.reason)
            raise
    
if __name__ == '__main__':

    # If you run this directly, the module provide a very simple
    # commandline interface to the filer, which runs system-cli
    # commands via ZAPI.
    # Because of the way twisted works, exitcodes aren't possible yet.

    import device

    try:
        device_name = sys.argv[1]
        command = ' '.join(sys.argv[2:])
    except IndexError, e:
        log.error("Usage: netapp.py <device> <zapi_command>")
        raise

    log.debug("device: %s, command: %s", device_name, command)

    device = device.Device(device_name)
    #device.ipaddress = '10.232.8.71'
    device.zapi_scheme = 'https'

    prov = ZAPIProvisioner('zapi-test')
    d = prov.zapi_system_command(None, device, command)

    def got_result(result):
        log.debug("result is: %s", result)
        # Find the result output
        output = result.results.find('cli-output').text
        print output
        cli_errno = int(result.results.find('cli-result-value').text)
        #print "errno: %d" % cli_errno
        reactor.stop()
        
    def error(failure):
        log.error("error fetching page")
        tlog.err(failure)
        reactor.stop()

    d.addCallback(got_result)
    d.addErrback(error)

    reactor.run()
