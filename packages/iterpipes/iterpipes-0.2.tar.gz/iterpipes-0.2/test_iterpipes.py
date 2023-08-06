# -*- coding: utf-8 -*-

from __future__ import with_statement
import sys
from itertools import islice
from subprocess import CalledProcessError
from nose.tools import eq_, assert_raises
from minimock import Mock

from iterpipes import pipe, runpipe

STDOUT_FILENO = 1

join = lambda xs: ''.join(xs).strip()

def test_basic_single():
    eq_(runpipe('ls -d /'), '/\n')

def test_basic_many():
    eq_(runpipe('echo foo | wc -l'), '1\n')

def test_huge_input():
    wc = pipe('wc -l')
    eq_(join(wc('%d\n' % x for x in xrange(10000))), '10000')

def test_make_pipe():
    lines = runpipe(r'echo a b c b a | tr {} \\n | sort | uniq', ' ')
    eq_(lines, 'a\nb\nc\n')

def test_really_huge_input():
    cat = pipe('cat')
    sum = 0
    BUFSIZE = 10000
    TIMES = 10000
    with open('/dev/zero', 'rb') as fd:
        for x in cat(islice(iter(lambda: fd.read(BUFSIZE), ''), TIMES)):
            sum += len(x)
    eq_(sum, BUFSIZE * TIMES)

def test_dont_touch_stdout():
    eq_(runpipe('ls -d /', stdout=STDOUT_FILENO), '')

def test_nonexistent_command():
    assert_raises(CalledProcessError,
        lambda: runpipe('echo foo | bar --baz'))

def test_stdin_iterable_excpt():
    class E(Exception): pass
    def g():
        raise E('foo')
        yield 'bar'
    assert_raises(E, lambda: join(pipe('ls /')(g())))

if __name__ == '__main__':
    test_basic_single()

