# Introduction

This is a command line tool for practicing coding skills against coding
website, e.g. leetcode.

There're some existing tools, like
[terminal-leetocde](https://github.com/chishui/terminal-leetcode)
and [leetcode-cli](https://www.npmjs.com/package/leetcode-cli).

# Features

- using login status from your browser
- list questions
- pick a question, generate a local file with default code
- test your solution in local file, with customizable test cases
- submit your solution

# Install and usage

Use `pip install pracode` to install this tool. Note this only works
with Python 3. Python 2 is not supported.

After installation, use command `pracode` to enter shell-like
environment, in which you can use `?` or `help` command for help.

Here are some commands available:

- `l`, `list`: list all problems
- `p ID`, `pick ID`, `ID`: pick a problem with the problem ID, this
will generate a local file with default code, which you can edit with
your prefered editor
- `t`, `test`, `t 'TESTCASE'`, `test 'TESTCASE'`: post your code in
local file to remote website, test it and show you the result. You can
also use your own test cases after the command.
- `s`, `submit`: submit your code, show you the result
- `q`, `quit`: quit

# TODO

performance:
- make the request for test result concurrent
- optimize all the network request, maybe asyncio?

ux:
- use `prompt_toolkit` instead of `cmd` package
- filter/pager for list
- more browsers/platforms, auto detect login status
- better looking refer to the `leetcode-cli` project
- more programming languages
- more websites

