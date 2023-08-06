# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from zope.interface.verify import verifyObject

class SearchableTests:
    # This is only designed to be mixed in to test cases for objects which
    # implement ISearchable or a subclass thereof

    def test_searcheable_interface(self):
        from twiddler.interfaces import ISearchable
        verifyObject(ISearchable, self.s)

    def test_bad_getBy(self):
        try:
            self.s.getBy(x='x',y='y')
        except ValueError:
            pass # yay!
        else:
            self.fail('ValueError not raised')
            
    def test_notfound_getBy(self):
        try:
            self.s.getBy(foo='NotFound!')
        except KeyError:
            pass # yay!
        else:
            self.fail('KeyError not raised')

    def test_notfound_getitem(self):
        try:
            self.s['NotFound!']
        except KeyError:
            pass # yay!
        else:
            self.fail('KeyError not raised')
