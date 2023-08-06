"""\
@file stacked_test.py
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



from eventlet import api
from eventlet import channel
from eventlet import coros
from eventlet import httpc
from eventlet import httpd
from eventlet import processes

import greenlet

from mulib import mu
from mulib import nodes
from mulib import stacked
from mulib import tests


class TestConsume(tests.FakeRequestCase):
    mode = 'static'
    def test_simple(self):
        result = self.consume("hello")
        self.assertEquals(
            result, "hello")

    def test_missing(self):
        result = self.consume("hello", 'missing_segment')
        self.assertEquals(result, tests.NOT_FOUND)

    def test_sequence(self):
        self.assertEquals(
            self.consume(['a', 'b'], '0'), 'a')
        self.assertEquals(
            self.consume(['a', 'b'], '1'), 'b')
        self.assertEquals(
            self.consume(['a', 'b'], '9'), tests.NOT_FOUND)
        self.assertEquals(
            self.consume(('a', 'b'), '0'), 'a')
        self.assertEquals(
            self.consume(('a', 'b'), '1'), 'b')
        self.assertEquals(
            self.consume(('a', 'b'), '9'), tests.NOT_FOUND)

    def test_dict(self):
        self.assertEquals(
            self.consume({'hello': 'world'}, 'hello'), 'world')

    def test_dict_missing(self):
        self.assertEquals(
            self.consume({'hello': 'world'}, 'goodbye'), tests.NOT_FOUND)

    def test_nesting(self):
        nested_lists = [['a1', 'a2'], ['b1', 'b2']]
        self.assertEquals(
            self.consume(nested_lists, 0, 0), 'a1')
        self.assertEquals(
            self.consume(nested_lists, 1, 0), 'b1')

        nested_dicts = {
            'hello': {'world': 'hi'},
            'goodbye': {'now': 'bye'}}

        self.assertEquals(
            self.consume(nested_dicts, 'hello', 'world'), 'hi')

        self.assertEquals(
            self.consume(nested_dicts, 'goodbye', 'now'), 'bye')

    def test_none(self):
        self.assertEquals(self.consume(None, 'not'), tests.NOT_FOUND)
        self.assertEquals(self.consume([None], '0'), tests.NOT_FOUND)
        self.assertEquals(
            self.consume({'hello': None}, 'hello'), tests.NOT_FOUND)
        self.assertEquals(
            self.consume({'hello': None}, 'hello', 'world'),
            tests .NOT_FOUND)

    def test_set(self):
        root = {}
        self.req(root, tests.PUT, 'world', 'hello')
        self.assertEquals(root, {'hello':'world'})
        self.assertEquals(self.consume(root, 'hello'), 'world')

        root = {}
        self.req(root, tests.PUT, {'b': 1}, 'a')
        self.assertEquals(root, {'a' : {'b' : 1}})
        self.assertEquals(self.consume(root, 'a', 'b'), '1')

        root = []
        result_body, reqsult = self.req_(root, tests.PUT, 'hello', 'last')
        self.assertEquals(reqsult.get_outgoing_header('location'), '0')
        self.assertEquals(root, ['hello'])
        self.assertEquals(self.consume(root, '0'), 'hello')

        root = []
        result_body, reqsult = self.req_(root, tests.PUT, 'fail', '0')
        self.assertEquals(reqsult.status, 403)

        root = ['a', 'd', 'c']
        self.req(root, tests.PUT, 'b', '1')
        self.assertEquals(root, ['a', 'b', 'c'])

    def test_delete(self):
        root = {'hello': 'world'}
        self.req(root, tests.DELETE, '', 'hello')
        self.assertEquals(self.consume(root, 'hello'), tests.NOT_FOUND)
        ## Deleting something that is not there doesn't raise exception
        self.req(root, tests.DELETE, '', 'hello')

        root = ['a', 'b', 'c']
        self.req(root, tests.DELETE, '', '1')
        self.assertEquals(self.consume(root, '1'), 'c')
        ## Deleting something that is not there doesn't raise exception
        self.req(root, tests.DELETE, '', '6')

    def test_object(self):
        class world(object):
            def produce(self, req):
                req.write('world')

            def consume(self, req, segs):
                req.write('/'.join(segs))
        stacked.add_producer(world, world.produce)
        stacked.add_consumer(world, world.consume)

        root = {'hello': world()}
        self.assertEquals(self.consume(root, 'hello'), 'world')

        self.assertEquals(
            self.consume(root, 'hello', 'foo', 'bar', 'baz'),
            'foo/bar/baz')

    def test_leaf_object(self):
        class leaf(object):
            def produce(self, req):
                req.write('goodbye')
        stacked.add_producer(leaf, leaf.produce)

        self.assertEquals(self.consume(leaf(), 'hello'), tests.NOT_FOUND)
        self.assertEquals(self.consume(leaf()), 'goodbye')

    def test_object_attribute(self):
        class foo(object):
            bar = 'baz'

        self.assertEquals(self.consume(foo(), 'bar'), 'baz')

    def test_set_delete_object(self):
        class foo(object):
            hi = 'no'

        root = foo()
        self.req(root, tests.PUT, 'there', 'hi')
        self.assertEquals(root.hi, 'there')

        self.req(root, tests.DELETE, '', 'hi')
        self.assertEquals(root.hi, 'no')


class TestServerSimple(tests.TestServer):
    mode = 'static'
    def test_root(self):
        self.assertEquals(
            httpc.get('http://localhost:9000/'), 'hello')

    def test_404(self):
        self.assertRaises(
            httpc.NotFound, httpc.get, 'http://localhost:9000/foo')

    def test_uncaught_exception(self):
        # hide stderr
        import sys
        temp_ = sys.stderr
        sys.stderr = tests.NullSTDOut()
        try:
            class bar(object):
                def produce(self, req):
                    raise RuntimeError('the test passes if you see this!')

            stacked.add_producer(bar, bar.produce)

            self.site.root['bar'] = bar()
            self.assertRaises(
                httpc.InternalServerError, httpc.get, 'http://localhost:9000/bar')
        finally:
            sys.stderr = temp_

    def test_add_parser(self):
        loc = 'http://localhost:9000/bop'
        self.site.parsers['application/x-mmm-bop'] = lambda x: x[::-1]
        httpc.put(
            loc,
            'foo',
            content_type='application/x-mmm-bop')

        self.assertEquals(
            httpc.get(loc), 'oof')

    def skip_test_ab(self):
        self.site.root['foo'] = dict(bar=dict(baz='hello'))
        url = 'http://localhost:9000/foo/bar/baz'
        out = processes.Process('/usr/sbin/ab', ['-c','64','-n','1024', '-k', url])
        print out.read()


class TestResource(tests.TestServer):
    mode = 'static'
    def setUp(self):
        super(TestResource, self).setUp()
        self.evt = coros.event()
        self.resource = mu.Resource()
        self.site.root['resource'] = self.resource
        self.resource.template = "Hello World!"
        self.resource.child_will = mu.Resource()
        self.resource.child_will.template = "should not see"
        should_see = mu.Resource()
        should_see.template = "should see"
        self.resource.child_will.willHandle = lambda _: should_see
        def afterHandle(req):
            self.evt.send()
        self.resource.afterHandle = afterHandle
        self.resource.child_foo = mu.Resource()
        self.resource.child_foo.template = "Foo!"

    def test_simple(self):
        result = httpc.get('http://localhost:9000/resource')
        self.assertEquals(result, "Hello World!")

    def test_traversal(self):
        result = httpc.get('http://localhost:9000/resource/foo')
        self.assertEquals(result, "Foo!")

    def test_will_and_after_handle(self):
        result = httpc.get('http://localhost:9000/resource/will')
        cancel = api.exc_after(5, RuntimeError)
        self.evt.wait()
        cancel.cancel()
        self.assertEquals(result, "should see")
        

if __name__ == '__main__':
    tests.main()

