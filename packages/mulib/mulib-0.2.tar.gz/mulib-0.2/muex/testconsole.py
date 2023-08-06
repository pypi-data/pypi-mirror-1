"""\
@file testconsole.py
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
import popen2
import sys
import time

from eventlet import api

from mulib import mu
from mulib import console

import simplejson

try:
    from indra.base import llsd
except:
    pass


from os.path import dirname, join, realpath
directory = realpath(dirname(__file__))
TEST_SCRIPT_PATH = realpath(
    directory + '../../../../test/test.py')


TEST_CONSOLE_URL = 'http://localhost:12040/test/'


class TestConsole(console.Console):
    transforms = os.path.join(os.path.dirname(__file__), 'testconsole.js')
    stylesheet = os.path.join(os.path.dirname(__file__), 'testconsole.css')

    def __init__(self, config, context):
        self.my_host = context['host']
        self.test_script_path = context.get(
            'test-script-path', TEST_SCRIPT_PATH)
        self.test_console_url = context.get(
            'test-console-url', TEST_CONSOLE_URL)
        console.Console.__init__(self)

    def event_connect(self, target):
        return "testconsole running on %s" % (self.my_host,)

    def post_log_start(self, req, body):
        self.clear_replay()
        self.log_and_broadcast('log_start', ['', body])

    def _run_cmd(self, switch, value):
        child = popen2.Popen3([
            sys.executable,
            self.test_script_path,
            switch, value,
            '-c', self.test_console_url
            ])
        status = -1
        while status == -1:
            status = child.poll()
            api.sleep()

    def post_run(self, req, test_name):
        self._run_cmd('-t', test_name)

    def post_run_suite(self, req, mode):
        self._run_cmd('-m', mode)


index = TestConsole({}, {'host':'localhost'})

