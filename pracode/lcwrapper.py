import cmd
import glob
import logging
import sys

import sh

from pracode.util import out

logger = logging.getLogger(__name__)


class Error(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class LeetCode(cmd.Cmd):
    intro = 'Welcome to pracode. Type help or ? to list commands.\n'

    def __init__(self):
        super().__init__()
        self._name = 'LCW'
        self._problems = []
        self._filename = ''
        self._title = ''
        self._lang = 'python'
        self._testcase = ''
        _sh = sh(_out=sys.stdout, _err=sys.stderr)
        self._cmd = _sh.leetcode

    @property
    def prompt(self):
        return '\n{}:{}> '.format(self._name, self._filename)

    def do_quit(self, arg):
        '''quit'''
        return True

    def do_list(self, arg):
        '''list problems'''
        self._cmd.list()

    def do_pick(self, arg):
        '''pick a problem with id, generate a file with description and sample code'''
        try:
            _id = int(arg.split()[0])
        except EOFError:
            return self.do_quit(arg)
        except (ValueError, IndexError):
            if arg == 'EOF':
                return self.do_quit(arg)
            out.error('invalid problem id: ' + arg)
            return

        file_list = glob.glob('./{}.*.py'.format(_id))
        if not file_list:
            # leetcode -g -x -l python show
            self._cmd.show(_id, g=True, x=True, l='python')

        file_list = glob.glob('./{}.*.py'.format(_id))
        if not file_list:
            out.error('failed to pick problem: {}'.format(_id))
            return
        self._filename = file_list[0]

    def do_test(self, arg):
        '''test solution with test cases'''
        # find test case
        testcase = None
        if arg.strip() != '':
            testcase = arg
            self._cmd.test(self._filename, t=testcase)
        else:
            # no testcase given
            self._cmd.test(self._filename)

    def do_submit(self, arg):
        '''submit current solution'''
        self._cmd.submit(self._filename)

    def do_stat(self, arg):
        self._cmd.stat()

    def do_graph(self, arg):
        self._cmd.stat(g=True)

    # ============================
    # alias
    # ============================
    def do_q(self, arg):
        '''alias for quit'''
        return self.do_quit(arg)

    def do_l(self, arg):
        '''alias for list'''
        return self.do_list(arg)

    def do_p(self, arg):
        '''alias for pick'''
        return self.do_pick(arg)

    def do_t(self, arg):
        '''alias for test'''
        return self.do_test(arg)

    def do_sub(self, arg):
        '''alias for submit'''
        return self.do_submit(arg)

    def do_s(self, arg):
        '''alias for submit'''
        return self.do_submit(arg)

    def do_st(self, arg):
        '''alias for stat'''
        return self.do_stat(arg)

    def do_g(self, arg):
        '''alias for graph'''
        return self.do_graph(arg)

    def do_h(self, arg):
        '''alias for help'''
        return self.do_help(arg)

    def default(self, line):
        '''default to pick'''
        return self.do_pick(line)

    def emptyline(self):
        '''override, prevent from repeating last command implicitly'''
        pass

    # ============================
    # util
    # ============================
    def cmdloop(self):
        while True:
            try:
                super().cmdloop()
                break
            except Error as e:
                out.error(e)
