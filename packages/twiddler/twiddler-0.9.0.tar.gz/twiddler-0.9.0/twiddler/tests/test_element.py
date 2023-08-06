# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import unittest

from searchable import SearchableTests
from zope.interface.verify import verifyObject

class ElementTests(unittest.TestCase,SearchableTests):
    # This test case is deliberately designed so that it can be subclassed
    # and the setUp method replaced so that different implementations
    # can be tested

    def setUp(self):
        from twiddler import Twiddler
        self.s = self.e = Twiddler('<moo id="test"/>')['test']
        
    def test_interface(self):
        from twiddler.interfaces import IElement
        verifyObject(IElement, self.e)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ElementTests),
        ))
