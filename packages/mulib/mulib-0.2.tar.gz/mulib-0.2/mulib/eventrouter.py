"""\
@file eventrouter.py
@author Donovan Preston

Copyright (c) 2005-2006, Donovan Preston
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

import os
import time
import socket
import os.path

import simplejson

from mulib import mu, resources

from eventlet import api,channel, timer


class TimedOut(Exception):
    pass


class DumbEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        return str(obj)

class Target(mu.Resource):
    debug = False
    cache = False
    contentType = 'text/xml'
    
    reconnect_timer = None
    channel = None

    def __init__(self, target_id, resource, peer_name):
        self.target_id = target_id
        self.queue = []
        self.resource = resource
        self.peer_name = peer_name

    def handle(self, request):
        try:
            mu.Resource.handle(self, request)
        except socket.error, (errno, reason):
            if errno == 32:
                self.reconnect_timer.cancel()
                return
            raise

    def handle_get(self, req):
        req.write(())

    def handle_post(self, req):
        req.set_header('pragma', 'no-cache')
        req.set_header('content-type', 'text/xml')
        if self.reconnect_timer:
            # The client made another request within 5 seconds, horray!
            self.reconnect_timer.cancel()
        req.resource = self.resource

        sock = req.protocol.socket
        def bounce(descriptor=None):
            try:
                api.get_hub().remove_descriptor(sock.fileno())
            except socket.error:
                ## server closed;
                ## ignore
                return
            # Client closed browser; remove ourself
            # this will be done in socket.error in handle above
            self._client_timeout()
            
        api.get_hub().add_descriptor(sock.fileno(), read=lambda *a: None, exc=bounce)

        got_event = dict(
            request_id=self.request_id,
            target_id=self.target_id,
            events=self._process_events())

        # cancel the close watchdog
        api.get_hub().remove_descriptor(sock.fileno())

        req.write(mu.xml(simplejson.dumps(got_event, cls=DumbEncoder)))
        return None

    def _process_events(self):
        if self.queue:
            queue, self.queue = self.queue, []
            return queue

        # Server has 25 seconds to send an event before being disconnected
        self.timer = timer.Timer(25, self._server_timeout)
        self.timer.schedule()
        self.channel = channel.channel()
        try:
            event = self.channel.receive()
        except TimedOut:
            event = None
        self.timer.cancel()
        self.channel = None

        # Client has 5 seconds to reconnect before being disconnected
        self.reconnect_timer = timer.Timer(5, self._client_timeout)
        self.reconnect_timer.schedule()

        if event != None:
            return [event]
        return []

    def _send(self, event):
        if self.channel is not None:
            self.channel.send(event)
        else:
            self.queue.append(event)    

    def _server_timeout(self):
        # We didn't have an event on the server; send a noop
        self.channel.send_exception(TimedOut)

    def _client_timeout(self):
        # Client didn't reconnect fast enough; we're going bye-bye
        self.resource._event_target_disconnected(self)

    def msg(self, transform, data, broadcasted=False, log=True):
        """Send a message to this target.

        transform: The client-side function to invoke.
        data: The data to send as the argument to the function.
        """
        to_send = (transform, simplejson.dumps(data, cls=DumbEncoder))
        if log and not broadcasted:
            console = self.resource.console
            if console is not None:
                console.log_transform(to_send)
        self._send(to_send)

    def peer_name_string(self):
        return "%s-%s" % self.peer_name


class Router(mu.Resource):
    debug = True
    transforms = 'transforms.js'
    stylesheet = 'stylesheet.css'
    template = mu.xml("""<html><head>
      <script src="http://www.mochikit.com/MochiKit/MochiKit.js"> </script>
      <script src="eventrouter.js" /> </script>
      <script src="transforms.js"> </script>
      <link href="styles.css" rel="stylesheet" />
    </head><body id="body">
      <div id="contents">
        Contents here.
      </div>
      <div id="bottom"> </div>
    </body></html>""")

    def __init__(self, transforms=None, stylesheet=None, console=None):
        if console is True:
            self.console = self
        else:
            self.console = console
        self.clients = dict()
        self.targets_by_id = dict()
        self.targets_by_target_id = dict()
        self.targets = list()
        base = os.path.split(__file__)[0]
        self.child_mochi = resources.Directory(
            os.path.join(base, '../../js/MochiKit/'))
        if transforms is not None:
            self.transforms = transforms
        if stylesheet is not None:
            self.stylesheet = stylesheet
        if os.path.exists(self.transforms):
            setattr(self, 'child_transforms.js', resources.File(self.transforms))
        if os.path.exists(self.stylesheet):
            setattr(self, 'child_styles.css', resources.File(self.stylesheet))
        setattr(self, 'child_eventrouter.js', resources.File(os.path.join(base, 'eventrouter.js')))

    def child_(self, req, segment):
        return self

    def broadcast(self, transform, data, log=True):
        """Send a message to all clients connected to this router.

        transform: The client-side function to invoke on all connected browsers.
        data: The data to send to the function.
        """
        for client in self.clients.values():
            if log and self.console is not None:
                self.console.log_transform((transform, simplejson.dumps(data)))
                broadcasted = True
            else:
                broadcasted = False
            client.msg(transform, data, broadcasted=broadcasted, log=log)

    def _event_target_connected(self, target):
        collector = []
        def new_msg(name, value):
            collector.append((name, value))

        target.msg = new_msg
        result = self.event_connect(target)
        del target.msg

        target.msg('__initialize__', result)
        for name, value in collector:
            target.msg(name, value)

        self.targets.append(target)

    def event_connect(self, target):
        """override me
        """
        pass

    def _event_target_disconnected(self, target):
        if target in self.targets:
            self.targets.remove(target)
        else:
            ## This can go away if this bug goes away.
            print "Bug tracking: Target was not present", target
        self.targets_by_id.pop(str(id(target)))
        self.targets_by_target_id.pop(target.target_id)
        self.clients.pop(target.request_id)
        self.event_disconnect(target)

    def event_disconnect(self, target):
        """override me
        """
        pass

    def child_events(self, req, name):
        old_request_id = req.get_query('request_id')
        if old_request_id in self.clients:
            reconnect = True
            target = self.clients.pop(old_request_id)
        else:
            if old_request_id:
                print "WTF. This is a bug.", old_request_id, self.clients
            reconnect = False
            self.target_id = getattr(self, 'target_id', 0) + 1
            target = Target(self.target_id, self, req.socket().getpeername())
            self._event_target_connected(target)

        ## TODO: If this proves to fix the bug, just make the request_id always time() + target_id
        target.request_id = str(time.time())
        if target.request_id in self.clients:
            print "Bug tracking: Duplicate request_id", target.request_id

        target.request_id += "-" + str(self.target_id)
        self.clients[target.request_id] = target
        self.targets_by_id[str(id(target))] = target
        self.targets_by_target_id[target.target_id] = target
        if not reconnect:
            self.event_connect(target)
        req.target = target
        return target

    def handle_get(self, req):
        if not req.path().endswith('/'):
            # redirect to url with trailing slash added
            req.response(301, 'Moved Permanently')
            req.set_header('location', 'http://' + req.get_header('host') + req.path() + '/')
            req.write('')
            return
        return mu.Resource.handle_get(self, req)

    def handle_post(self, req):
        post = req.get_query('post', 'default')
        target_id = int(req.get_query('target_id'))
        body = simplejson.loads(req.read_body())
        if self.console is not None:
            self.console.log_send_data((post, str(self.targets_by_target_id[target_id]), body))
        handler = getattr(self, 'post_%s' % (post, ), None)
        if handler is None:
            print "No post_* handler for send_data:", post
        else:
            handler(req, self.targets_by_target_id[target_id], body)
        req.write('')
