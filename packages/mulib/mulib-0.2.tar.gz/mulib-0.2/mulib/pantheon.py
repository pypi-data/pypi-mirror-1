"""\
@file pantheon.py
@author Donovan Preston

Copyright (c) 2007, Linden Research, Inc.
$License$

A pantheon is a temple to all gods. A Pantheon is a Resource which
provides a REST store that anyone can edit using PUT and DELETE,
and a way to ask to observe a set of paths for changes using the
"http long poll" or "comet"-style technique.

Each Pantheon is manipulated using a simple javascript api. Each
Pantheon should have a script with a main javascript function which
will be called when the page is loaded. See pantheon.js for details
about using javascript to implement the Pantheon's UI.

Construct a Pantheon and tell it the path to the script file.
Optionally pass a dictionary to initialize the REST store and
the path to a stylesheet file containing css styles for the app.

pantheon.Pantheon(
    {'hello': 'world'},
    script=pantheon.sibling(__file__, 'hello.js'))
"""

import base64
import pickle
import md5

from os.path import split, join, dirname
import time

import simplejson

from mulib import mu
from mulib import shaped
from mulib import stacked
from mulib import resources

from eventlet import api
from eventlet import coros


LATEST_EVENT = -1
EARLIEST_EVENT = None



def sibling(original, sibling):
    return join(dirname(original), sibling)


def make_etag(path):
    m = md5.new()
    m.update('/'.join(path))
    m.update(time.asctime())
    return '"%s"' % base64.encodestring(m.digest()).strip()


def internal_request(what, segs):
    fake = stacked.TestRequest()
    gather = []
    fake.write = gather.append
    stacked.consume(what, fake, segs)
    return gather[0]


def calculate_etags(pantheon, req, segs):
    segs = tuple(segs)
    method = req.method()
    if method == 'GET':
        if_none_match = req.get_header('if-none-match', None)
        old_etag = pantheon._entity_events.get(segs, {}).get('etag')
        if if_none_match and old_etag:
            for match in if_none_match.split(', '):
                if match == old_etag:
                    break
            else:
                req.response(304)
                req.write({
                    'status': 304, 'reason':
                    'Not Modified',
                    'etag': old_etag})
                return True

    elif method == 'DELETE':
        if segs in pantheon._entity_events:
            del pantheon._entity_events[segs]
        segs2 = list(segs)
        segs2[-1] = '*'
        segs2 = tuple(segs2)
        if segs2 in pantheon._container_events:
            del pantheon._container_events[segs2]
    return False


def consume_pantheon(pantheon, req, segs):
    not_modified = calculate_etags(pantheon, req, segs)
    if not_modified:
        return

    if segs == ['']:
        if req.method() == 'POST':
            wait_time = 30
            try:
                content_type = req.get_header('content-type', '')
                body = req.parsed_body()
                # catch alternate content-types for json
                if content_type.startswith('text/'):
                    try:
                        body = simplejson.loads(body)
                    except Exception, e:
                        print "Exc", e, body
                        body = ''

                ## This line blocks until an event occurs
                event = pantheon.observe(body, wait_time)
                req.response(200)
                req.write(event)
            except coros.Cancelled:
                req.response(202)
                req.write({})
            return

        stacked.produce(pantheon, req)
        return

    method = req.method()
    if method == 'PUT':
        if not shaped.would_retain_shape(
        pantheon.shape, pantheon._data, segs, req.parsed_body()):
            req.response(403)
            req.write({})

    stacked.consume(pantheon._data, req, segs)

    if method in ['PUT', 'DELETE']:
        ## Notify both observers of the resource and it's container
        pantheon.notify(method, segs, req.parsed_body())


def produce_pantheon(pantheon, req):
    url = req.full_url()
    if not url.endswith('/'):
        url += '/'
        req.response(301, headers=(('Location', url), ), body=url)
        return

    if req.method() == 'GET':
        script = (
            file(join(dirname(__file__), 'pantheon.js')).read() + 
            file(pantheon.script).read() + """

addLoadEvent(function() {
    main();
    _get_dirty_events();
})
        """)

        try:
            stylesheet = file(pantheon.stylesheet).read()
        except:
            stylesheet = ''

        req.response(200)
        req.set_header('content-type', 'text/html')
        req.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html><head>
          <script src="http://www.mochikit.com/MochiKit/MochiKit.js"> </script>
          <script>
%s
          </script>
          <style type="text/css">
%s
          </style>
        </head><body id="body">
          <div id="contents">
            Contents here.
          </div>
          <div id="bottom"> </div>
        </body></html>
""" % (script, stylesheet))
    else:
        req.not_found()


def make_parent(child):
    parent = list(child)
    parent[-1] = '*'
    return tuple(parent)

def make_event(event, path, etag, body):
    return {'event': event, 'path': path, 'etag': etag, 'body': body, 'to_notify': '/'.join(path)}


class PanMeta(type):
    def __init__(klass, name, bases, ivars):
        super(PanMeta, klass).__init__(name, bases, ivars)
        stacked.add_producer(
            klass, produce_pantheon, 'text/html')
        stacked.add_producer(
            klass, produce_pantheon, '*/*')
        stacked.add_consumer(klass, consume_pantheon)


def walk(something, path=()):
    yield path, something

    if isinstance(something, (list, tuple)):
        iterator = enumerate(something)
    elif isinstance(something, dict):
        iterator = something.items()
    else:
        return

    for i, val in iterator:
        for child in walk(val, path + (i, )):
            yield child


class ContainerEvent(object):
    def __init__(self, etag, path, previous=None):
        self.etag = etag
        self.path = path
        self.previous = previous
        if previous:
            previous.set_next(self)
        self.next = None

    def set_next(self, next):
        self.next = next


class Pantheon(object):
    __metaclass__ = PanMeta

    script = 'script.js'
    stylesheet = 'stylesheet.css'

    def __init__(self, data=None, shape=None, script=None, stylesheet=None):
        self._entity_events = {}
        self._container_events = {}
        self._data = {}
        if data is not None:
            self._data.update(data)
            for path, val in walk(data):
                etag = make_etag(path)
                self._entity_events[path] = {etag: make_event('PUT', path, etag, val)}

                if not path:
                    continue

                path2 = make_parent(path)
                etag = make_etag(path2)
                container_event = make_event('PUT', path, etag, val)
                container_event['to_notify'] = '/'.join(path2)
                self._container_events[path2] = {etag: container_event, None: container_event}

        if shape is None:
            shape = shaped.any
        self.shape = shape

        if script is not None:
            self.script = script
        if stylesheet is not None:
            self.stylesheet = stylesheet

        ## Who to notify when something changes
        ## {'path/to/data', greenlet}
        self._notify = {}
        ## Who is watching what
        ## {greenlet: ['path/to/data']}
        self._watching = {}
        ## If a new request comes in from an already connected client
        ## disconnect the old connection
        ## {'client-chosen-unique-id': greenlet}
        self._by_client_id = {}

    def _resume(self, gr, evt=None, exc=None):
        api.call_after(0, api.switch, gr, evt, exc)

    def _observe(self, greenlet, observing):
        for obs in observing:
            obs = obs['path']
            if obs not in self._notify:
                self._notify[obs] = {}
            self._notify[obs][greenlet] = True

    def _remove(self, greenlet, observing):
        for obs in observing:
            self._notify[obs['path']].pop(greenlet)

    def _resume_path(self, to_notify, evt):
        to_resume = self._notify.get(to_notify, {}).keys()
        for greenlet in to_resume:
            self._resume(greenlet, evt)
            self._remove(greenlet, self._watching[greenlet])

    def observe(self, observation_data, wait_time=None):
        client_id = observation_data.get('client-id')
        interest_list = observation_data['observe']

        if client_id in self._by_client_id:
            ## Short circuit an existing request that is waiting for an old interest_list
            self._resume(
                self._by_client_id.pop(client_id), exc=coros.Cancelled)

        for interested in interest_list:
            splitpath = tuple(interested['path'].encode('utf8').split('/'))
            ## If it doesn't end in *, it's a normal entity event, just compare the latest etag
            if splitpath[-1] != '*':
                entity_event = self._entity_events.get(splitpath)
                if entity_event and entity_event.get('etag') != interested.get('etag'):
                    entity_event = entity_event.copy()
                    entity_event['to_notify'] = interested['path']
                    return entity_event
            ## If it does end in *, it's a container event, 
            else:
                ## If the client did not supply an etag, we'll get the EARLIEST_EVENT
                ## key out of _container_events, which is always set to the first event
                container_events = self._container_events.get(splitpath, {})
                if interested.get('etag') is None:
                    if EARLIEST_EVENT in container_events:
                        evt = self._entity_events[container_events[EARLIEST_EVENT].path].copy()
                        evt['to_notify'] = interested['path']
                        return evt
                else:
                    container_event = container_events.get(interested['etag'])
                    if container_event and container_event.next:
                        entity_event = self._entity_events[container_event.next.path].copy()
                        entity_event['to_notify'] = interested['path']
                        return entity_event

        current = api.getcurrent()
        self._watching[current] = interest_list
        self._by_client_id[client_id] = current
        self._observe(current, interest_list)

        if wait_time is not None:
            canceller = api.exc_after(wait_time, coros.Cancelled)
        try:
            result = api.get_hub().switch()
        except coros.Cancelled:
            ## Just in case this was the short-circuit code above
            if wait_time is not None:
                canceller.cancel()
            self._remove(current, interest_list)
            if client_id in self._by_client_id:
                self._by_client_id.pop(client_id)
            raise
        if client_id in self._by_client_id:
            self._by_client_id.pop(client_id)
        if wait_time is not None:
            canceller.cancel()

        return result

    def notify(self, event, path, body):
        path = tuple(path)
        etag = make_etag(path)
        evt = make_event(event, path, etag, body)

        event_to_elide = self._entity_events.get(path)
        self._entity_events[path] = evt

        parent_path = make_parent(path)

        container_events = self._container_events.setdefault(parent_path, {})
        if not container_events:
            event = ContainerEvent(etag, path)
            container_events[EARLIEST_EVENT] = event
        else:
            previous_event = container_events[LATEST_EVENT]
            event = ContainerEvent(etag, path, previous_event)
        container_events[LATEST_EVENT] = container_events[etag] = event

        if event_to_elide:
            elide = container_events[event_to_elide['etag']]
            elide.previous.next = elide.next

        self._resume_path('/'.join(path), evt)
        cont_evt = evt.copy()
        cont_evt['to_notify'] = '/'.join(parent_path)
        self._resume_path('/'.join(parent_path), cont_evt)


stacked.add_consumer(Pantheon, consume_pantheon)
stacked.add_producer(
    Pantheon, produce_pantheon, 'text/html')
stacked.add_producer(
    Pantheon, produce_pantheon, '*/*')
