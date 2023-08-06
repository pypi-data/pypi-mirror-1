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

import re, errno
from subprocess import Popen, PIPE, CalledProcessError
from threading import Thread

READ_BUFSIZE = 4096

def pipe(pipeline='', *args, **opts):
    'str, ... > (Iterable(bytes) -> Iterable(bytes))'
    opts = opts.copy()
    opts.setdefault('stdout', PIPE)
    cmd = _format(pipeline, args)
    return lambda input: _run_pipeline(cmd, input, **opts)

def runpipe(pipeline='', *args, **opts):
    'str, ... -> Iterable(bytes)'
    return pipe(pipeline, *args, **opts)([])

def o(*fs):
    '*[y -> z, x -> y, ..., a -> b] -> (a -> z)'
    return lambda x: reduce(lambda x, f: f(x), reversed(fs), x)

def _shell_escape(str):
    'str -> str'
    return re.sub(r'''([ \t'"\$])''', r'\\\1', str)

def _format(pipeline, args):
    r'''str, [str] -> str

    >>> _format('ls -l {} | grep {} | wc', ['foo 1', 'bar$BAZ'])
    'ls -l foo\\ 1 | grep bar\\$BAZ | wc'
    '''
    # No escaping for '{}' at this moment
    assert pipeline.count('{}') == len(args)
    return reduce(
        lambda str, arg: str.replace('{}', arg, 1),
        map(_shell_escape, args),
        pipeline)

def _run_pipeline(cmd, input, **opts):
    def write(fd, xs):
        try:
            for x in xs:
                fd.write(x)
        finally:
            fd.close()
    opts.update(dict(shell=True, stdin=PIPE))
    p = Popen(cmd, **opts)
    try:
        writer = Thread(target=write, args=(p.stdin, iter(input)))
        writer.start()
        try:
            if p.stdout is not None:
                for x in iter(lambda: p.stdout.read(READ_BUFSIZE), ''):
                    yield x
        finally:
            writer.join()
    finally:
        ret = p.wait()
        if ret != 0:
            raise CalledProcessError(ret, cmd)

