
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
    old = var._ScopedVariable__stack[scope]
    try:
        var._ScopedVariable__stack[scope] = value
        yield
    finally:
        var._ScopedVariable__stack[scope] = old


class ProxyBase(object):
    # taken from werkzeug.local.LocalProxy
    __slots__ = ()
    @property
    def __dict__(self):
        try:
            return self._current_object_.__dict__
        except RuntimeError:
            return AttributeError('__dict__')

    def __repr__(self):
        try:
            obj = self._current_object_
        except RuntimeError:
            return '<%s unbound>' % self.__class__.__name__
        return repr(obj)

    def __nonzero__(self):
        try:
            return bool(self._current_object_)
        except RuntimeError:
            return False

    def __unicode__(self):
        try:
            return unicode(self._current_object_)
        except RuntimeError:
            return repr(self)

    def __dir__(self):
        try:
            return dir(self._current_object_)
        except RuntimeError:
            return []

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self._current_object_)
        return getattr(self._current_object_, name)

    def __setitem__(self, key, value):
        self._current_object_[key] = value

    def __delitem__(self, key):
        del self._current_object_[key]

    def __setslice__(self, i, j, seq):
        self._current_object_[i:j] = seq

    def __delslice__(self, i, j):
        del self._current_object_[i:j]

    __setattr__ = lambda x, n, v: setattr(x._current_object_, n, v)
    __delattr__ = lambda x, n: delattr(x._current_object_, n)
    __str__ = lambda x: str(x._current_object_)
    __lt__ = lambda x, o: x._current_object_ < o
    __le__ = lambda x, o: x._current_object_ <= o
    __eq__ = lambda x, o: x._current_object_ == o
    __ne__ = lambda x, o: x._current_object_ != o
    __gt__ = lambda x, o: x._current_object_ > o
    __ge__ = lambda x, o: x._current_object_ >= o
    __cmp__ = lambda x, o: cmp(x._current_object_, o)
    __hash__ = lambda x: hash(x._current_object_)
    __call__ = lambda x, *a, **kw: x._current_object_(*a, **kw)
    __len__ = lambda x: len(x._current_object_)
    __getitem__ = lambda x, i: x._current_object_[i]
    __iter__ = lambda x: iter(x._current_object_)
    __contains__ = lambda x, i: i in x._current_object_
    __getslice__ = lambda x, i, j: x._current_object_[i:j]
    __add__ = lambda x, o: x._current_object_ + o
    __sub__ = lambda x, o: x._current_object_ - o
    __mul__ = lambda x, o: x._current_object_ * o
    __floordiv__ = lambda x, o: x._current_object_ // o
    __mod__ = lambda x, o: x._current_object_ % o
    __divmod__ = lambda x, o: x._current_object_.__divmod__(o)
    __pow__ = lambda x, o: x._current_object_ ** o
    __lshift__ = lambda x, o: x._current_object_ << o
    __rshift__ = lambda x, o: x._current_object_ >> o
    __and__ = lambda x, o: x._current_object_ & o
    __xor__ = lambda x, o: x._current_object_ ^ o
    __or__ = lambda x, o: x._current_object_ | o
    __div__ = lambda x, o: x._current_object_.__div__(o)
    __truediv__ = lambda x, o: x._current_object_.__truediv__(o)
    __neg__ = lambda x: -(x._current_object_)
    __pos__ = lambda x: +(x._current_object_)
    __abs__ = lambda x: abs(x._current_object_)
    __invert__ = lambda x: ~(x._current_object_)
    __complex__ = lambda x: complex(x._current_object_)
    __int__ = lambda x: int(x._current_object_)
    __long__ = lambda x: long(x._current_object_)
    __float__ = lambda x: float(x._current_object_)
    __oct__ = lambda x: oct(x._current_object_)
    __hex__ = lambda x: hex(x._current_object_)
    __index__ = lambda x: x._current_object_.__index__()
    __coerce__ = lambda x, o: x.__coerce__(x, o)
    __enter__ = lambda x: x.__enter__()
    __exit__ = lambda x, *a, **kw: x.__exit__(*a, **kw)


class ScopedVariable(ProxyBase):
    __slots__ = '__last', '__indent_stacks', '__dict__'
    def __init__(self, 
            default=_missing,
            scope_func = thread_concurrent_scope):
        object.__setattr__(self, '_ScopedVariable__last', default)
        object.__setattr__(self, '_ScopedVariable__stack', defaultdict(list))
        object.__setattr__(self, '_ScopedVariable__scope', scope_func)

    @property
    def _current_object_(self):
        ident = self.__scope()
        current = self.__stack.get(ident, self.__last)
        if current is _missing:
            raise RuntimeError, "unbound scoped var %r"%self
        return current

scoped = ScopedVariable
