
from mulib import pantheon

class Hello(pantheon.Pantheon):
    def __init__(self):
        pantheon.Pantheon.__init__(
            self, {'document':'edit this text', 'container':{'key':'value'}},
            script=pantheon.sibling(__file__, 'hello_pantheon.js'),
            stylesheet=pantheon.sibling(__file__, 'hello_pantheon.css'))


index = Hello()

