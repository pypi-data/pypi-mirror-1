## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from twiddler.zope2.interfaces import *
from twiddler.input.default import Default as DefaultInput
from twiddler.input.plaintext import PlainText
from twiddler.output.default import Default as DefaultOutput
from twiddler.zope2.executor.traverse import Traverse
from zope.interface import directlyProvides

class Factory:

    def __init__(self,obj):
        self.obj = obj

    def __call__(self):
        if IConfigurableComponent.implementedBy(self.obj):
            return self.obj()
        return self.obj

input_default = Factory(DefaultInput)
directlyProvides(input_default,IInputFactory)

input_plaintext = Factory(PlainText)
directlyProvides(input_plaintext,IInputFactory)

output_default = Factory(DefaultOutput)
directlyProvides(output_default,IOutputFactory)

no_executor = Factory(None)
directlyProvides(no_executor,IExecutorFactory)

traverse_executor = Factory(Traverse)
directlyProvides(traverse_executor,IExecutorFactory)
