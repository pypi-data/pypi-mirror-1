"""\
@file sourceconsole.py
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

import keyword
import marshal
from os import path
import token
import tokenize

from mulib import mu
from mulib import console

import coverage

SEEN_TYPES = {}


class SourceConsole(console.Console):
    transforms = path.join(path.dirname(__file__), 'sourceconsole.js')
    stylesheet = path.join(path.dirname(__file__), 'sourceconsole.css')

    def tokenize(self, line_iter):
        current_line = 0
        displayed_line = 0
        inside_define = False
        inside_parameters = False
        complete_line = []
        for tok in tokenize.generate_tokens(line_iter):
            tok_type, tok, (start_row, start_col), (end_row, end_col), line = tok
            if inside_define:
                tok_type = "identifier"
                inside_parameters = True
            elif tok_type == token.NAME:
                if keyword.iskeyword(tok):
                    tok_type = 'keyword'
                else:
                    if inside_parameters:
                        tok_type = 'parameter'
                    else:
                        tok_type = 'variable'
            else:
                tok_type = token.tok_name[tok_type].lower()

            complete_line.append((tok, tok_type))

            if tok_type not in SEEN_TYPES:
                print "TOKEN", tok_type
                SEEN_TYPES[tok_type] = True

            current_line += tok.count('\n')
            if current_line > displayed_line:
                self.log_and_broadcast(
                    'finish_line',
                    dict(
                        tokens=complete_line,
                        num=current_line,
                        uncovered=current_line in self.uncovered))
                complete_line = []
                displayed_line = current_line

    def event_connect(self, target):
        super(SourceConsole, self).event_connect(target)
        return "sourceconsole running on tiny"

    def post_show_source(self, source_file):
        self.clear_replay()
        source_file = path.realpath(source_file)
        coverage.the_coverage.get_ready(False)
        coverage.the_coverage.exclude('#pragma[: ]+[nN][oO] [cC][oO][vV][eE][rR]')
        filename, statements, excluded, uncovered, lines = coverage.analysis2(
            source_file)
        print "cexecuted"
        print "EXCLUDED", uncovered
        self.uncovered = uncovered

        self.log_and_broadcast('start_file', source_file)
        if source_file.startswith('/Users/donovan/Code/'):
            self.tokenize(file(source_file).next)
        else:
            self.log_and_broadcast('error', 'Access denied')


index = SourceConsole({}, {'host':'localhost'})

