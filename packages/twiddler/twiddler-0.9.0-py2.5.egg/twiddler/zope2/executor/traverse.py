# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from Acquisition import Implicit
from Persistence import Persistent
from twiddler import Twiddler
from twiddler.interfaces import IExecutor
from twiddler.zope2.interfaces import IConfigurableComponent
from zope.interface import implements

form = Twiddler('''<div>
Path: <input name="path" value=""/>
</div>''')

class Traverse(Persistent,Implicit):

    implements(IExecutor,IConfigurableComponent)

    def __init__(self,path=''):
        self.path = path
        
    def __call__(self,*args,**kw):
        return self.unrestrictedTraverse(self.path)(*args,**kw)

    def configureForm(self):
        t = form.clone()
        t['path'].replace(value=self.path)
        return t.render()

    def configure(self,form):
        self.path = form['path']
