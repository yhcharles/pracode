import cmd
import os.path
import re
import time

from bs4 import BeautifulSoup
import browser_cookie3
import requests

from . import util
from .util import logger


class Error(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class LeetCode(cmd.Cmd):
    intro = 'Welcome to pracode. Type help or ? to list commands.\n'

    def __init__(self):
        super().__init__()
        self._name = 'LC'
        self._problems = []
        self._id = 0
        self._title = ''
        self._lang = 'python'
        self._testcase = ''

    @property
    def _cookie(self):
        return browser_cookie3.chrome(domain_name='leetcode.com')

    @property
    def _csrftoken(self):
        return requests.utils.dict_from_cookiejar(self._cookie)['csrftoken']

    def _request(self, url, headers={}, data=None, json=None):
        h = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        }
        h.update(headers)
        if data is None and json is None:
            resp = requests.get(url, headers=h, cookies=self._cookie)
        else:
            resp = requests.post(url, headers=h, data=data, json=json, cookies=self._cookie)
        if resp.status_code != 200:
            raise Error('network request failed: {}'.format(resp.content))
        return resp

    def _xmlrequest(self, url, headers={}, data=None, json=None):
        h = {'x-requested-with': 'XMLHttpRequest'}
        h.update(headers)
        return self._request(url, h, data, json)

    @property
    def _filename(self):
        return '{}.{}.py'.format(self._id, self._title) if self._id else ''

    @property
    def prompt(self):
        return '\n{}:{}> '.format(self._name, self._filename)

    def do_quit(self, arg):
        '''quit'''
        return True

    def do_list(self, arg):
        '''list problems'''
        self._problems = self._xmlrequest('https://leetcode.com/api/problems/all/',
                                          headers={
                                              'referer': 'https://leetcode.com/problemset/all/',
                                          }).json()['stat_status_pairs']
        for p in self._problems:
            msg = '{status}\t{level}\t{question_id:4}\t{question__title}'.format(**p, **p['stat'], **p['difficulty'])
            if p['status'] is None:
                logger.info(msg)
            elif p['status'] == 'ac':
                logger.success(msg)
            else:
                logger.error(msg)

    def do_pick(self, arg):
        '''pick a problem with id, generate a file with description and sample code'''
        try:
            _id = int(arg.split()[0])
        except EOFError:
            self.do_quit(arg)
        except (ValueError, IndexError):
            logger.error('invalid problem id:', arg)
            return

        # find problem
        for p in self._problems:
            if p['stat']['question_id'] == _id:
                self._id = _id
                self._title = p['stat']['question__title_slug']
                break
        else:
            logger.error('problem id not found')
            return

        resp = self._request('https://leetcode.com/problems/{}/description/'.format(self._title)).content.decode()
        sp = BeautifulSoup(resp, 'lxml')

        # get test cases
        testcase = re.findall("sampleTestCase:\s*'(.*)',\s*judgerAvailable:", resp)
        if len(testcase) == 1:
            self._testcase = repr(util.unescape_unicode(testcase[0]))
        else:
            self._testcase = ''
            logger.error('no test cases found')

        if os.path.exists(self._filename):
            logger.info('use existing file:', self._filename)
            return

        # get description
        description = '# {}. {}\n#\n# {}'.format(
            self._id,
            sp.select('[property=og:title]')[0].get('content'),
            '\n# '.join(util.wrap_text(sp.select('[name=description]')[0].get('content')).splitlines()))

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
        print(description, '# sampleTestCase: {}'.format(self._testcase), default_code, sep='\n#\n',
              file=open(self._filename, 'w'))
        logger.info('new file:', self._filename)

    def do_test(self, arg):
        '''test solution with test cases'''
        solution = self._load_solution()
        if solution is None:
            return

        # find test case
        if arg.strip() != '':
            testcase = arg
        else:
            testcase = self._testcase
        logger.info('testcase:', testcase)

        resp = self._xmlrequest('https://leetcode.com/problems/{}/interpret_solution/'.format(self._title),
                                headers={
                                    'origin': 'https://leetcode.com',
                                    'referer': 'https://leetcode.com/problems/{}/description/'.format(self._title),
                                    'x-csrftoken': self._csrftoken,
                                },
                                json={
                                    'data_input': eval(testcase),
                                    'judge_type': 'large',
                                    'lang': 'python',
                                    'question_id': str(self._id),
                                    'test_mode': False,
                                    'typed_code': solution
                                }).json()

        # TODO: concurrently, colored
        result_expect = self._interpret(resp['interpret_expected_id'])
        logger.info('expected:', result_expect['code_answer'])
        result_yours = self._interpret(resp['interpret_id'])
        logger.info('   yours:', result_yours['code_answer'])

    def do_submit(self, arg):
        '''submit current solution'''
        solution = self._load_solution()
        if solution is None:
            return

        resp = self._xmlrequest('https://leetcode.com/problems/{}/submit/'.format(self._title),
                          headers={
                              'referer': 'https://leetcode.com/problems/{}/description/'.format(self._title),
                              'x-csrftoken': self._csrftoken,
                          },
                          json={
                              'data_input': eval(self._testcase),
                              'judge_type': 'large',
                              'lang': 'python',
                              'question_id': str(self._id),
                              'test_mode': False,
                              'typed_code': solution
                          })
        submit_id = resp.json()['submission_id']
        for i in range(100):
            resp = self._xmlrequest('https://leetcode.com/submissions/detail/{}/check/'.format(submit_id))
            if resp.json()['state'] != 'PENDING' and resp.json()['state'] != 'STARTED':
                break
        # TODO: better formated result, and more details about time percentile
        logger.info(resp.json())

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
    # TODO: make this async
    def _interpret(self, interpret_id):
        for i in range(100):
            resp = self._xmlrequest('https://leetcode.com/submissions/detail/{}/check/'.format(interpret_id)).json()
            if resp['state'] != 'PENDING' and resp['state'] != 'STARTED':
                return resp
            time.sleep(0.2)

    def cmdloop(self):
        while True:
            try:
                super().cmdloop()
                break
            except Error as e:
                logger.error(e)

    def _load_solution(self):
        if not self._id:
            logger.error('please pick a problem first')
            return
        if not os.path.exists(self._filename):
            logger.error('file missing:', self._filename)
            return
        return open(self._filename).read()
