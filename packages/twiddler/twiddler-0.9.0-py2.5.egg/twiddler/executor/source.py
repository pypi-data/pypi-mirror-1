# Copyright (c) 2006 Simplistix Ltd
#
# This Software is released under the MIT License:
# http://www.opensource.org/licenses/mit-license.html
# See license.txt for more details.

from copy import copy

class Source:

    function = None
    
    def __init__(self,source,name=None):
        self.source = source
        self.name = name
        self._compile()

    def __getstate__(self):
        state = copy(self.__dict__)
        if state.has_key('function'):
            del state['function']
        return state
        
    def __setstate__(self,__dict__):
        self.__dict__.update(__dict__)
        self._compile()

    def __call__(self,*args,**kw):
        return self.function(*args,**kw)
    
    def _compile(self):
        d = {}
        exec self.source in d
        if self.name is None:
            if len(d)>2:
                raise SyntaxError(
                    'Only one function may be defined in a code block.'
                    )
            for k,v in d.items():
                if not k.startswith('_'):
                    self.function = v
                    break
        else:
            self.function = d[self.name]
            
        
