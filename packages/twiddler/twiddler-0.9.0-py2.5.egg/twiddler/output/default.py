# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from elementtree.ElementTree import Comment
from elementtree.ElementTree import _escape_cdata
from elementtree.ElementTree import ProcessingInstruction
from elementtree.ElementTree import QName
from elementtree.ElementTree import _raise_serialization_error
from twiddler.elementtreeplus import DocType
from twiddler.elementtreeplus import XMLDeclaration
from twiddler.interfaces import IOutput
from zope.interface import directlyProvides

def _render(output, node, namespaces):
    tag = node.tag
    if tag is Comment:
        output.append(u"<!--%s-->" % _escape_cdata(node.text))
    elif tag is ProcessingInstruction:
        output.append(u"<?%s?>" % _escape_cdata(node.text))
    elif tag in (XMLDeclaration,DocType):
        output.append(node.text)
    elif tag is False:
        if node.text:
            output.append(node.text)
        for n in node:
            _render(output,n,namespaces)
    else:
        items = node.items()
        xmlns_items = [] # new namespaces in this scope
        try:
            if isinstance(tag, QName) or tag[:1] == "{":
                tag, xmlns = fixtag(tag, namespaces)
                if xmlns: xmlns_items.append(xmlns)
        except TypeError:
            _raise_serialization_error(tag)            
        output.append(u"<" + tag)
        if items or xmlns_items:
            items.sort() # lexical order
            for k, v in items:
                try:
                    if isinstance(k, QName) or k[:1] == "{":
                        k, xmlns = fixtag(k, namespaces)
                        if xmlns: xmlns_items.append(xmlns)
                except TypeError:
                    _raise_serialization_error(k)
                try:
                    if isinstance(v, QName):
                        v, xmlns = fixtag(v, namespaces)
                        if xmlns: xmlns_items.append(xmlns)
                except TypeError:
                    _raise_serialization_error(v)
                output.append(u" %s=\"%s\"" % (k,v))
            for k, v in xmlns_items:
                output.append(u" %s=\"%s\"" % (k,v))
        if node.text or len(node):
            output.append(u">")
            if node.text:
                output.append(node.text)
            for n in node:
                _render(output,n,namespaces)
            output.append(u"</" + tag + u">")
        else:
            output.append(u" />")
        for k, v in xmlns_items:
            del namespaces[v]
    if node.tail:
        output.append(node.tail)

def Default(root,*args,**kw):
    """Default output renderer"""
    output = []
    _render(output, root._root, {})
    return u''.join(output)
        
directlyProvides(Default,IOutput)
    
