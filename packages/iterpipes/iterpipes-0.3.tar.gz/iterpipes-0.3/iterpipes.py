# -*- coding: utf-8 -*-

# Copyright (c) 2009 Andrey Vlasovskikh
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from __future__ import with_statement
from contextlib import contextmanager
import re, errno, locale, string
from subprocess import Popen, PIPE, CalledProcessError
from threading import Thread
from itertools import imap
from codecs import iterdecode

__all__ = [
    'cmd', 'bincmd', 'linecmd', 'run', 'call', 'check_call', 'join', 'each',
    'strip', 'Fun', 'format',
]

_DEFAULT_READ_BUFSIZE = 4096

def bincmd(command, *args, **opts):
    'str, ... -> (Iterable(bytes) -> Iterable(bytes))'
    opts = opts.copy()
    opts.setdefault('stdout', PIPE)
    command = format(command, args)
    return Fun(lambda input: _run_pipeline(command, input, **opts))

def cmd(command, *args, **opts):
    'str, ... -> (Iterable(str) -> Iterable(str))'
    def decode(xs):
        return iterdecode(xs, encoding)
    def encode(xs):
        return (x.encode(encoding) for x in xs)
    opts = opts.copy()
    encoding = opts.setdefault('encoding', locale.getpreferredencoding())
    opts.pop('encoding')
    return Fun(encode) | bincmd(command, *args, **opts) | decode

def linecmd(command, *args, **opts):
    'str, ... -> (Iterable(str) -> Iterable(str))'
    opts = opts.copy()
    opts['bufsize'] = 1
    return cmd(command, *args, **opts)

class Fun(object):
    'Function wrapper that defines the function composition operator `|`.'
    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        return self.f(*args, **kwargs)

    def __or__(self, other):
        return Fun(compose(other, self))

    def __repr__(self):
        return repr(self.f)

    def __getattr__(self, name):
        return getattr(self.f, name)

def run(p, input=[]):
    input = input if _is_iterable(input) else str(input)
    return p(input)

def call(p, input=[]):
    return _retcode(run(p, input))

def check_call(p, input=[]):
    return _force(run(p, input))

def join(xs):
    'Iterable(bytes or str) -> bytes or str'
    return ''.join(xs)

def each(f):
    '(a -> b) -> (Iterable(a) -> Iterable(b)'
    return lambda xs: imap(f, xs)

def strip(chars=None):
    return each(lambda s: s.strip(chars))

def compose(*fs):
    '*[y -> z, x -> y, ..., a -> b] -> (a -> z)'
    f = lambda x: reduce(lambda x, f: f(x), reversed(fs), x)
    f.__name__ = ', '.join(f.__name__ for f in fs)
    return f

o = compose

def _force(xs):
    'Iterable(a) -> None'
    for x in xs:
        pass

def _retcode(xs):
    'Iterable(a) -> int'
    try:
        _force(xs)
    except CalledProcessError, e:
        return e.returncode
    else:
        return 0

def format(command, args):
    r'''str, [str] -> str

    >>> format('ls -l {} | grep {} | wc', ['foo 1', 'bar$BAZ'])
    'ls -l foo\\ 1 | grep bar\\$BAZ | wc'
    '''
    if command.count('{}') != len(args):
        raise TypeError('arguments do not match the format string %r: %r',
            (command, args))
    fmt = command.replace('%', '%%').replace('{}', '%s')
    return fmt % tuple(map(_shell_escape, args))

def _shell_escape(str):
    'str -> str'
    return re.sub(r'''([ \t'"\$])''', r'\\\1', str)

def _run_pipeline(command, input, **opts):
    if not _is_iterable(input):
        raise TypeError('input must be iterable, got %r' % type(input).__name__)
    opts = opts.copy()
    opts.update(dict(shell=True, stdin=input))
    bs_opt = opts.get('bufsize', 0)
    bufsize = _DEFAULT_READ_BUFSIZE if bs_opt <= 0 else bs_opt
    with _popen(command, **opts) as p:
        if p.stdout is None:
            return
        if bufsize == 1:
            xs = p.stdout
        else:
            xs = iter(lambda: p.stdout.read(bufsize), '')
        for x in xs:
            yield x

def _is_iterable(x):
    return hasattr(x, '__iter__')

@contextmanager
def _popen(*args, **kwargs):
    def write(fd, xs):
        try:
            for x in xs:
                fd.write(x)
        except IOError, e:
            if e.errno != errno.EPIPE:
                write_expts.append(e)
        except Exception, e:
            write_expts.append(e)
        finally:
            fd.close()
    write_expts = []
    stdin = kwargs.get('stdin')
    if _is_iterable(stdin):
        kwargs = kwargs.copy()
        kwargs['stdin'] = PIPE
    p = Popen(*args, **kwargs)
    try:
        if _is_iterable(stdin):
            writer = Thread(target=write, args=(p.stdin, iter(stdin)))
            writer.start()
            try:
                yield p
            finally:
                writer.join()
                if len(write_expts) > 0:
                    raise write_expts.pop()
        else:
            yield p
    except Exception, e:
        if hasattr(p, 'terminate'):
            p.terminate()
        raise
    else:
        ret = p.wait()
        if ret != 0:
            raise CalledProcessError(ret, *args)

