"""\
@file logconsole.py
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

import os.path


from mulib import eventrouter


class Console(eventrouter.Router):
    transforms = os.path.join(os.path.dirname(__file__), 'logconsole.js')
    stylesheet = os.path.join(os.path.dirname(__file__), 'logconsole.css')

    def __init__(self, config, context):
        self.my_ip = context['host']
        eventrouter.Router.__init__(self)

    def event_connect(self, target):
        return "logconsole running on %s" % (self.my_ip, )

    def emit(self, output):
        self.broadcast('log', output, log=False)

    def log(self, *message):
        output = ' '.join([str(x) for x in message])
        self.broadcast('log', output, log=False)

    def log_request(self, request_id, method, netloc, path, headers, body):
        self.broadcast('log-request', {'request-id': request_id, 'method': method, 'url': netloc, 'path': path, 'headers': headers, 'body': body}, log=False)

    def log_response(self, request_id, status, headers, body):
        self.broadcast('log-response', {'request-id': request_id, 'status': status, 'headers': headers, 'body': body}, log=False)

    def log_transform(self, (transform, data)):
        self.broadcast('log-transform', (transform, data), log=False)

    def log_send_data(self, (post, target, body)):
        self.broadcast('log-send-data', (post, target, body), log=False)


index = Console({}, {'host':'localhost'})

