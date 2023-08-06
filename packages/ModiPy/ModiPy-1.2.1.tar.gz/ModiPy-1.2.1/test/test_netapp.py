##
## $Id: test_netapp.py 98 2009-07-04 07:35:19Z daedalus $
##
##COPYRIGHT##

"""
Test NetApp ZAPI changes, provisioners, etc.
"""

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error, defer

from modipy.options import ChangeOptions
from modipy.confloader import ConfigLoader, ChangeController
from modipy.provisioner import Provisioner
from modipy.netapp import ZAPIProvisioner
from modipy.change import Change
from device_stub import DeviceStub as Device

#from test_provisioner import win, fail, changefail

from netappzapi.zapi import ZAPIResult

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)


class NetAppTest(unittest.TestCase):

    def setUp(self):

        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '--debug=%s' % logging._levelNames[log.level].lower() ])
        self.cfgldr = ConfigLoader()
        self.cfgldr.options = optparser.options

        self.controller = ChangeController(self.cfgldr)
        
        self.prov = ZAPIProvisioner()
        self.cfgldr.provisioners['prov1'] = self.prov

        # always work
        self.prov.zapi_request = self.win
        self.prov.zapi_system_command = self.win

        self.device = Device('dummy1')

        self.exec_order = []

    def win(self, device, cmd, *args, **kwargs):
        xmldata = """<result>
  <results status='passed'/>
</result>
"""
        result = ZAPIResult(xmldata)
        self.exec_order.append(cmd)
        return defer.succeed( result )
        
    def test_single_command(self):
        """
        Test running a change with a single commandset
        """
        xmldata = """
<change name="testchange1"
        module="modipy.netapp"
        type="ZAPIChange">

  <impl>
    <zapicommand>
      <do-something></do-something>
    </zapicommand>

  </impl>

</change>
"""
        node = etree.fromstring(xmldata)

        change = self.cfgldr.add_change(None, node)
        
        change.devices.append(self.device)

        d = self.prov.perform_change(None, change, self.cfgldr.global_namespace)
        return d
        
    def test_command_delay(self):
        """
        Test running a ZAPI command after a delay
        """
        
        xmldata = """
<change name="testchange1"
        module="modipy.netapp"
        type="ZAPIChange">

  <impl>
    <zapicommand>
      <do-something></do-something>
    </zapicommand>

  </impl>

</change>
"""
        node = etree.fromstring(xmldata)

        change = self.cfgldr.add_change(None, node)
        
        change.devices.append(self.device)

        self.prov.command_delay = 1
        d = self.prov.perform_change(None, change, self.cfgldr.global_namespace)
        return d

    def test_command_delay_sequence(self):
        """
        Test running a sequence of ZAPI commands with delays
        """
        
        xmldata = """
<change name="testchange1"
        module="modipy.netapp"
        type="ZAPIChange">

  <impl>
    <zapicommand><do-something/></zapicommand>

    <zapicommand><do-2/></zapicommand>

    <zapicommand><do-3/></zapicommand>

  </impl>

</change>
"""
        node = etree.fromstring(xmldata)

        change = self.cfgldr.add_change(None, node)
        
        change.devices.append(self.device)

        self.prov.command_delay = 1
        
        d = self.prov.perform_change(None, change, self.cfgldr.global_namespace)

        def finished(ignored):
            log.debug("exec order: %s", self.exec_order)
            self.failUnlessEqual(self.exec_order,
                                 [ '<do-something/>',
                                   '<do-2/>',
                                   '<do-3/>',
                                   ])
            pass
        d.addCallback(finished)
        return d
