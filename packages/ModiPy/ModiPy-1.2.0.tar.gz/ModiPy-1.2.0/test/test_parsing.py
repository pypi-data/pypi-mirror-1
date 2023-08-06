##
## $Id$
##
##COPYRIGHT##

"""
Test the ability to correctly parse various configurations
"""
import os.path

from twisted.trial import unittest
from twisted.internet import error
from twisted.python.util import sibpath

from modipy.options import ChangeOptions
from modipy.confloader import ConfigLoader

import logging
log = logging.getLogger('modipy')
log.setLevel(logging.DEBUG)
#log.setLevel(logging.INFO)

TEST_CONFIG_DIR = sibpath(__file__, 'test_configs')

class TestParsing(unittest.TestCase):

    def setUp(self):
        optparser = ChangeOptions()
        optparser.parseOptions(['-c dummy', '--debug=%s' % logging._levelNames[log.level].lower() ])        
        self.cfgldr = ConfigLoader()
        self.cfgldr.options = optparser.options
        pass
        
    def tearDown(self):
        pass

    def test_standalone_prereq_parsing(self):
        """
        Test parsing a <prereq/> tag that stands
        by itself rather than as a child of a
        <change/>
        """
        configfile = os.path.join(TEST_CONFIG_DIR, 'post_prereqs.xml')
        
        self.cfgldr.parse(None, configfile, [])

        # check the dependencies are in the right order
        change1 = self.cfgldr.changes['change1']
        change2 = self.cfgldr.changes['change2']

        self.failUnless( change1 in change2.pre_requisites )

    def test_prereq_within_change(self):
        """
        Test parsing a <prereq/> tag as <change/> child
        """
        configfile = os.path.join(TEST_CONFIG_DIR, 'prereq_inside_change.xml')
        
        self.cfgldr.parse(None, configfile, [])

        # check the dependencies are in the right order
        change1 = self.cfgldr.changes['change1']
        change2 = self.cfgldr.changes['change2']

        self.failUnless( change1 in change2.pre_requisites )
        
