"""\
@file mud.py
Mud: the simplest, most do-nothing mulib server you could ask for.  It
is a blank slate that you can put stuff in.

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
import os.path
import sys

#from mulib import caps
from mulib import mu
from mulib import stacked

from eventlet import api, httpd, util

util.wrap_socket_with_coroutine_socket()



class MethodGuard(object):
    def __init__(self, root, 
        GET=False, PUT=False, DELETE=False,
        POST=False, HEAD=False, OPTIONS=False):
        self.root = root
        self.GET = GET
        self.PUT = PUT
        self.DELETE = DELETE
        self.POST = POST
        self.HEAD = HEAD
        self.OPTIONS = OPTIONS

    def handle(self, req, segments):
        print "consume", segments
        if len(segments) == 2 and segments[0] == 'cap':
            ## Special case for the capability proxy, allow
            ## the holder of the capability to invoke any method
            return stacked.consume(self.root, req, segments)

        method = req.method().upper()
        if getattr(self, method, False):
            return stacked.consume(self.root, req, segments)

        req.response(405, body='')
stacked.add_consumer(MethodGuard, MethodGuard.handle)


def run(port=8080):
    run_named('muex', port=8080)
 

def run_named(name, port=8080):
    ## TODO figure out ip address 0.0.0.0 is going to bind to?
    root = api.named(name)
    site = mu.SiteMap(root)

    print root, type(root), dir(root)
#    site.root['_cap'] = cap_store = caps.CapabilityStore(
#        'http://localhost:%s/cap/' % port)
#    site.root['cap'] = caps.CapabilityProxy(cap_store)

    api.spawn(
        httpd.server,
        api.tcp_listener(('127.0.0.1', port)),
        site,
        max_size=512)

    httpd.server(
        api.tcp_listener(('0.0.0.0', port)),
        mu.SiteMap(MethodGuard(site.root, GET=True)),
        max_size=512)



if __name__ == '__main__':
    run()
