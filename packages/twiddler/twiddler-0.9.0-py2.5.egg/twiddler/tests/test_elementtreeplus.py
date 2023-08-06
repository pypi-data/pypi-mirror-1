# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import unittest
from doctest import DocFileSuite,ELLIPSIS

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('elementtreeplus.txt', optionflags=ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
