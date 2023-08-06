## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view
from Acquisition import Explicit
from Globals import InitializeClass
from twiddler.interfaces import IRepeater
from zope.interface import implements

class ZopeTwiddlerRepeater(Explicit):

    implements(IRepeater)

    def __init__(self,e):
        self.r = e.repeater()
    
    security = ClassSecurityInfo()

    security.declareObjectProtected(view)
    
    security.declareProtected(view,'repeat')
    def repeat(self,*args,**kw):
        "Proxy for TwiddlerRepeater.repeat"
        # import here to avoid import loop
        from twiddler.zope2.ZopeTwiddlerCopyElement import ZopeTwiddlerCopyElement
        return ZopeTwiddlerCopyElement(self.r.repeat(*args,**kw)).__of__(self)
    
InitializeClass(ZopeTwiddlerRepeater)
    
