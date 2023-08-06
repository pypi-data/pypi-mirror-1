"""proxy.py

Proxies HTTP requests

$LicenseInfo:firstyear=2007&license=internal$

Copyright (c) 2007-2008, Linden Research, Inc.

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
$/LicenseInfo$
"""

import urlparse
import httplib
import socket
import time

from eventlet import httpc

from mulib import mu

def prepareRelayedHeaders(req, netloc, headers):
    headers_to_remove = [
        x.strip().lower() for x in headers.get('connection', "").split(",")]

    headers_to_remove.append('connection')
    # remove transfer-encoding header to avoid
    # sending non-chunked data from Apache
    # as chunk. Failure to remove this causes
    # httplib.py to receive a line of chunk data
    # in place of chunk headers (length, extensions)
    # etc. which understably causes httplib.py
    # to throw a exception about int() incoversion
    headers_to_remove.append('transfer-encoding')

    for key in headers_to_remove:
        headers.pop(key, None)


class FakeResponse(object):
    status = "EXCEPTION"
    msg = {}


class Proxy(mu.Resource):
    """A resource which will proxy the current request
    to another location.
    """
    def __init__(
        self, 
        url, 
        console=None,
        debug=False, 
        via_cache=False,
        via_header=None):
        self.private = url
        self.console = console
        self.debug = debug
        self.via_cache = via_cache
        self.via_header = via_header

    def findChild(self, request, segments):
        return self, segments, ()

    def handle(self, req):
        """Handle an incoming request by making another request to a private
        resource and writing the reply to our incoming request.

        WARNING: It is very important to the design of the current capability
        server (in caps.py) that this code not allow anything to change
        self.private, the url which we are proxying to. For example, designs
        which allow parameterization of proxying by passing query arguments
        or path segments from the incoming request to the private request
        would allow for injection attacks.

        It is still worth thinking of designs where capabilities are
        parameterizable. For example adding ?foo=bar to the capability
        could result in passing the ?foo=bar query parameter to an
        internal web service. Another example is a hypothetical
        "backbone" capability, granted by the simulator to point at
        http://localhost:12040/, and then given to the viewer only in god
        mode, which then gives it to a mozilla control which pops up (or 
        is on a face!). The mozilla control would do it's thing fetching the
        capability, which it would then add path segments and query
        args to the end of and attempt to fetch, which a hypothetical
        capability server could append to the private url.

        However, any implementations of the above hypothetical capability
        architectures would have to preserve the current semantics of
        capabilities for existing users.
        """
        proto, netloc, path, query, fragment = urlparse.urlsplit(
            self.private)

        path_to_proxy = path
        if query:
            path_to_proxy += "?" + query

        incoming_body = req.read_body()

        headers_to_proxy = dict([
            (key.lower(), value) for (key, value) in req.get_headers().dict.items()])
        prepareRelayedHeaders(req, netloc, headers_to_proxy)

        headers_to_proxy.pop('content-length', None)

        # Only set adjust the via header if someone passed that in
        # during construction.
        if self.via_header:
            via = headers_to_proxy.get('via', '')
            if via:
                via += ", "
            via += self.via_header
            headers_to_proxy['via'] = via

        # kartic: override the host header with the value
        # got from request headers. Proxying fails
        # otherwise, as it uses localhost:<port>
        headers_to_proxy['host'] = netloc

            ## this is a bug in python 2.3
            ## client.request below automatically adds a content-length
            ## header. However, it adds a *duplicate* header if we have
            ## already set one. This bug is not present in 2.4.
            ## work around this by leaving out content length here.

        headers_to_proxy['connection'] = "close"
        forwarded_ip, forwarded_port = req.socket().getpeername()
        headers_to_proxy['x-forwarded-for'] = forwarded_ip
        headers_to_proxy['x-forwarded-for-port'] = forwarded_port

        request_id = time.time()

        if headers_to_proxy.get('content-type') == 'application/octet-stream':
            to_log = (request_id, req.method(), netloc, path_to_proxy, headers_to_proxy, "<binary body>")
        else:
            if not path_to_proxy.endswith('event-get'):
                to_log = (request_id, req.method(), netloc, path_to_proxy, headers_to_proxy, incoming_body)
            else:
                to_log = None
        if self.console is not None and to_log is not None:
            self.console.log_request(*to_log)
        if self.debug and to_log is not None:
            print to_log

        response = FakeResponse()
        body = None

        try:
            client = httpc.make_connection(proto, netloc, self.via_cache)
            if self.debug:
                print 'Proxy.handle(): %s' % netloc
            client.connect()
            if self.via_cache:
                path_to_proxy = self.private
                headers_to_proxy['host'] = netloc
            client.request(
                req.method().upper(),
                path_to_proxy,
                incoming_body,
                headers_to_proxy)

            response = client.getresponse()

            body = response.read()
            req.response(response.status, response.reason)
            headers_to_respond = dict(response.msg.items())
            prepareRelayedHeaders(req, netloc, headers_to_respond)
            for header, value in headers_to_respond.items():
                req.set_header(header, value)
        except (httplib.HTTPException, socket.error), e:
            body = "Upstream error: %s" % (str(e), )
            req.response(502, body)
            req.set_header('content-type', 'text/plain')

        to_log = None
        if not isinstance(response, FakeResponse):
            if headers_to_respond.get('content-type') == 'application/octet-stream':
                to_log = (request_id, response.status, headers_to_respond, "<binary body>")
            else:
                if not path_to_proxy.endswith('event-get'):
                    to_log = (request_id, response.status, headers_to_respond, body)
        if self.console is not None and to_log is not None:
            self.console.log_response(*to_log)
        if self.debug and to_log is not None:
            print to_log

        req.write(mu.xml(body))

