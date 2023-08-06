##
## $Id: test_iterator.py 98 2009-07-04 07:35:19Z daedalus $
##
##COPYRIGHT##

"""
Test Iterators
"""
import os.path

from lxml import etree

from twisted.trial import unittest
from twisted.internet import error, defer
from twisted.python.util import sibpath

from modipy.options import ChangeOptions
from modipy.confloader import ConfigLoader, ChangeController
from modipy.provisioner import Provisioner
from modipy.iterator import create_iterator
from modipy.change import Change
from device_stub import DeviceStub as Device

import logging
from modipy import debug
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)

CONFIG_BASE = sibpath(__file__, "test_configs")

class TestIteratorParsing(unittest.TestCase):
    """
    Test parsing of various iterator syntax
    """

    def setUp(self):
        pass

    def test_single_entry_dict(self):
        """
        Test parsing of a single dict with 1 entry
        """
        configstr = """
<iterator name='testiter'>
  <dict>
    <entry name="myname">myvalue</entry>
  </dict>
</iterator>
"""
        node = etree.fromstring(configstr)
        iterator = create_iterator(node)

    def test_multiple_entry_dict(self):
        """
        Test parsing of a single dict with multiple entries
        """
        configstr = """
<iterator name='testiter'>
  <dict>
    <entry name="myname">myvalue</entry>
    <entry name="blah">fred</entry>
    <entry name="thing">145</entry>
    <entry name="morestuff">wibble</entry>
  </dict>
</iterator>
"""
        node = etree.fromstring(configstr)
        iterator = create_iterator(node)
        
    def test_multiple_dict(self):
        """
        Test parsing of a 3 dicts with 1 entry
        """
        configstr = """
<iterator name='testiter'>
  <dict>
    <entry name="myname1">myvalue1</entry>
  </dict>
  <dict>
    <entry name="myname2">myvalue2</entry>
  </dict>
  <dict>
    <entry name="myname3">myvalue2</entry>
  </dict>
</iterator>
"""
        node = etree.fromstring(configstr)
        iterator = create_iterator(node)

    def test_multi_entry_multi_dict(self):
        """
        Test parsing of a 3 dicts with multiple entries
        """
        configstr = """
<iterator name='testiter'>
  <dict>
    <entry name="myname1">myvalue1</entry>
    <entry name="myname2">myvalue2</entry>
  </dict>
  <dict>
    <entry name="myname2">myvalue2</entry>
    <entry name="mynamefnord">myvalue2</entry>
  </dict>
  <dict>
    <entry name="myname3">myvalue2</entry>
    <entry name="fgneier">1556</entry>
    <entry name="monost">01023923ghdsdjfh</entry>
  </dict>
</iterator>
"""
        node = etree.fromstring(configstr)
        iterator = create_iterator(node)
        
    def test_noname(self):
        """
        Test that an iterator with no name is an error
        """
        configstr = """
<iterator>
  <dict>
    <entry name="myname">myvalue</entry>
  </dict>
</iterator>
"""
        node = etree.fromstring(configstr)
        self.failUnlessRaises(ValueError, create_iterator, node)

class TestCSVIterator(unittest.TestCase):
    """
    Test creation of an Iterator from a CSV file
    """

    def test_csv_parsing(self):
        """
        Test the ability to parse a csv file as an iterator
        """
        csvfile = 'iterator.csv'
        configstr = """
<iterator name='csvtest' type='csv' file='%s'/>
""" % os.path.join(CONFIG_BASE, csvfile)

        node = etree.fromstring(configstr)
        iterator = create_iterator(node)
        iterator.load_config()
        self.failUnlessEqual( len([x for x in iterator]), 3 )

    def test_dict_capable(self):
        """
        Check that a CSV iterator is usable as a dictionary
        """
        csvfile = 'iterator.csv'
        configstr = """
<iterator name='csvtest' type='csv' file='%s'/>
""" % os.path.join(CONFIG_BASE, csvfile)

        node = etree.fromstring(configstr)
        iterator = create_iterator(node)
        iterator.load_config()

        for item in iterator:
            self.failUnless( item.has_key('name1') )
            self.failUnless( item.has_key('anothername') )
            pass
        
class TestIteration(unittest.TestCase):
    """
    Test iteration using an iterator.
    """

    def setUp(self):

        configstr = """
<iterator name='testiter'>
  <dict>
    <entry name="name">myname</entry>
    <entry name="location">eigenlab</entry>
    <entry name="purpose">test1</entry>
  </dict>

  <dict>
    <entry name="name">beagle</entry>
    <entry name="location">melblab</entry>
    <entry name="purpose">test2</entry>
  </dict>

  <dict>
    <entry name="name">fred</entry>
    <entry name="location">Andromeda</entry>
    <entry name="purpose">joke</entry>
  </dict>

</iterator>
"""
        node = etree.fromstring(configstr)
        self.iterator = create_iterator(node)
        
    def test_plain_iteration(self):
        """
        Test iteration of an iterator loaded from XML
        """
        for index, item in enumerate(self.iterator):
            log.debug("item: %s", item)
            if index == 0:
                self.failUnlessEqual( item['name'], 'myname' )
            elif index == 1:
                self.failUnlessEqual( item['name'], 'beagle' )
            elif index == 2:
                self.failUnlessEqual( item['name'], 'fred' )

            pass

class TestCommandIterator(unittest.TestCase):
    """
    Test iterating over a command changes
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

        iterator_xml = """
<iterator name="testiter01">
  <dict>
    <entry name="item1">value1</entry>
    <entry name="item2">value2</entry>
  </dict>

  <dict>
    <entry name="item1">value3</entry>
    <entry name="item2">value4</entry>
  </dict>

</iterator>
"""
        node = etree.fromstring(iterator_xml)
        self.iterator = self.cfgldr.add_iterator(None, node)

        self.exec_order = []

    def change_ran(self, prov, device, ns, **kwargs):
        log.debug("ns: %s", ns)
        self.exec_order.append(ns)
        return defer.succeed(None)
    
    def test_iterate_single_change(self):
        """
        Test a change that has preimpl and impl steps
        """
        ns = {}
        xmlstring = """
<change name="change1" module="modipy.change_command" type="CommandChange" iterator="testiter01">
  <target name="testdev1"/>

</change>
"""
        node = etree.fromstring(xmlstring)
        change = self.cfgldr.add_change(None, node)

        change.apply = self.change_ran

        def finished(ignored):
            self.failUnlessEqual(self.exec_order[0]['item1'], 'value1')
            self.failUnlessEqual(self.exec_order[1]['item1'], 'value3')
        
        d = self.controller.do_changes(None)
        d.addCallback(finished)
        return d
