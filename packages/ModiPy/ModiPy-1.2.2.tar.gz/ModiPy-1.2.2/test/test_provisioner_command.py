##
## $Id: test_provisioner_command.py 98 2009-07-04 07:35:19Z daedalus $
##
##COPYRIGHT##

"""
Test CommandProvisioners
"""

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error, defer, reactor

from device_stub import DeviceStub as Device
from modipy.options import ChangeOptions
from modipy.confloader import ConfigLoader, ChangeController
from modipy.provisioner_command import CommandProvisioner, ConnectingProvisioner

from test_expectproto import TransportStub

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)

class TestCommandProvisioner(unittest.TestCase):

    def setUp(self):

        self.prov = CommandProvisioner('testing')

    def test_split_command_singlequotes(self):
        """
        Test splitting a command with single quotes
        """
        cmdstring = "echo 'Hello, World'"

        result = self.prov.split_command(cmdstring)
        self.failUnlessEqual( len(result), 2 )

    def test_split_command_doublequotes(self):
        """
        Test splitting a command with double quotes
        """
        cmdstring = 'echo "Hello, World"'

        result = self.prov.split_command(cmdstring)
        self.failUnlessEqual( len(result), 2 )

    def test_authoritarian_mode(self):
        """
        Test that authoritarian mode is triggered
        """
        
    def test_connect(self):
        """
        Test that the connect parameters are correct.
        """
        device = Device('fred')
        ns = {}
        self.prov.connect(device, ns)

class TestSingleChangeExecution(unittest.TestCase):
    """
    Test the logic flow of executing the stages of a single
    change with various levels of detail.
    """

    def setUp(self):
        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '--debug=%s' % logging._levelNames[log.level].lower() ])
        self.cfgldr = ConfigLoader()
        self.cfgldr.options = optparser.options
        self.controller = ChangeController(self.cfgldr)

        # Stub out the device
        self.device = Device('testdev1')
        self.cfgldr.devices[self.device.name] = self.device

        prov_xml = """
<provisioner name="prov1"
             module="modipy.provisioner_command"
             type="ConnectingProvisioner">
  <connect_command>echo "connect"</connect_command>
</provisioner>
"""
        node = etree.fromstring(prov_xml)
        self.prov = self.cfgldr.add_provisioner(None, node)

    def test_single_change_pre_impl_only(self):
        """
        Test a change that has implementation steps only.
        """
        ns = {}
        xmlstring = """
<change name="change1" module="modipy.change_command" type="CommandChange">
  <target name="testdev1"/>
  <preimpl>
    <command>
      <expect>wait for me</expect>
      <send>hello</send>
    </command>
  </preimpl>
</change>
"""
        node = etree.fromstring(xmlstring)
        change = self.cfgldr.add_change(None, node)

        # Stub the connect success to trigger data input
        def conn_made():
            reactor.callLater(0, self.prov.ep.outReceived, "I know you will wait for me until I send this")
            ConnectingProvisioner.connection_success(self.prov)
            pass
        self.prov.connection_success = conn_made

        return self.controller.do_changes(None)
        
    def test_single_change_impl_only(self):
        """
        Test a change that has implementation steps only.
        """
        ns = {}
        xmlstring = """
<change name="change1" module="modipy.change_command" type="CommandChange">
  <target name="testdev1"/>
  <impl>
    <command>
      <expect>wait for me</expect>
    </command>
  </impl>
</change>
"""
        node = etree.fromstring(xmlstring)
        change = self.cfgldr.add_change(None, node)

        # Stub the connect success to trigger data input
        def conn_made():
            reactor.callLater(0, self.prov.ep.outReceived, "I know you will wait for me until I send this")
            ConnectingProvisioner.connection_success(self.prov)
            pass
        self.prov.connection_success = conn_made

        return self.controller.do_changes(None)

    def test_single_change_pre_and_impl(self):
        """
        Test a change that has preimpl and impl steps
        """
        ns = {}
        xmlstring = """
<change name="change1" module="modipy.change_command" type="CommandChange">
  <target name="testdev1"/>

  <preimpl>
    <command>
      <expect>wait for me</expect>
    </command>
  </preimpl>

  <impl>
    <command>
      <expect>wait for me</expect>
    </command>
  </impl>
</change>
"""
        node = etree.fromstring(xmlstring)
        change = self.cfgldr.add_change(None, node)

        # Stub the connect success to trigger data input
        def conn_made():
            reactor.callLater(0, self.prov.ep.outReceived, "I know you will wait for me until I send this")
            reactor.callLater(0, self.prov.ep.outReceived, "I know you will wait for me until I send this")
            ConnectingProvisioner.connection_success(self.prov)
            pass
        self.prov.connection_success = conn_made
        
        return self.controller.do_changes(None)
    
    def test_single_change_all_impl(self):
        """
        Test a change that has preimpl and impl steps
        """
        ns = {}
        xmlstring = """
<change name="change1" module="modipy.change_command" type="CommandChange">
  <target name="testdev1"/>

  <preimpl>
    <command>
      <expect>wait for me</expect>
      <send>fnord</send>
    </command>
  </preimpl>

  <impl>
    <command>
      <expect>wait for me</expect>
      <send>fnord</send>
    </command>
  </impl>

  <postimpl>
    <command>
      <expect>wait for me</expect>
      <send>fnord</send>
    </command>
  </postimpl>

</change>
"""
        node = etree.fromstring(xmlstring)
        change = self.cfgldr.add_change(None, node)

        # Stub the connect success to trigger data input
        def conn_made():
            reactor.callLater(0, self.prov.ep.outReceived, "I know you will wait for me until I send this")
            reactor.callLater(0, self.prov.ep.outReceived, "I know you will wait for me until I send this")
            reactor.callLater(0, self.prov.ep.outReceived, "I know you will wait for me until I send this")
            ConnectingProvisioner.connection_success(self.prov)
            pass
        self.prov.connection_success = conn_made

        return self.controller.do_changes(None)
