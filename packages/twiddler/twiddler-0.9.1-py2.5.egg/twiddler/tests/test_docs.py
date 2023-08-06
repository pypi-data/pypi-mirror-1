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
        DocFileSuite('../readme.txt', optionflags=options),
        DocFileSuite('../docs/replace.txt', optionflags=options),
        DocFileSuite('../docs/repeat.txt', optionflags=options),
        DocFileSuite('../docs/search.txt', optionflags=options),
        DocFileSuite('../docs/filters.txt', optionflags=options),
        DocFileSuite('../docs/inandout.txt', optionflags=options),
        DocFileSuite('../docs/execution.txt', optionflags=options),
        DocFileSuite('../executor/source.txt', optionflags=options),
        DocFileSuite('../docs/templating.txt', optionflags=options),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
