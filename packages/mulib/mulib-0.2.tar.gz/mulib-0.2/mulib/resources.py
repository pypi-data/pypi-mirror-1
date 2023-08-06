"""\
@file resources.py
@author Donovan Preston
@brief Miscellaneous useful Resource subclasses.

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

import mimetypes
import os
import time

from eventlet import httpdate

from mulib import mu

class MovedPermanently(mu.Resource):
    def __init__(self, location):
        self.location = location

    def handle_get(self, req):
        req.set_header(
            'Location',
            self.location)
        req.response(301) # Moved Permanently
        req.write(self.location)


class Data(mu.Resource):
    def __init__(self, data, content_type='text/html'):
        self.data = data
        self.content_type = content_type
        self.time_created = httpdate.format_date_time(time.time())

    def handle_get(self, req):
        #if req.get_header('If-Modified-Since') == self.time_created:
        #    req.response(304)
        #    return ''
        req.set_header('Content-Type', self.content_type)
        req.set_header('Content-Length', len(self.data))
        req.set_header('Last-Modified', self.time_created)
        req.write(self.data)


class Directory(mu.Resource):
    def __init__(self, path):
        self.path = path

    def findChild(self, req, segments):
        full_path = os.path.join(*(self.path, ) + segments)
        if os.path.exists(full_path):
            return (
                File(full_path, mimetypes.guess_type(full_path)),
                segments, ())
        return (None, (), segments)


class File(mu.Resource):
    def __init__(self, path, content_type=None):
        self.path = path
        if content_type is None:
            content_type, encoding = mimetypes.guess_type(path)
            if content_type is None:
                content_type = 'application/octet-stream'
        self.content_type = content_type

    def handle_get(self, req):
        f = file(self.path, 'rb')
        finfo = os.stat(self.path)
        req.set_header('Content-Type', self.content_type)
        #modtime = httpdate.format_date_time(finfo.st_mtime)
        #req.set_header('Last-Modified', modtime)

        #if req.get_header('If-Modified-Since') == modtime:
        #    req.response(304)
        #    return ''

        req.write(f.read())
        return

        # block = f.read(32*1024)
#         if not block:
#             req.send_error(204)
#         else:
#             while True:
#                 req.write_chunked(xml(block))
#                 block = f.read(32*1024)
#                 if not block:
#                     break


class Response(mu.Resource):
    def __init__(self, code, headers=(), body=''):
        self.code = code
        self.headers = headers
        self.body = body

    def handle(self, req):
        req.response(self.code)
        for key, value in self.headers:
            req.set_header(key, value)
        req.write(self.body)

