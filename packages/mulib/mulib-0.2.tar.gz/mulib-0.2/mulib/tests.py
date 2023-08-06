"""\
@file tests.py
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

import os
import sys
import unittest

from eventlet import api
from eventlet import httpd

from mulib import stacked, mu

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

NOT_FOUND = 'error: 404 not_found'

PUT = 'PUT'
GET = 'GET'
POST = 'POST'
DELETE = 'DELETE'


class NullSTDOut(object):
    def noop(*args):
        pass
    write = noop
    read = noop
    flush = noop

class FakeRequestCase(unittest.TestCase):
    mode = 'static'
    def setUp(self):
        self.site = mu.SiteMap()

    def consume(self, obj, *segs):
        return self.consume_(obj, stacked.TestRequest(site=self.site), *segs)

    def consume_(self, obj, req, *segs):
        stacked.consume(obj, req, segs)
        req.seek(0)
        out = req.read()
        return out

    def req(self, obj, method, body, *segs):
        return self.req_(obj, method, body, *segs)[0]

    def req_(self, obj, method, body, *segs):
        self.site = mu.SiteMap()
        req = stacked.TestRequest(site=self.site)
        req.method = lambda: method
        req.parsed_body = lambda: body
        out = self.consume_(obj, req, *segs)
        return out, req

class TestServer(unittest.TestCase):
    mode = 'static'
    def setUp(self):
        self.site = mu.SiteMap()
        self.logfile = StringIO()
        self.site.root[''] = 'hello'
        self.killer = api.spawn(
            httpd.server,
            api.tcp_listener(('0.0.0.0', 9000)),
            self.site,
            log=self.logfile)

    def tearDown(self):
        ## TODO probably only one of these should be required
        api.kill(self.killer)


main = unittest.main

doc_test_files = []

def run_all_tests(test_files = doc_test_files):
    """ Runs all the unit tests, returning immediately after the 
    first failed test.
    
    Returns true if the tests all succeeded.  This method is really much longer
    than it ought to be.
    """
    eventlet_dir = os.path.realpath(os.path.dirname(__file__))
    if eventlet_dir not in sys.path:
        sys.path.append(eventlet_dir)
    
    # add all _test files as a policy
    import glob
    test_files += [os.path.splitext(os.path.basename(x))[0] 
                  for x in glob.glob(os.path.join(eventlet_dir, "*_test.py"))]
    test_files.sort()
    
    for test_file in test_files:
        print "-=", test_file, "=-"
        try:
            test_module = __import__(test_file)
        except ImportError:
            print "Unable to import %s, skipping" % test_file
            continue
            
        if test_file.endswith('_test'):
            # gawd, unittest, why you make it so difficult to just run some tests!
            suite = unittest.findTestCases(test_module)
            result = unittest.TextTestRunner().run(suite)
            if not result.wasSuccessful():
                return False
        else:    
            failures, tests = doctest.testmod(test_module)
            if failures:
                return False
            else:
                print "OK"
                
    return True
    
if __name__ == '__main__':
    run_all_tests()

