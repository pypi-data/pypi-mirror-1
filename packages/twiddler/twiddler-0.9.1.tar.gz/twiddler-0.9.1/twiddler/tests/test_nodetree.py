# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import unittest

from zope.interface.verify import verifyObject

class NodeTreeTests(unittest.TestCase):
    # This test case is deliberately designed so that it can be subclassed
    # and the setUp method replaced so that different implementations
    # can be tested

    def setUp(self):
        from twiddler import Twiddler
        t = Twiddler('''<?xml version='1.0' encoding='utf-8'?><moo><cow id="test">some text</cow>tail</moo>''')
        self.t = t.node
        self.n = t['test'].node
        
    def test_node_interface(self):
        from twiddler.interfaces import INode
        verifyObject(INode, self.n)

    def test_node_attributetypes(self):
        self.failUnless(isinstance(self.n.tag,unicode))
        self.failUnless(isinstance(self.n.text,unicode))
        self.failUnless(isinstance(self.n.tail,unicode))
        
    def test_tree_interface(self):
        from twiddler.interfaces import ITree
        verifyObject(ITree, self.t)

    def test_bad_element_search(self):
        self.assertRaises(KeyError,self.n.search,'foo')
        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(NodeTreeTests),
        ))
