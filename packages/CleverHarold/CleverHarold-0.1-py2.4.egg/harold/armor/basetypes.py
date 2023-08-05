#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 The Incorporated Wizzo Widget Works
# Distributed under the terms of the GNU General Public License v2
# Author: Troy Melhase <troy@gci.net>

##
# Helper module for using builtin types as validators.
#
# The getargspec function in the inspect module does not work with
# builtin types.  Since there is no way to introspect the type for
# their call signatures, we provide rough equivalents to them here as
# functions that can be inspected.
#
# Method signatures do not match type signatures in all cases.
# Particularly, slice and xrange signatures are only close.  Better
# implementations are possible, but their worth is questionable.
#
##


class marker:
    pass


def _bool(x=False):
    return bool(x)


def _buffer(object, offset=0, size=-1):
    return buffer(object, offset, size)


def _classmethod(function):
    return classmethod(function)


def _complex(real, imag=0):
    return complex(real, imag)


def _dict(initial=marker, **kwds):
    if initial is marker and not kwds:
        return dict()
    elif initial is marker:
        return dict(**kwds)
    else:
        return dict(initial)


def _enumerate(iterable):
    return enumerate(iterable)


def _file(name, mode='r', buffering=marker):
    if buffering is marker:
        return file(name, mode)
    return file(name, mode, buffering)


def _float(x=0.0):
    return float(x)


def _frozenset(iterable=marker):
    if iterable is marker:
        iterable = []
    return frozenset(iterable)


def _int(x=0, base=marker):
    if base is marker:
        return int(x)
    else:
        return int(x, base)


def _list(initial=marker):
    if initial is marker:
        return list()
    else:
        return list(initial)


def _long(x=0, base=marker):
    if base is marker:
        return long(x)
    else:
        return long(x, base)


def _object():
    return object()


def _property(fget=None, fset=None, fdel=None, doc=None):
    return property(fget, fset, fdel, doc)


def _reversed(sequence):
    return reversed(sequence)


def _set(iterable=marker):
    if iterable is marker:
        iterable = []
    return set(iterable)


def _slice(start=None, stop=0, step=None):
    return slice(start, stop, step)


def _staticmethod(function):
    return staticmethod(function)


def _str(object=''):
    return str(object)


def _super(typ, typ2=marker):
    if typ2 is marker:
        return super(type)
    return super(typ, typ2)


def _tuple(sequence=marker):
    if sequence is marker:
        return tuple()
    return tuple(sequence)


def _type(object_or_name, bases=marker, namespace=marker):
    if bases is marker and namespace is marker:
        return type(object_or_name)
    if bases is marker:
        bases = ()
    if namespace is marker:
        namespace = {}
    return type(object_or_name, bases, namespace)


def _unicode(string, encoding=marker, errors=marker):
    if encoding is marker and errors is marker:
        return unicode(string)
    if errors is marker:
        return unicode(string, encoding)
    return unicode(string, encoding, errors)


def _xrange(start=marker, stop=None, step=marker):
    if start is marker and step is marker:
        return xrange(stop)
    if step is marker:
        return xrange(start, stop)
    return xrange(start, stop, step)


##
# A mapping of builtin types to inspectable wrapper functions.

basetypes = {
    # basestring cannot be instantiated
    bool : _bool,
    buffer : _buffer,
    classmethod : _classmethod,
    complex : _complex,
    dict : _dict,
    enumerate : _enumerate,
    file : _file,
    float : _float,
    frozenset : _frozenset,
    int : _int,
    list : _list,
    long : _long,
    object : _object,
    property : _property,
    reversed : _reversed,
    set : _set,
    slice : _slice,
    staticmethod : _staticmethod,
    str : _str,
    super : _super,
    tuple : _tuple,
    type : _type,
    unicode : _unicode,
    xrange : _xrange,
    }
