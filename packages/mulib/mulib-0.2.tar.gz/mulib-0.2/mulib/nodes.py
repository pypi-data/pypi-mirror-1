"""\
@file nodes.py
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

import itertools
import time
import types

from eventlet import api
from eventlet import coros
from eventlet import httpc

from mulib import stacked


class referenced_list(list):
    pass


class referenced_tuple(tuple):
    pass


stacked.add_consumer(referenced_list, stacked.consume_list)
stacked.add_consumer(referenced_tuple, stacked.consume_tuple)


class referenced_dict(dict):
    pass


stacked.add_consumer(referenced_dict, stacked.consume_dict)


class autoprovider(type):
    def __init__(klass, name, bases, ivars):
        super(autoprovider, klass).__init__(name, bases, ivars)
        stacked.add_consumer(klass, klass._consume_entity)
        stacked.add_producer(klass, klass._produce_entity, '*/*')
        stacked.add_producer(klass, klass._produce_entity, 'text/html')


class entity(object):
    __metaclass__ = autoprovider

    _consume_entity = None
    _produce_entity = None


def consume_entity(obj, req, segs):
    if len(segs) == 1:
        method = req.method()
        if method == 'PUT':
            setattr(obj, segs[0], req.parsed_body())
            req.response(201, body='')
            return
        elif method == 'DELETE':
            try:
                delattr(obj, segs[0])
            except AttributeError:
                pass
            req.response(200, body='')
            return
        if not segs[0]:
            stacked.consume(obj, req, ())
            return
    try:
        child = getattr(obj, segs[0])
    except AttributeError:
        req.not_found()
        return
    stacked.consume(child, req, segs[1:])


entity._consume_entity = consume_entity


SAFE_TYPES = (dict, list, tuple, str, unicode,
    int, long, float, bool, types.NoneType)


REFERENCED_TYPES = (entity, referenced_list, referenced_dict)


def produce_entity(obj, req):
    safe = {}
    for attr in dir(obj):
        if attr.startswith('_'):
            continue
        value = getattr(obj, attr)
        if type(value) in SAFE_TYPES:
            safe[attr] = value
        elif isinstance(value, REFERENCED_TYPES):
            safe[attr] = req.full_url() + '/' + attr
    stacked.produce(safe, req)


entity._produce_entity = produce_entity


class node(entity):
    """The server-side of publish/subscribe
    """
    def __init__(self):
        self.event = referenced_list()
        self.event.append(coros.event())

    def publish(self, evt):
        self.event[-1].send(evt)
        self.event.append(coros.event())


NO_DATA = object()


class observer(object):
    """The client-side of publish/subscribe
    Caches locally some state, which the observer then
    subscribes to

    This is a proof-of-concept implementation which will need
    more work to finish.
    """
    def __init__(self, node_url, subscription_ttl=30, poll_wait_time=25):
        self.node_url = node_url
        self.subscription_ttl = subscription_ttl
        self.poll_wait_time = poll_wait_time
        self._last_ping_time = 0
        self._last_timeout_time = 0
        self._event = coros.event()
        self._subscription_data = NO_DATA

    def _subscribe(self):
        self._subscription_data = httpc.get(self.node_url)
        counter = itertools.count()
        changed = True
        while self._last_ping_time + self.subscription_ttl > time.time():
            if changed:
                old_event = self._event
                self._event = coros.event()
                old_event.send(self._subscription_data)
                event_number = counter.next()
            ## TODO: Event skipping by having the node report it's current event
            try:
                httpc.get('%s/event/%s' % (
                    self.node_url, event_number),
                    {'x-stacked-event-wait-time': self.poll_wait_time})
                changed = True
            except httpc.Accepted:
                ## There wasn't an event for us yet. Ask again.
                changed = False
            if changed:
                self._subscription_data = httpc.get(self.node_url)

        ## This subscription is expired if we exit the loop.
        self.expire()

    def expire(self):
        self._subscription_data = NO_DATA
        self._last_timeout_time = time.time()
        
    def ping(self):
        self._last_ping_time = time.time()
        if self._subscription_data is NO_DATA:
            api.spawn(self._subscribe)
            self._event.wait()


def produce_observer(obs, req):
    obs.ping()
    stacked.produce(obs._subscription_data, req)
stacked.add_producer(observer, produce_observer)

