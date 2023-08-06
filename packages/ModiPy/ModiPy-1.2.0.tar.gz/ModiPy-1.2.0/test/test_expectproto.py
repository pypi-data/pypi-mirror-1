##
## $Id$
##
##COPYRIGHT##

"""
Test the ExpectProtocol
"""
import sys

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error, reactor, defer

from modipy.device import Device
from modipy.provisioner_command import ExpectProtocol, CommandProvisioner
from modipy.change_command import ExpectSet

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)

class TransportStub:
    """
    A stub class to emulate a twisted Transport
    """
    def writeSomeData(self, data):
        """
        Pretend to write some data to a remote thing.
        """

class TestExpectProto(unittest.TestCase):

    def setUp(self):
        sessionlog = sys.stdout
        
        self.prov = CommandProvisioner('testing', sessionlog)
        self.ep = ExpectProtocol(self.prov, sessionlog)
        self.ep.transport = TransportStub()

    def test_expect_timeout_default(self):
        """
        Test that waiting for an expect string will time out
        after 300 seconds by default.
        """
        raise unittest.SkipTest("Default timeout of 300 seconds will take ages to test.")
        ns = {}
        xmlstring = """
<impl>
  <command>
    <expect>wait for me</expect>
  </command>
</impl>
"""
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)

        def timeout_too_long(d):
            self.ep.data_wait_timeout.cancel()
            raise NotImplementedError("timeout took too long. implementation error.")

        def cancel_cl(ignored, cl):
            cl.cancel()
            return ignored
        
        d = self.ep.run_remote_commands(expectset, ns)
        
        # call this if the timeout takes too long
        cl = reactor.callLater(301, timeout_too_long, d)
        d.addErrback(cancel_cl, cl)
        
        self.failUnlessFailure(d, ValueError)
        return d

    def test_expect_timeout_nondefault(self):
        """
        Test setting a custom timeout value for the expect
        """
        CUSTOM_TIMEOUT = 5
        ns = {}
        xmlstring = """
<impl>
  <command>
    <expect timeout="%s">wait for me</expect>
  </command>
</impl>
""" % CUSTOM_TIMEOUT
        
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)

        def timeout_too_long(d):
            self.ep.data_wait_timeout.cancel()
            raise NotImplementedError("timeout took too long. implementation error.")

        def cancel_cl(ignored, cl):
            cl.cancel()
            return ignored
        
        d = self.ep.run_remote_commands(expectset, ns)
        
        # call this if the timeout takes too long
        cl = reactor.callLater(CUSTOM_TIMEOUT+1, timeout_too_long, d)
        d.addErrback(cancel_cl, cl)
        
        self.failUnlessFailure(d, ValueError)
        return d
    
    def test_single_expect(self):
        """
        Test waiting for a single expect thing that then
        triggers.
        """
        ns = {}
        xmlstring = """
<impl>
  <command>
    <expect>wait for me</expect>
  </command>
</impl>
"""
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)
        d = self.ep.run_remote_commands(expectset, ns)

        # set up a call to send some data in a moment
        def send_data():
            data = """
This is some data that will be sent to the client.
Emulating a session to a remote host or process.
It is waiting for a string.
The string: wait for me, in fact.
That will appear in the middle, on the line above.
woo woo.
"""
            self.ep.outReceived(data)
            pass
        
        reactor.callLater(0, send_data)
        return d

    def test_single_partial_receive(self):
        """
        Test reception of only part of the expected
        stream, and then more of it a little later.
        """
        ns = {}
        xmlstring = """
<impl>
  <command>
    <expect>wait for me</expect>
  </command>
</impl>
"""
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)
        d = self.ep.run_remote_commands(expectset, ns)

        # set up a call to send some data in a moment
        def send_data_part1():
            data = """
This is some data that will be sent to the client.
Emulating a session to a remote host or process.
It is waiting for a string.
The string: wait fo"""
            self.ep.outReceived(data)
            pass
        
        def send_data_part2():
            data = """r me, in fact.
That will appear in the middle, on the line above.
woo woo.
"""
            self.ep.outReceived(data)
            pass
        
        reactor.callLater(0, send_data_part1)
        reactor.callLater(1, send_data_part2)
        return d
    
    def test_chained_expect(self):
        """
        Test multiple expects chained together without any
        <send/> nodes between them.
        """
        ns = {}
        xmlstring = """
<impl>
  <command>
    <expect>wait for me</expect>
  </command>
  <command>
    <expect>wait some more</expect>
  </command>
</impl>
"""
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)
        d = self.ep.run_remote_commands(expectset, ns)

        # set up a call to send some data in a moment
        def send_data():
            data = """
This is some data that will be sent to the client.
Emulating a session to a remote host or process.
It is waiting for a string.
The string: wait for me, in fact.
That will appear in the middle, on the line above.
woo woo.
and it will wait some more for more data as well.
"""
            self.ep.outReceived(data)
            pass
        
        reactor.callLater(0, send_data)
        return d

    
    def test_extra_data(self):
        """
        Test that extra data received after all the expects have
        already been found doesn't break processing.
        """
        ns = {}
        xmlstring = """
<impl>
  <command>
    <expect>wait for me</expect>
  </command>
</impl>
"""
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)

        def done_data_send(ignored):
            log.debug("sent all the data!")
            return ignored
        
        all_data_sent = defer.Deferred()
        all_data_sent.addCallback(done_data_send)

        d = self.ep.run_remote_commands(expectset, ns)
        # set up a call to send some data in a moment
        def send_data_part1():
            data = """
This is some data that will be sent to the client.
Emulating a session to a remote host or process.
It is waiting for a string.
The string: wait fo"""
            self.ep.outReceived(data)
            pass
        
        def send_data_part2():
            data = """r me, in fact.
That will appear in the middle, on the line above.
woo woo.
"""
            self.ep.outReceived(data)
            pass
        
        def send_data_part3(all_data_sent):
            data = """
spurious extra data
"""
            self.ep.outReceived(data)
            all_data_sent.callback('whee!')
            pass
        
        reactor.callLater(0, send_data_part1)
        reactor.callLater(0, send_data_part2)
        reactor.callLater(0, send_data_part3, all_data_sent)

        return defer.DeferredList([d, all_data_sent])

    def test_single_send(self):
        """
        Test a single send command
        """
        ns = {}
        xmlstring = """
<impl>
  <command>
    <send>do it now</send>
  </command>
</impl>
"""
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)
        d = self.ep.run_remote_commands(expectset, ns)
        return d

    def test_multiple_send(self):
        """
        Test several send commands in a row
        """
        ns = {}
        xmlstring = """
<impl>
  <command>
    <send>do it now</send>
  </command>

  <command>
    <send>do it now</send>
  </command>

  <command>
    <send>do it now</send>
  </command>

</impl>
"""
        node = etree.fromstring(xmlstring)
        expectset = ExpectSet(node)
        d = self.ep.run_remote_commands(expectset, ns)
        return d
