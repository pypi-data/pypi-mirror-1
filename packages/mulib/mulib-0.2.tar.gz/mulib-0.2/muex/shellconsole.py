"""\
@file shellconsole.py
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


import code
import os.path
import popen2
import sys
import time

from eventlet import api
from eventlet import logutil

from mulib import mu
from mulib import console

import simplejson


class ShellConsole(console.Console):
    transforms = os.path.join(os.path.dirname(__file__), 'shellconsole.js')
    stylesheet = os.path.join(os.path.dirname(__file__), 'shellconsole.css')

    def __init__(self, config, context):
        self.my_host = context['host']
        if 'root' in context:
            root = context['root']
        else:
            root = dict(config=config, context=context)
        self.interactor = code.InteractiveConsole(root)
        self.logsucker = logutil.LineLogger(self.emit)
        self.reset_collector()
        self.partial_lines = ''
        self.ps1_prompt = '>>> '
        self.ps2_prompt = '... '
        self.prompt = self.ps1_prompt
        super(ShellConsole, self).__init__()

    def event_connect(self, target):
        return [target.peer_name_string(), "shellconsole running on %s" % (self.my_host, )]

    def reset_collector(self):
        self.collector = []

    def emit(self, line):
        self.collector.append(line)

    def post_key_typed(self, my_name='', current_input=''):
        for target in self.targets:
            if target.peer_name_string() != my_name:
                target.msg('key-typed', [my_name, current_input])

    def post_console_input(self, my_name='', input=''):
        self.reset_collector()
        command_id = time.time()
        cmd = str(input)
        print "Running command", command_id, cmd
        self.broadcast('input-line', [my_name, self.prompt, cmd])
        stderr = self.saved_stderr = sys.stderr
        stdout = self.saved_stdout = sys.stdout

        try:
            sys.stderr = self.logsucker
            sys.stdout = self.logsucker
            result = self.interactor.runsource(self.partial_lines + cmd)
        finally:
            sys.stderr, sys.stdout = self.saved_stderr, self.saved_stdout
        if not result:
            self.prompt = self.ps1_prompt
            self.partial_lines = ''
        else:
            self.prompt = self.ps2_prompt
            self.partial_lines += cmd + '\n'
        for output_line in self.collector:
            print output_line
            self.broadcast('output-line', output_line)
        print "Finished shell command", `result`, command_id


index = ShellConsole({}, {'host':'localhost'})

