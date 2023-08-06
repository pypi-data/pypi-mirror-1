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
import re, errno
from subprocess import Popen, PIPE, CalledProcessError
from threading import Thread

__all__ = ['pipe', 'runpipe', 'format', 'o']

READ_BUFSIZE = 4096

def pipe(pipeline, *args, **opts):
    'str, ... > (Iterable(bytes) -> Iterable(bytes))'
    opts = opts.copy()
    opts.setdefault('stdout', PIPE)
    cmd = format(pipeline, args)
    return lambda input: _run_pipeline(cmd, input, **opts)

def runpipe(pipeline, *args, **opts):
    'str, ... -> bytes'
    return ''.join(pipe(pipeline, *args, **opts)([]))

def o(*fs):
    '*[y -> z, x -> y, ..., a -> b] -> (a -> z)'
    return lambda x: reduce(lambda x, f: f(x), reversed(fs), x)

def format(pipeline, args):
    r'''str, [str] -> str

    >>> format('ls -l {} | grep {} | wc', ['foo 1', 'bar$BAZ'])
    'ls -l foo\\ 1 | grep bar\\$BAZ | wc'
    '''
    # No escaping for '{}' at this moment
    assert pipeline.count('{}') == len(args)
    return reduce(
        lambda str, arg: str.replace('{}', arg, 1),
        map(_shell_escape, args),
        pipeline)

def _shell_escape(str):
    'str -> str'
    return re.sub(r'''([ \t'"\$])''', r'\\\1', str)

def _run_pipeline(cmd, input, **opts):
    if not _is_iterable(input):
        raise TypeError('input must be iterable, got %r' % type(input).__name__)
    opts.update(dict(shell=True, stdin=input))
    with _popen(cmd, **opts) as p:
        if p.stdout is not None:
            for x in iter(lambda: p.stdout.read(READ_BUFSIZE), ''):
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

