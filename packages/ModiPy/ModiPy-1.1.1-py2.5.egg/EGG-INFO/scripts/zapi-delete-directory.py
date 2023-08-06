#!/usr/bin/python
#
# Rename a directory on a NetApp
#
import sys
from optparse import OptionParser

from twisted.internet import reactor, defer
from modipy.zapi import ZAPITool

version = '1.0'
usage = 'zapi-delete-directory.py <device> </vol/path>'

outerr = 0

optparser = OptionParser(usage=usage, version=version)
options, args = optparser.parse_args()

if len(args) < 2:
    optparser.error("Not enough arguments.")
    sys.exit(1)

ztool = ZAPITool()

def all_failed(failure):
    global outerr
    outerr = 1
    sys.stderr.write("Error: %s\n" % failure.value)
    reactor.stop()

def all_ok(ignored):
    reactor.stop()

@defer.inlineCallbacks
def rename_directory(device, path):
    """
    Rename a directory on a device
    """
    command = "<file-delete-directory><path>%s</path></file-delete-directory>" % (path)

    result = yield ztool.zapi_request(device, command)

    # check the result is ok
    if result.status == 'failed':
        raise ValueError("Rename failed: %s" % result)

def go(args, options):
    """
    Called when the reactor is running, to do the ZAPI stuff.
    """
    d = rename_directory(args[0], args[1])
    d.addErrback(all_failed)
    d.addCallback(all_ok)

reactor.callWhenRunning(go, args, options)
reactor.run()

# Exit with an error code, if one was set
sys.exit(outerr)
