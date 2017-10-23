import sys
import textwrap

import colors

def unescape_unicode(s):
    return bytes(s, 'utf-8').decode('unicode-escape')

def wrap_text(s):
    return '\n'.join(map(lambda x: textwrap.fill(x), s.splitlines()))

class ColorOut(object):
    def _out(self, *msg):
        print(*msg, file=sys.stderr)

    def info(self, *msg):
        self._out(*msg)
    def warn(self, *msg):
        self._out(colors.yellow(*msg))
    def error(self, *msg):
        self._out(colors.red(*msg))
    def success(self, *msg):
        self._out(colors.green(*msg))
out = ColorOut()

