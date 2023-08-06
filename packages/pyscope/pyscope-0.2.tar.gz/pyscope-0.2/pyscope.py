
"""
    pyscope
    ~~~~~~~

    lisp-alike scoped vars for python

    >>> a = scoped(1)
    >>> a == 1
    True
    >>> with scope(a, 2):
    >>>     a == 2
    True


    :copyright: 2009 by Ronny Pfannschmidt
    :license: MIT
"""

_missing = object()
from collections import defaultdict

def no_concurrent_scope():
    return None

import threading

def thread_concurrent_scope():
    return threading.currentThread().ident


import contextlib

@contextlib.contextmanager
def scope(var, value):
    scope = var._ScopedVariable__scope()
    stack = var._ScopedVariable__stack[scope]
    try:
        stack.append(value)
        yield
    finally:
        stack.pop()


class ScopedVariable(object):
    __slots__ = '__last', '__indent_stacks', '__dict__'
    def __init__(self, 
            default=_missing,
            scope_func = thread_concurrent_scope):
        object.__setattr__(self, '_ScopedVariable__last', default)
        object.__setattr__(self, '_ScopedVariable__stack', defaultdict(list))
        object.__setattr__(self, '_ScopedVariable__scope', scope_func)

    @property
    def __current_object(self):
        ident = self.__scope()
        stack = self.__stack[ident]
        return stack[-1] if stack else self.__last

    # the rest is taken from werkzeug.local.LocalProxy

    @property
    def __dict__(self):
        try:
            return self.__current_object.__dict__
        except RuntimeError:
            return AttributeError('__dict__')

    def __repr__(self):
        try:
            obj = self.__current_object
        except RuntimeError:
            return '<%s unbound>' % self.__class__.__name__
        return repr(obj)

    def __nonzero__(self):
        try:
            return bool(self.__current_object)
        except RuntimeError:
            return False

    def __unicode__(self):
        try:
            return unicode(self.__current_object)
        except RuntimeError:
            return repr(self)

    def __dir__(self):
        try:
            return dir(self.__current_object)
        except RuntimeError:
            return []

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self.__current_object)
        return getattr(self.__current_object, name)

    def __setitem__(self, key, value):
        self.__current_object[key] = value

    def __delitem__(self, key):
        del self.__current_object[key]

    def __setslice__(self, i, j, seq):
        self.__current_object[i:j] = seq

    def __delslice__(self, i, j):
        del self.__current_object[i:j]

    __setattr__ = lambda x, n, v: setattr(x.__current_object, n, v)
    __delattr__ = lambda x, n: delattr(x.__current_object, n)
    __str__ = lambda x: str(x.__current_object)
    __lt__ = lambda x, o: x.__current_object < o
    __le__ = lambda x, o: x.__current_object <= o
    __eq__ = lambda x, o: x.__current_object == o
    __ne__ = lambda x, o: x.__current_object != o
    __gt__ = lambda x, o: x.__current_object > o
    __ge__ = lambda x, o: x.__current_object >= o
    __cmp__ = lambda x, o: cmp(x.__current_object, o)
    __hash__ = lambda x: hash(x.__current_object)
    __call__ = lambda x, *a, **kw: x.__current_object(*a, **kw)
    __len__ = lambda x: len(x.__current_object)
    __getitem__ = lambda x, i: x.__current_object[i]
    __iter__ = lambda x: iter(x.__current_object)
    __contains__ = lambda x, i: i in x.__current_object
    __getslice__ = lambda x, i, j: x.__current_object[i:j]
    __add__ = lambda x, o: x.__current_object + o
    __sub__ = lambda x, o: x.__current_object - o
    __mul__ = lambda x, o: x.__current_object * o
    __floordiv__ = lambda x, o: x.__current_object // o
    __mod__ = lambda x, o: x.__current_object % o
    __divmod__ = lambda x, o: x.__current_object.__divmod__(o)
    __pow__ = lambda x, o: x.__current_object ** o
    __lshift__ = lambda x, o: x.__current_object << o
    __rshift__ = lambda x, o: x.__current_object >> o
    __and__ = lambda x, o: x.__current_object & o
    __xor__ = lambda x, o: x.__current_object ^ o
    __or__ = lambda x, o: x.__current_object | o
    __div__ = lambda x, o: x.__current_object.__div__(o)
    __truediv__ = lambda x, o: x.__current_object.__truediv__(o)
    __neg__ = lambda x: -(x.__current_object)
    __pos__ = lambda x: +(x.__current_object)
    __abs__ = lambda x: abs(x.__current_object)
    __invert__ = lambda x: ~(x.__current_object)
    __complex__ = lambda x: complex(x.__current_object)
    __int__ = lambda x: int(x.__current_object)
    __long__ = lambda x: long(x.__current_object)
    __float__ = lambda x: float(x.__current_object)
    __oct__ = lambda x: oct(x.__current_object)
    __hex__ = lambda x: hex(x.__current_object)
    __index__ = lambda x: x.__current_object.__index__()
    __coerce__ = lambda x, o: x.__coerce__(x, o)
    __enter__ = lambda x: x.__enter__()
    __exit__ = lambda x, *a, **kw: x.__exit__(*a, **kw)

scoped = ScopedVariable
