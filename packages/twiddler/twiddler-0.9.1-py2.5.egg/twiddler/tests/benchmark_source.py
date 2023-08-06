# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.
from twiddler.twiddler import Twiddler
from time import time

iterations = 10

def benchmark(source,compiler,runner):
    tsum = 0
    for i in range(iterations):
        t1 = time()
        compiled = compiler(source)
        t2 = time()
        tsum += (t2-t1)
    t_compile = tsum/iterations
    for i in range(iterations):
        t1 = time()
        runner(compiled)
        t2 = time()
        tsum += (t2-t1)
    t_run = tsum/iterations
    return t_compile,t_run
        
def benchmark1(compiler,runner):
    # oh the irony, using a Twiddler to generate the source for the benchmarks!
    t = Twiddler('''
    <root xmlns:tal="http://namespaces.zope.org/tal">
    <element name="e">
    <repeat name="rX" tal:repeat="i range(0,100,10)">
    <attributes name="aX" tal:attributes="attrib1 string:Attribute Value">
    <content name="cX" tal:content="string:My Content"/>
    </attributes>
    </repeat>
    </element>
    </root>
    ''')
    lengths = range(0,4,1)
    lengths[0]=1
    sequences = [range(i) for i in range(0,101,10)]
    e = t.getByName('e')
    i = 0
    for length in lengths:
        while i<length:
            si = str(i)
            new = e.repeat()
            new.getByName('rX').replace(name='r'+si)
            new.getByName('aX').replace(name='a'+si)
            new.getByName('cX').replace(name='c'+si)
            i+=1
        print t.render()
        print

benchmark1(None,None)
