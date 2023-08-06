# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import unittest
from zope.testing.doctest import DocFileSuite, REPORT_NDIFF,ELLIPSIS

options = REPORT_NDIFF|ELLIPSIS
def test_suite():
    return unittest.TestSuite((
        DocFileSuite('../output/default.txt', optionflags=options),
        DocFileSuite('../output/emailer.txt', optionflags=options),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
