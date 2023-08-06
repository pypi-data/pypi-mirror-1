"""\
@file nodes_test.py
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

from eventlet import api, httpc, util, coros
from mulib import nodes

from mulib import tests

util.wrap_socket_with_coroutine_socket()

class TestEntity(tests.FakeRequestCase):
    mode = 'static'
    def test_entity_consume(self):
        class foo(nodes.entity):
            bar = 'baz'

        self.assertEquals(
            self.consume(foo(), 'bar'), 'baz')

    def test_entity_produce(self):
        class bar(nodes.entity):
            bar = 1
        result = self.consume(bar())
        self.assertEquals(
            eval(result), {"bar": 1})

    def test_entity_set(self):
        class baz(nodes.entity):
            baz = 1
        root = baz()
        self.req(root, tests.PUT, 2, 'baz')
        self.assertEquals(root.baz, 2)
        self.req(root, tests.DELETE, '', 'baz')
        self.assertEquals(root.baz, 1)
        self.req(root, tests.DELETE, '', 'baz')
        self.assertEquals(
            self.consume(root, 'asdf'), tests.NOT_FOUND)

    def test_nested(self):
        class contained(nodes.entity):
            foo = 1

        class container(nodes.entity):
            child = contained()

        root = container()
        result = eval(self.consume(root))
        self.assertEquals(result, {'child': 'full_url/child'})


class TestNodeServer(tests.TestServer):
    mode = 'static'
    def setUp(self):
        super(TestNodeServer, self).setUp()
        self.node = nodes.node()
        self.node.foo = 'foo'
        self.site.root['node'] = self.node
        self.site.root['observer'] = nodes.observer(
            'http://localhost:9000/node')

    def test_node(self):
        httpc.get('http://localhost:9000/node')
        evt = coros.event()        
        def get_event():
            r = httpc.get('http://localhost:9000/node/event/0')
            evt.send(r)
        api.spawn(get_event)
        self.node.publish('bar')
        self.assertEquals(evt.wait(), 'bar')

    def test_node_timeout(self):
        self.assertRaises(
            httpc.Accepted,
            httpc.get,
            'http://localhost:9000/node/event/0',
            {'x-stacked-event-wait-time': '0.01'})

    def test_observer(self):
        ## Get the initial state
        state = httpc.get('http://localhost:9000/observer')
        self.assertEquals(eval(state)['foo'], 'foo')
        self.node.foo = 'bar'
        self.node.publish('foo')
        api.sleep(0.1)
        state = httpc.get('http://localhost:9000/observer')
        self.assertEquals(eval(state)['foo'], 'bar')

    def test_observer_times_out(self):
        obs = nodes.observer('http://localhost:9000/node', 0.1, 0.1)
        self.site.root['observer'] = obs

        old_expire = obs.expire
        evt = coros.event()
        def exp():
            old_expire()
            evt.send(None)
        obs.expire = exp

        httpc.get('http://localhost:9000/observer')

        evt.wait()
        self.assertNotEquals(obs._last_timeout_time, 0)



if __name__ == '__main__':
    tests.main()
