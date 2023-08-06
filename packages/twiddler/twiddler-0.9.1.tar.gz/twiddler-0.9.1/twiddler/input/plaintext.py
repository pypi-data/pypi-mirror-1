# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from twiddler.interfaces import IInput
from re import compile,DOTALL
from zope.interface import directlyProvides

sub_re = compile('\$(\w+)')
sec_re = compile('<(\w+)>(.*)</\\1>',DOTALL)
whitespace_re = compile('\s*')

from twiddler.elementtreeplus import ElementTreePlus,ElementPlus

def PlainText(source,indexes):
    tree = ElementTreePlus(indexes)
    root = ElementPlus(False,{})
    root._tree = tree
    tree._root = root
    source = unicode(source)
    process(root,source)
    return tree,None
    
directlyProvides(PlainText,IInput)

def handle_text(element,current,i,text):
    if i:
        if current.text.startswith('$'):
            tail = None
        else:
            m = whitespace_re.match(text)
            tail = m.group(0)
            text = text[m.end():]
        current.tail = tail
        if text:
            e = ElementPlus(False,{})
            e.text = text
            element.append(e)
            current = e
    else:
        element.text = text
    return current
    
def process(element,source):
    i = 0
    current = element
    while True:
        m = sub_re.search(source,i)
        n = sec_re.search(source,i)
        if m and n:
            if m.start()<n.start():
                n = None
            else:
                m = None
        match = m or n
        if match:
            current = handle_text(element,
                                  current,
                                  i,
                                  source[i:match.start()])
            new = ElementPlus(False,{'id':match.group(1)})
        if m:
            new.text = m.group(0)
            element.append(new)
            i = m.end()
            current = new
        elif n:
            process(new,n.group(2))
            element.append(new)
            current = new
            i = n.end()
        else:
            break
    current = handle_text(element,
                          current,
                          i,
                          source[i:])

