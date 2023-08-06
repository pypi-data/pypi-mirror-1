"""\
@file shaped_test.py
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

#from eventlet import pylibsupport
#pylibsupport.emulate()
from eventlet import util
util.wrap_socket_with_coroutine_socket()


import unittest

from mulib import shaped

from eventlet import api
from eventlet import channel
from eventlet import httpc
from eventlet import httpd


class TestShaped(unittest.TestCase):
    mode = 'static'
    def test_shaped(self):
        self.assertEquals(
            shaped.shaped("hello", str),
            True)
        self.assertEquals(
            shaped.shaped(1, int),
            True)
        self.assertEquals(
            shaped.shaped([1, 2, 3], [int]),
            True)

    def test_not_shaped(self):
        self.assertRaises(
            shaped.TypeMismatch,
            shaped.shaped_exc, 1, str)
        self.assertRaises(
            shaped.TypeMismatch, 
            shaped.shaped_exc, [1, 2, 3], bool)
        self.assertRaises(
            shaped.TypeMismatch, 
            shaped.shaped_exc, {'hello': 'world'}, int)
        self.assertEqual(
            shaped.shaped(1, bool),
            False)

    def test_dict_shape(self):
        self.assertEquals(
            shaped.shaped({'foo': 1}, {'foo': int}),
            True)

    def test_dict_not_shaped(self):
        self.assertRaises(
            shaped.KeyMismatch,
            shaped.shaped_exc, {'bar': 1}, {'foo': int})

    def test_list_shape(self):
        self.assertEquals(
            shaped.shaped([1, 2, 3], [int]),
            True)

    def test_list_not_shaped(self):
        self.assertRaises(
            shaped.TypeMismatch,
            shaped.shaped_exc, [1, 2], [str])

    def test_tuple_shaped(self):
        self.assertEquals(
            shaped.shaped(
                (1, "hello", True), (int, str, bool)),
            True)

    def test_tuple_not_shaped(self):
        self.assertRaises(
            shaped.SizeMismatch,
            shaped.shaped_exc,
            (1, "hello", True), (int, str))
        self.assertRaises(
            shaped.SizeMismatch,
            shaped.shaped_exc,
            (1, "hello", True), (int, str, bool, int))

        self.assertRaises(
            shaped.TypeMismatch,
            shaped.shaped_exc,
            (1, "hello", True), (int, str, str))

    def test_deep_nesting(self):
        self.assertEquals(
            shaped.shaped(
                {'hello': 1, 'world': [{'abc': 'def'}, {'abc': 'def'}]},
                {'hello': int, 'world': [{'abc': str}]}),
            True)

    def test_exact_match(self):
        self.assertEquals(
            shaped.shaped(
                {'hello': 'world'}, {'hello': 'world'}),
            True)

    def test_exact_mismatch(self):
        self.assertRaises(
            shaped.PredicateMismatch, shaped.shaped_exc,
            {'hello': 'world'}, {'hello': 'something'})

    def test_predicate_match(self):
        self.assertEquals(
            shaped.shaped(
                {'hello': 'world'},
                {'hello': lambda x: x.startswith('w')}),
            True)

    def test_predicate_mismatch(self):
        self.assertRaises(
            shaped.PredicateMismatch,
            shaped.shaped_exc,
            {'hello': 'something'},
            {'hello': lambda x: x.startswith('w')})


class TestMakeShape(unittest.TestCase):
    mode = 'static'
    def test_simple(self):
        self.assertEquals(shaped.make_shape(1), int)

    def test_dict(self):
        self.assertEquals(
            shaped.make_shape({'hello': 'world'}),
            {'hello': str})

    def test_list(self):
        self.assertEquals(
            shaped.make_shape({'foo': ["one", "two", "three"]}),
            {'foo': [str]})

    def test_tuple(self):
        self.assertEquals(
            shaped.make_shape({'bar': (1, "hello", True)}),
            {'bar': (int, str, bool)})

    def test_nest(self):
        self.assertEquals(
            shaped.make_shape(
                {'foo': [{'bar': 1}, {'bar': 2}],
                'baz': ({'bamf': 'hello'}, 5)}),
            {'foo': [{'bar': int}], 'baz': ({'bamf': str}, int)}) 

    def test_malformed(self):
        self.assertRaises(
            shaped.AmbiguousShape,
            shaped.make_shape,
            {'hello': []})
        self.assertRaises(
            shaped.HeterogenousList,
            shaped.make_shape,
            [1, 'hi'])


class TestWouldRetainShape(unittest.TestCase):
    mode = 'static'
    def test_function_shape(self):
        self.assert_(
            shaped.would_retain_shape(int, 5, (), '9'))
        self.assert_(
            not shaped.would_retain_shape(int, 5, (), 'hello'))

    def test_list(self):
        self.assert_(
            shaped.would_retain_shape([int], [1, 2], ('1', ), '9'))
        self.assert_(
            not shaped.would_retain_shape([int], [1, 2], ('1', ), 'hello'))

    def test_dict(self):
        self.assert_(
            shaped.would_retain_shape(
                {'hello': int}, {'hello': 1}, ('hello', ), '9'))
        self.assert_(
            not shaped.would_retain_shape(
                {'hello': int}, {'hello': 1}, ('hello', ), 'hello'))

    def test_nesting(self):
        self.assert_(
            shaped.would_retain_shape(
                {'hello': [{'goodbye': int}]},
                {'hello': [{'goodbye': 1}, {'goodbye': 2}]},
                ('hello', '1', 'goodbye'), '9'))
        self.assert_(
            not shaped.would_retain_shape(
                {'hello': [{'goodbye': int}]},
                {'hello': [{'goodbye': 1}, {'goodbye': 2}]},
                ('hello', '1', 'goodbye'), 'hello'))

    def test_any(self):
        self.assert_(
            shaped.would_retain_shape(
                shaped.any,
                {'hello': [{'goodbye': 1}, {'goodbye': 2}]},
                ('hello', '1', 'goodbye'), '9'))

if __name__ == '__main__':
    unittest.main()

