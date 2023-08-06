"""\
@file cgiadapter.py
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
import os.path
import traceback

os.environ['PYTHON_EGG_CACHE'] = '/tmp/' + os.environ.get('USER', 'nobody')

if not os.path.exists(os.environ['PYTHON_EGG_CACHE']):
    os.mkdir(os.environ['PYTHON_EGG_CACHE'])

from eventlet import api

from mulib import mu

import sys
import syslog
import BaseHTTPServer


class NullLog(object):
    def write(self, *a):
        pass


class NullServer(object):
    def __init__(self, site):
        self.site = site
        self.log = NullLog()

    def log_message(self, message):
        pass
#        self.log.write(message)

    def write_access_log_line(self, *args):
        """Write a line to the access.log. Arguments:
        client_address, date_time, requestline, code, size, request_time
        """
        pass

    def log_exception(self, type, value, tb):
        print ''.join(traceback.format_exception(type, value, tb))


class CgiProtocol(object):
    request_version = 'HTTP/1.0'
    responses = BaseHTTPServer.BaseHTTPRequestHandler.responses
    def __init__(self, server):
        from eventlet import logutil

        self.server = server
        self.wfile = sys.stdout
        self.rfile = sys.stdin
        self.socket = sys.stdin
        sys.stdout, sys.stderr = (
            logutil.SysLogger(syslog.LOG_INFO),
            logutil.SysLogger(syslog.LOG_ERR))

        self.client_address = ('Unknown address - CGI', 'Unknown port')
        self.requestline = "Unknown request line - CGI"

    def set_response_code(self, request, code, message):
        request.set_header('Status', "%s %s" % (code, message))

    def generate_status_line(self):
        return []


def log_fatal_exception(msg="Internal Server Error"):
    from eventlet import logutil

    fatal_error_logger = logutil.SysLogger(syslog.LOG_ERR)
    formatted = ''.join(traceback.format_exception(*sys.exc_info()))
    fatal_error_logger.write(formatted)
    return "Status: 500 %s\r\nContent-type: text/plain\r\n\r\n%s" % (msg, formatted)


def run_as_cgi(module_name, class_name, *args, **keywords):
    """http://www.w3.org/CGI/
    http://hoohoo.ncsa.uiuc.edu/cgi/env.html
    http://hoohoo.ncsa.uiuc.edu/cgi/out.html
    """
    syslog.openlog(sys.argv[0], syslog.LOG_PID, syslog.LOG_LOCAL0)

    try:
        klass = api.named(module_name + '.' + class_name)
    except Exception:
        ## Catch import errors.
        print log_fatal_exception("cgiadapter could not import module")
        return

    try:
        site = mu.SiteMap(klass(*args, **keywords))
        server = NullServer(site)
        method = os.environ.get("REQUEST_METHOD", "GET")
        path = os.environ.get("PATH_INFO", "/")
        query = os.environ.get("QUERY_STRING", "")
        if query:
            path = "%s?%s" % (path, query)
        headers = {}
        for name in os.environ.keys():
            if name.startswith('HTTP_'):
                header_name = name[len('HTTP_'):].replace('_', '-')
                headers[header_name.lower()] = os.environ[name]
            elif name == 'CONTENT_TYPE':
                headers['content-type'] = os.environ['CONTENT_TYPE']
            elif name == 'CONTENT_LENGTH':
                headers['content-length'] = os.environ['CONTENT_LENGTH']
    except Exception:
        ## Catch exceptions in klass.__init__, and misc crap.
        print log_fatal_exception("cgiadapter error")

    from eventlet import httpd

    ## Theoretically we should never have an exception here...
    request = httpd.Request(CgiProtocol(server), method, path, headers)
    ## And if an exception happens inside here, mu will be sure to catch it.
    site.handle_request(request)

    if not request._request_started:
        request.write(
            "Request completed without writing a response:\n%s\n%s" % (
                request, request.__dict__))

