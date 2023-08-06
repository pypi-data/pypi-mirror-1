# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
from twiddler.elementtreeplus import XML
from twiddler.executor.source import Source
from twiddler.interfaces import IInput
from re import compile as re_compile, DOTALL
from zope.interface import directlyProvides

code_re = re_compile('<!--twiddler(.+?)-->\n?',DOTALL)

class FoundIndent(Exception):
    pass

def Default(source,indexes):
    if isinstance(source,unicode):
        source = source.encode('utf-8')
    return XML(source,indexes=indexes),None

directlyProvides(Default,IInput)

def DefaultWithCodeBlock(source,indexes):
    # this stuff is butt ugly but does successfully extract the code
    # block and normalise the indentation. Improvements welcome!
    src = None
    c = code_re.search(source)
    if c:
        s = c.groups()[0]
        lines = []
        for line in s.split('\n'):
            if line.strip():
                lines.append(line.rstrip())
        i = 0
        try:
            while True:
                for line in lines:
                    if not line[i].isspace():
                        raise FoundIndent
                i+=1
        except FoundIndent:
            pass
        src = []
        for line in lines:
            src.append(line[i:])
        src = '\n'.join(src)+'\n'

        # now we just replace the code block with nothing        
        source = code_re.sub('',source)

    node,junk = Default(source,indexes=indexes)
    if src:
        executor = Source(src)
    else:
        executor = False
    return node,executor

directlyProvides(DefaultWithCodeBlock,IInput)
