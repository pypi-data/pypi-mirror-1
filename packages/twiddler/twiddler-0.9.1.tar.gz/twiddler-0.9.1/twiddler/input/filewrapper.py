# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

import os

from twiddler.input.default import Default
from twiddler.interfaces import IInput
from zope.interface import implements

class FileWrapper:

    implements(IInput)

    def __init__(self,input=Default,prefix=None,encoding=None):
        self.input = input
        self.encoding = encoding
        if prefix is None:
            self.prefix = os.getcwd()
        elif os.path.isfile(prefix):
            self.prefix = os.path.split(prefix)[0]
        else:
            self.prefix = prefix

    def __call__(self,source,indexes):
        source = open(os.path.abspath(os.path.join(self.prefix,source))).read()
        if self.encoding is not None:
            source = source.decode(self.encoding)
        return self.input(source,indexes)
