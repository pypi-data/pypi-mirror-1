# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import unittest
from zope.testing.doctest import DocFileSuite, REPORT_NDIFF,ELLIPSIS
options = REPORT_NDIFF|ELLIPSIS

def addPythonScript(c,name,source):
    c.manage_addProduct['PythonScripts'].manage_addPythonScript(name)
    getattr(c,name).write(source)
    
def setUp(test):
    # I do hope someone can suggest a lighter weight way of doing
    # this in future :-/
    from Testing.makerequest import makerequest
    from Zope2 import app
    a = makerequest(app())
    a.manage_addFolder('folder')
    test.globs['folder']=a.folder
    test.globs['request']=a.REQUEST
    test.globs['addPythonScript']=addPythonScript
    
def test_suite():
    suite = unittest.TestSuite()
    try:
        import Zope2
    except ImportError:
         # no zope 2, don't try and test
        return suite
    suite.addTest(
        DocFileSuite('../readme.txt', optionflags=options,
                     setUp=setUp)
        )
    return suite

if __name__ == '__main__':
    unittest.main(default='test_suite')
