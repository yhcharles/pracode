import cmd
import os.path
import re
from functools import partial
import time

import requests
import browser_cookie3
from bs4 import BeautifulSoup

from . import util


class LeetCode(cmd.Cmd):
    intro = 'Welcome to pracode. Type help or ? to list commands.\n'
    file = None

    def __init__(self):
        super().__init__()
        self._name = 'LeetCode'
        self._id = 0
        self._title = ''
        self._lang = 'python'
        self._testcase = ''
        self._cookiejar = browser_cookie3.chrome(domain_name='leetcode.com')
        self._session = requests.Session()
        self._session.cookies = self._cookiejar
        self._get = partial(self._session.get, cookies=self._cookiejar)
        self._post = partial(self._session.post, cookies=self._cookiejar)
        self._problems = []
        self._page = None
        self._soup = None

    @property
    def _filename(self):
        return '{}.{}.py'.format(self._id, self._title) if self._id else ''

    @property
    def prompt(self):
        return '\n{}: {}\n> '.format(self._name, self._filename)

    def do_quit(self, arg):
        '''
        quit
        :param arg:
        :return:
        '''
        return True

    def do_list(self, arg):
        '''
        list problems
        :param arg:
        :return:
        '''
        r = self._get('https://leetcode.com/api/problems/all/').json()
        self._problems = r['stat_status_pairs']
        for p in self._problems:
            print('{status}\t{level}\t{question_id:4}\t{question__title}'.format(**p, **p['stat'], **p['difficulty']))

    def do_pick(self, arg):
        '''
        pick a problem with id, generate a file with description and sample code
        :param arg:
        :return:
        '''
        try:
            _id = int(arg.split()[0])
        except:
            print('invalid problem id')
            return

        # find problem
        for p in self._problems:
            if p['stat']['question_id'] == _id:
                self._id = _id
                self._title = p['stat']['question__title_slug']
                break
        else:
            print('problem id not found')
            return

        resp = self._get('https://leetcode.com/problems/{}/description/'.format(self._title)).content.decode()
        sp = BeautifulSoup(resp, 'lxml')
        self._page = resp
        self._soup = sp

        # get test cases
        testcase = re.findall("sampleTestCase:\s*'(.*)',\s*judgerAvailable:", resp)
        if len(testcase) == 1:
            self._testcase = repr(util.unescape_unicode(testcase[0]))
        else:
            self._testcase = ''
            print('no test cases found')

        if os.path.exists(self._filename):
            print('use existing file:', self._filename)
            return

        # get description
        description = '# {}. {}\n#\n# {}'.format(self._id,
                                                   sp.select('[property=og:title]')[0].get('content'),
                                                   '\n# '.join(
                                                       sp.select('[name=description]')[0].get('content').splitlines()))

        # get default code
        default_code = ''
        _codeDefinition = 'codeDefinition:'
        for line in resp.splitlines():
            line = line.strip()
            if line.startswith(_codeDefinition):
                l = eval(line[len(_codeDefinition):-1])
                break
        for d in l:
            if d['value'] == self._lang:
                default_code = '\n'.join(d['defaultCode'].splitlines())
        print(description, '# sampleTestCase: {}'.format(self._testcase), default_code, sep='\n#\n', file=open(self._filename, 'w'))
        print('new file:', self._filename)

    def do_test(self, arg):
        '''
        test solution with test cases
        :return:
        '''
        if not self._id:
            print('please pick a problem first')
            return
        if not os.path.exists(self._filename):
            print('file missing:', self._filename)
            return
        solution = open(self._filename).read()

        # find test case
        if arg.strip() != '':
            testcase = arg
        else:
            testcase = self._testcase
        print('testcase:', testcase)

        resp = self._post('https://leetcode.com/problems/{}/interpret_solution/'.format(self._title),
                          headers={
                              'origin': 'https://leetcode.com',
                              'referer': 'https://leetcode.com/problems/{}/description/'.format(self._title),
                              'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                              'x-csrftoken': requests.utils.dict_from_cookiejar(self._cookiejar)['csrftoken'],
                              'x-requested-with': 'XMLHttpRequest'
                          },
                          json={
                              'data_input': eval(testcase),
                              'judge_type': 'large',
                              'lang': 'python',
                              'question_id': str(self._id),
                              'test_mode': False,
                              'typed_code': solution
                          })
        if resp.status_code != 200:
            print('failed to send test request, respond:', resp.content)
            return
        resp = resp.json()

        result_expect = self.interpret(resp['interpret_expected_id'])
        print('expected:', result_expect['code_answer'])
        result_yours = self.interpret(resp['interpret_id'])
        print('   yours:', result_yours['code_answer'])


    def do_submit(self, arg):
        '''
        submit current solution
        :return:
        '''
        if not self._id:
            print('please pick a problem first')
            return
        if not os.path.exists(self._filename):
            print('file missing:', self._filename)
            return
        solution = open(self._filename).read()

        resp = self._post('https://leetcode.com/problems/{}/submit/'.format(self._title),
                          headers={
                              'origin': 'https://leetcode.com',
                              'referer': 'https://leetcode.com/problems/{}/description/'.format(self._title),
                              'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
                              'x-csrftoken': requests.utils.dict_from_cookiejar(self._cookiejar)['csrftoken'],
                              'x-requested-with': 'XMLHttpRequest'
                          },
                          json={
                              'data_input': eval(self._testcase),
                              'judge_type': 'large',
                              'lang': 'python',
                              'question_id': str(self._id),
                              'test_mode': False,
                              'typed_code': solution
                          })
        if resp.status_code != 200:
            print(resp.content)
            return
        submit_id = resp.json()['submission_id']
        resp = self._get('https://leetcode.com/submissions/detail/{}/check/'.format(submit_id))
        print(resp.json())
        pass

    # ============================
    # alias
    # ============================
    def do_q(self, arg):
        '''
        alias for quit
        :param arg:
        :return:
        '''
        return self.do_quit(arg)

    def do_l(self, arg):
        '''
        alias for list
        :param arg:
        :return:
        '''
        return self.do_list(arg)

    def do_p(self, arg):
        '''
        alias for pick
        :param arg:
        :return:
        '''
        return self.do_pick(arg)

    def do_t(self, arg):
        '''
        alias for test
        :return:
        '''
        return self.do_test(arg)

    def do_sub(self, arg):
        '''
        alias for submit
        :return:
        '''
        return self.do_submit(arg)

    def do_s(self, arg):
        '''
        alias for submit
        :return:
        '''
        return self.do_submit(arg)

    def default(self, line):
        '''
        default to pick
        :param line:
        :return:
        '''
        return self.do_pick(line)

    # ============================
    # util
    # ============================
    # TODO: make this async
    def interpret(self, interpret_id):
        for i in range(100):
            resp = self._get('https://leetcode.com/submissions/detail/{}/check/'.format(interpret_id))
            if resp.status_code != 200:
                print('interpret error:', resp.content)
                return
            resp = resp.json()
            if resp['state'] != 'PENDING' and resp['state'] != 'STARTED':
                return resp
            time.sleep(0.2)

