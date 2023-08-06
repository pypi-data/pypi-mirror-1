"""\
@file shaped.py
@author Donovan Preston

Copyright (c) 2007, Linden Research, Inc.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


import traceback


CONTAINER_TYPES = [dict, list, tuple]


class ShapeMismatch(Exception):
    pass


class TypeMismatch(ShapeMismatch):
    pass


class KeyMismatch(ShapeMismatch):
    pass


class SizeMismatch(ShapeMismatch):
    pass


class PredicateMismatch(ShapeMismatch):
    pass


def shaped(thing, shape):
    try:
        shaped_exc(thing, shape)
        return True
    except ShapeMismatch:
        return False


isshaped = shaped


def shaped_exc(thing, shape):
    if type(shape) in CONTAINER_TYPES:
        shape_type = type(shape)

        if shape_type is dict:
            for name in shape:
                if name not in thing:
                    raise KeyMismatch(
                        "key %r (for shape %s) was not in dict (%s)" % (
                            name, shape, thing))
                subitem = thing[name]
                subtype = shape[name]
                shaped_exc(subitem, subtype)
        elif shape_type is list:
            subtype = shape[0]
            for subitem in thing:
                shaped_exc(subitem, subtype)
        elif shape_type is tuple:
            if len(thing) != len(shape):
                raise SizeMismatch(
                    "wrong number of items in %s (for shape %s); "
                    "expected %s items" % (
                    thing, shape, len(shape)))

            subitem_iter = iter(thing)
            for subtype in shape:
                subitem = subitem_iter.next()
                shaped_exc(subitem, subtype)
        return
    elif type(shape) is not type:
        if callable(shape):
            if shape(thing):
                ## The predicate matches
                return
            raise PredicateMismatch(
                "predicate %r does not match (%r)" % (shape, thing))
        elif thing == shape:
            ## It's an exact match
            return
        raise PredicateMismatch(
            "shape %r was not matched (%r)" % (shape, thing))
    else:
        if not isinstance(thing, shape):
            raise TypeMismatch("type %r does not match %r (%s)" % (
                thing, type(shape), type(thing)))


class MalformedShape(Exception):
    pass


class AmbiguousShape(MalformedShape):
    pass


class HeterogenousList(MalformedShape):
    pass


def make_shape(what):
    what_type = type(what)
    if what_type is dict:
        shape = {}
        for key, value in what.items():
            shape[key] = make_shape(value)
        return shape
    elif what_type is list:
        if not len(what):
            raise AmbiguousShape(
                "Shape of item with list of zero elements "
                "cannot be determined")
        subtype = type(what[0])
        for subitem in what[1:]:
            if type(subitem) is not subtype:
                raise HeterogenousList(
                    "List items must be of homogenous type.")
        return [make_shape(what[0])]
    elif what_type is tuple:
        return tuple(map(make_shape, what))
    else:
        return type(what)


def any(item):
    return any


def _would_retain_shape(shape, data, segs, leaf):
    if not len(segs):
        ## TODO this still isn't quite right... if shape is callable,
        ## we need to call it, otherwise we need to call shaped(leaf, shape)
        ## instead. but it's good enough for this checkin
        shape(leaf)
        return

    if callable(shape):
        child = shape(data)
        segs = segs[1:]
    elif isinstance(shape, dict):
        seg = segs[0]
        if seg in shape:
            shape = shape[seg]
        elif str in shape:
            shape = shape[str]
        else:
            raise ShapeMismatch

        child = data.get(seg, '')
        segs = segs[1:]
    elif isinstance(shape, (list, tuple)):
        index = int(segs[0])
        if len(data) > index:
            child = data[index]
        else:
            child = ''
        shape = shape[0]
        segs = segs[1:]

    _would_retain_shape(shape, child, segs, leaf)


def would_retain_shape(shape, data, segs, leaf, debug=True):
    try:
        _would_retain_shape(shape, data, segs, leaf)
    except Exception, e:
        if debug:
            traceback.print_exc()
        return False
    return True
