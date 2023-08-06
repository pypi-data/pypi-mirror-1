
from mulib import mu, pantheon, stacked


class Draw(pantheon.Pantheon):
    def __init__(self):
        pantheon.Pantheon.__init__(
            self, {},
            script=pantheon.sibling(__file__, 'draw.js'),
            stylesheet=pantheon.sibling(__file__, 'draw.css'))


index = Draw()

