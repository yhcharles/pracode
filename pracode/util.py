import textwrap

def unescape_unicode(s):
    return bytes(s, 'utf-8').decode('unicode-escape')

def wrap_text(s):
    return '\n'.join(map(lambda x: textwrap.fill(x), s.splitlines()))
