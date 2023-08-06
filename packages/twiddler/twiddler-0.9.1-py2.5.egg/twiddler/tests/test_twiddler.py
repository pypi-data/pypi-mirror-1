# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import unittest

from searchable import SearchableTests
from zope.interface.verify import verifyObject

class TwiddlerTests(unittest.TestCase,SearchableTests):
    # This test case is deliberately designed so that it can be subclassed
    # and the setUp method replaced so that different implementations
    # can be tested

    def setUp(self):
        from twiddler import Twiddler
        self.s = self.t = Twiddler('<moo/>')
        
    def test_interface(self):
        from twiddler.interfaces import ITwiddler
        verifyObject(ITwiddler, self.t)

    def test_replaced_quoting_already_quoted(self):
        self.t.setSource('<input name="test" type="text" value="" />')
        self.t['test'].replace(value='&lt;something&gt;',filters=False)
        self.assertEqual(
            self.t.render(),
            '<input name="test" type="text" value="&lt;something&gt;" />'
            )

    def test_replaced_quotable_characters(self):
        self.t.setSource('<input name="test" type="text" value="" />')
        self.t['test'].replace(value='<something>',filters=False)
        self.assertEqual(
            self.t.render(),
            '<input name="test" type="text" value="<something>" />'
            )

    def test_cdata_quoting(self):
        xml = '<tag><![CDATA[ <some> <more> <tags> ]]></tag>'
        self.t.setSource(xml)
        self.assertEqual(self.t.render(),xml)
                             

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TwiddlerTests),
        ))
