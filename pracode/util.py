import sys

import chalk


class Message(object):
    def _stderr(self, *msg):
        print(*msg, file=sys.stderr)

    def info(self, *msg):
        self._stderr(chalk.blue(*msg))

    def error(self, *msg):
        self._stderr(chalk.red(*msg))

    def warn(self, *msg):
        self._stderr(chalk.yellow(*msg))


logger = Message()


def unescape_unicode(s):
    return bytes(s, 'utf-8').decode('unicode-escape')
