## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Acquisition import Explicit
from Globals import InitializeClass
from twiddler.interfaces import IElement
from twiddler.zope2.ZopeTwiddlerRepeater import ZopeTwiddlerRepeater
from zope.interface import implements

class ZopeTwiddlerCopyElement(Explicit):

    implements(IElement)

    def __init__(self,e):
        self.e = e
    
    security = ClassSecurityInfo()

    security.declareObjectProtected(view)
    
    def get_node(self):
        return self.e.node

    node = property(get_node)

    security.declareProtected(view,'__getitem__')
    def __getitem__(self,value):
        "Proxy for TwiddlerSearcher.__getitem__"
        return ZopeTwiddlerCopyElement(self.e[value]).__of__(self)
    
    security.declareProtected(view,'getBy')
    def getBy(self,**spec):
        "Proxy for TwiddlerSearcher.getBy"
        return ZopeTwiddlerCopyElement(self.e.getBy(**spec)).__of__(self)

    security.declareProtected(view,'replace')
    def replace(self,*args,**kw):
        "Proxy for TwiddlerElement.replace"
        self.e.replace(*args,**kw)

    security.declareProtected(view,'repeater')
    def repeater(self,*args,**kw):
        "Proxy for TwiddlerElement.repeater"
        return ZopeTwiddlerRepeater(self.e).__of__(self)

    security.declareProtected(view,'clone')
    def clone(self):
        "Proxy for TwiddlerElement.clone"
        # import here to avoid import loop
        return ZopeTwiddlerCopyElement(self.e.clone()).__of__(self)
    
    security.declareProtected(view,'remove')
    def remove(self,*args,**kw):
        "Proxy for TwiddlerElement.remove"
        self.e.remove(*args,**kw)
    
InitializeClass(ZopeTwiddlerCopyElement)
    
