"""\
@file console.py
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

from mulib import eventrouter
from mulib import mu

try:
    from indra.base import llsd
except:
    llsd = object()

import simplejson



class Console(eventrouter.Router):
    def __init__(self, transforms=None, stylesheet=None):
        super(Console, self).__init__(
            transforms=transforms,
            stylesheet=stylesheet)
        self.child_ = self
        self.replay = []

    def event_connect(self, target):
        for event in getattr(self, 'replay', ()):
            target.msg(*event)
        return None

    def clear_replay(self):
        self.replay = []

    def log_and_broadcast(self, action, data):
        if not hasattr(self, 'replay'):
            self.replay = []
        self.replay.append((action, data))
        self.broadcast(action, data)

    def handle_post(self, req):
        action = req.get_query('post', 'default')
        data = req.read_body()
        meth = getattr(self, 'post_' + action, None)
        if meth is None:
            meth = lambda *args, **kw: self.log_and_broadcast(action, data)
        if isinstance(data, list):
            meth(*data)
        elif isinstance(data, dict):
            data = dict([
                (str(k), v)
                for (k, v) in data.items()])
            meth(**data)
        elif data is None:
            meth()
        else:
            meth(data)
        req.write({})


index = Console()


