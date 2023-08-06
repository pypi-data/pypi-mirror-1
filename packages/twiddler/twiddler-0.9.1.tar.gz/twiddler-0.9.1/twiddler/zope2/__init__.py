## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from twiddler.input.filewrapper import FileWrapper
from twiddler.input.plaintext import PlainText
try:
    from twiddler.zope2.ZopeTwiddler import ZopeTwiddler
    from twiddler.zope2.permissions import add_twiddler
except ImportError:
    # no Zope 2
    pass
else:
    addTwiddlerFormTemplate = ZopeTwiddler('addTwiddlerForm',
                                           'addTwiddlerForm.twiddler',
                                           input=FileWrapper(PlainText,__file__),
                                           filters=())

def initialize( context ):
    context.registerClass(
        ZopeTwiddler,
        # we use the same permission as page templates
        # in order to keep things simple.
        permission=add_twiddler,
        constructors=(addTwiddlerForm,
                      addTwiddler),
        icon='twiddler.gif',
        )


def addTwiddlerForm(context):
    "The Twiddler Add Form"
    t = addTwiddlerFormTemplate.clone()
    t['header'].replace(context.manage_page_header())
    t['form_title'].replace(context.manage_form_title(form_title='Add Twiddler'))
    t['footer'].replace(context.manage_page_footer())
    return t.render()
    
def addTwiddler(self,id,REQUEST=None):
    "Add a Twiddler to the container"
    # how to set all the parameters of a Twiddler?
    self._setObject(id,ZopeTwiddler(id,'<node id="test"/>'))
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/manage_main')
    
