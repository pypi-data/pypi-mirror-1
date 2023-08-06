## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Acquisition import Explicit
from Globals import InitializeClass
from twiddler.zope2.ZopeTwiddlerCopyElement import ZopeTwiddlerCopyElement

class ZopeTwiddlerCopy(Explicit):

    def __init__(self,t):
        self.t = t
    
    security = ClassSecurityInfo()

    security.declareObjectProtected(view)
    
    def get_output(self):
        return self.t.output

    output = property(get_output)

    def get_node(self):
        return self.t.node

    node = property(get_node)

    security.declareProtected(view,'clone')
    def clone(self):
        "Return a clone of ZopeTwiddlerCopy"
        return ZopeTwiddlerCopy(loads(dumps(self.t))).__of__(self)

    security.declareProtected(view,'__getitem__')
    def __getitem__(self,value):
        "Proxy for TwiddlerSearcher.__getitem__"
        return ZopeTwiddlerCopyElement(self.t[value]).__of__(self)
    
    security.declareProtected(view,'getBy')
    def getBy(self,**spec):
        "Proxy for TwiddlerSearcher.getBy"
        return ZopeTwiddlerCopyElement(self.t.getBy(**spec)).__of__(self)

    security.declareProtected(view,'execute')
    def execute(self,*args,**kw):
        """Calls an executor in the Twiddler in the context of this proxy"""
        if self.t.executor is not None:
            t = self.t.executor(*((self,)+args),**kw)
            del self.t.executor
            if t is not None:
                return t
        return self.t
        
    security.declareProtected(view,'render')
    def render(self,*args,**kw):
        """Renders this Twiddler Copy"""
        # first we execute any code block
        t = self.execute(*args,**kw)
        # now we actually render ourselves
        return t.output(t.node,*args,**kw)

InitializeClass(ZopeTwiddlerCopy)
