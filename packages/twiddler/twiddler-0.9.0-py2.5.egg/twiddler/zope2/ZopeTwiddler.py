## Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view,view_management_screens,webdav_access
from Acquisition import aq_base
from cPickle import dumps,loads
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from twiddler import Twiddler,html_quote
from twiddler.input.filewrapper import FileWrapper
from twiddler.input.plaintext import PlainText
from twiddler.zope2 import interfaces
from twiddler.zope2.permissions import manage_twiddler
from twiddler.zope2.ZopeTwiddlerCopy import ZopeTwiddlerCopy
from zope.component import getUtilitiesFor,getUtility
from zope.event import notify
from zope.app.container.contained import ObjectModifiedEvent
    
# we mix in SimpleItem - when in Rome...

class ZopeTwiddler(Twiddler,SimpleItem,PropertyManager):
    "A Zope 2 wrapping for Twiddler"
    
    meta_type = 'Twiddler'
    title = ''
    manage_options = (
        {'label':'Source', 'action':'sourceForm'},
        {'label':'Configure', 'action':'configureForm'},
        {'label':'Test', 'action':''},
        ) + PropertyManager.manage_options \
          + SimpleItem.manage_options
          
    security = ClassSecurityInfo()

    security.declareObjectProtected(view)
    
    def __init__(self,id,*args,**kw):
        # many things in Zope 2 still rely on an id attribute :-(
        self.__name__ = self.id = id
        Twiddler.__init__(self,*args,**kw)

    index_html = None
    
    security.declareProtected(view,'render')
    security.declareProtected(view,'__call__')
    def __call__(self):
        "render this Twiddler"
        return self.clone().render()

    # we explicity handle id stuff to be sure
    security.declarePublic('getId')
    def getId(self):
        return self.__name__

    def _setId(self,new_id):
        self.__name__ = self.id = new_id

    security.declareProtected(manage_twiddler,'setSource')
    def setSource(self,source,REQUEST=None):
        "edit the source of this Twiddler"
        Twiddler.setSource(self,source)
        self.source=source
        notify(ObjectModifiedEvent(self))
        if REQUEST is not None:
            return self.sourceForm(
                manage_tabs_message='Your changes have been saved!'
                )

    security.declareProtected(manage_twiddler,'setComponent')
    def setComponent(self,component,name,REQUEST=None):
        "replace the output of this Twiddler"
        ccomp = component.capitalize()
        setattr(self,component,
                getUtility(getattr(interfaces,'I%sFactory'%ccomp),name)())
        if component in ('input','executor'):
            Twiddler.setSource(self,self.source)
        if REQUEST is not None:
            return self.configureForm(
                manage_tabs_message=ccomp+' replaced!'
                )

    security.declareProtected(manage_twiddler,'configureComponent')
    def configureComponent(self,component,REQUEST):
        "configure the output of this Twiddler"
        getattr(self,component).configure(REQUEST.form)
        if component in ('input','executor'):
            Twiddler.setSource(self,self.source)
        if REQUEST is not None:
            return self.configureForm(
                manage_tabs_message=component.capitalize()+' configured!'
                )

    # return a proxy that only requires view to mess with
    security.declareProtected(view,'clone')
    def clone(self):
        """Returns a clone of this Twiddler in its current state"""
        return ZopeTwiddlerCopy(loads(dumps(aq_base(self)))).__of__(self)

    # management interface forms and methods
    security.declareProtected(view_management_screens,'sourceForm')
    def sourceForm(self,manage_tabs_message=None):
        "The form for editing the twiddler source"
        t = sourceFormTemplate.clone()
        t['header'].replace(self.manage_page_header())
        t['tabs'].replace(self.manage_tabs(manage_tabs_message=manage_tabs_message))
        t['footer'].replace(self.manage_page_footer())
        t['action'].replace(self.absolute_url()+'/setSource')
        t['body'].replace(self.source,filters=(html_quote,))
        return t.render()

    security.declareProtected(view_management_screens,'configureForm')
    def configureForm(self,manage_tabs_message=None):
        "The form for editing the configuration of this Twiddler"
        t = configureFormTemplate.clone()
        url = self.absolute_url()
        # hide the other outer tag 'cos we're using the default parser
        # here ;-)
        t['container'].replace(tag=False)
        # dtml bits
        t['header'].replace(self.manage_page_header())
        t['tabs'].replace(self.manage_tabs(manage_tabs_message=manage_tabs_message))
        t['footer'].replace(self.manage_page_footer())
        # configure bits
        template_form = t['form'].repeater()
        for name in ('input','executor','output'):
            cname = name.capitalize()
            form = template_form.repeat(name=False)
            component = getattr(self,name)
            # title
            form['title'].replace(cname,name=False)
            # show
            form['repr'].replace(component,id=False,filters=(html_quote,))
            # configure
            cform = form['configure']
            if interfaces.IConfigurableComponent.providedBy(component):
                cform.replace(id=False,action=url+'/configureComponent')
                cform['component'].replace(value=name)
                cform['slot'].replace(component.configureForm(),tag=False)
            else:
                cform.remove()
            # select
            sform = form['select']
            sform.replace(id=False,action=url+'/setComponent')
            sform['component'].replace(value=name)
            option = sform['option'].repeater()
            for name,input in getUtilitiesFor(getattr(interfaces,'I%sFactory'%cname)):
                option.repeat(name,id=False,value=name)
        # return the rendered html
        return t.render()
        
    # webdav bits
    security.declareProtected(view,'get_size')
    def get_size(self):
        "return the size of our webdav representation"
        return len(self.source)
    
    security.declareProtected(webdav_access,'manage_DAVget')
    def manage_DAVget(self):
        "Gets the document source"
        return self.source

    security.declareProtected(manage_twiddler,'PUT')
    def PUT(self, REQUEST, RESPONSE):
        """ Handle HTTP PUT requests """
        self.dav__init(REQUEST, RESPONSE)
        self.dav__simpleifhandler(REQUEST, RESPONSE, refresh=1)
        self.setSource(REQUEST.get('BODY', ''))
        RESPONSE.setStatus(204)
        return RESPONSE

InitializeClass(ZopeTwiddler)

sourceFormTemplate = ZopeTwiddler('sourceForm',
                                  'sourceForm.twiddler',
                                  input=FileWrapper(PlainText,__file__),
                                  filters=())

configureFormTemplate = ZopeTwiddler('configureForm',
                                     'configureForm.twiddler',
                                     input=FileWrapper(prefix=__file__),
                                     filters=())
    
