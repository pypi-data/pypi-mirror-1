import threading, sys
from time import time
import pkg_resources
pkg_resources.require('lazypy')
from LazyEvaluation.Promises import PromiseMetaClass

# See: http://freshmeat.net/projects/lazypy/
# for a lazy evaluation metaclass
class tailfish(object):
    __metaclass__ = PromiseMetaClass
    def __init__(self,func,args,kw):
        self._func = func
        self._args = args
        self._kw = kw
    def __force__(self):
        return self.func(*self.args,**self.kw)

def tail(func):
    func._tail_state = threading.local()
    def helper(*args,**kw):
        if not hasattr(func._tail_state,'recur'):
            func._tail_state.recur = True
        else:
            return tailfish(func,args,kw)
        f = func
        try:
            while True:
                ret = f(*args,**kw)
                if isinstance(ret,tailfish):
                    f = ret._func
                    args = ret._args
                    kw = ret._kw
                else:
                    return ret
        finally:
            del func._tail_state.recur
    return helper

# See also: http://code.activestate.com/recipes/496691/

__all__ = ['tail']

