# Introduction

This is a command line tool for practicing coding skills against coding
website, e.g. leetcode.

There're some existing tools, like
[terminal-leetocde](https://github.com/chishui/terminal-leetcode)
and [leetcode-cli](https://www.npmjs.com/package/leetcode-cli).

# Features

- list questions
- pick a question, generate a local file with default code
- test your solution in local file, with customizable test cases
- submit your solution

# Install

Install [leetcode-cli](https://www.npmjs.com/package/leetcode-cli) first.
Then `pip install pracode` to install this tool. Note this only works
with Python 3. Python 2 is not supported.

After installation, use command `pracode` to enter shell-like
environment, in which you can use `?` or `help` command for help.

# Usage

Here are some commands available:

- `l`, `list`: list all problems
- `p ID`, `pick ID`, `ID`: pick a problem with the problem ID, this
will generate a local file with default code, which you can edit with
your prefered editor
- `t`, `test`, `t TESTCASE`, `test TESTCASE`: post your code in
local file to remote website, test it and show you the result. You can
also use your own test cases after the command.
- `s`, `submit`: submit your code, show you the result
- `q`, `quit`: quit

# TODO

ux:
- use `prompt_toolkit` instead of `cmd` package
- more programming languages
- more websites

