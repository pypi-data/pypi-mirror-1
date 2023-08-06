#-*- coding: utf-8 -*-

from nose.tools import *
from dmlt.datastructure import Token, TokenStream, _undefined


TEST_STREAM = [
    Token('bold'), Token('italic'), Token('uff'),
    Token('papapapa'), Token('foo'), Token('python'),
    Token('spaghetti'), Token('car'), Token('mom')
]
l = list


# Test functions for the TokenStream
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def test_feed():
    stream = TokenStream()
    for name in ('bold', 'italic', 'uff', 'papapapa', 'foo',
                 'python', 'spaghetti', 'car', 'mom'):
        stream.push(Token(name))
    for idx, received in enumerate(stream):
        exp = TEST_STREAM[idx]
        assert_equal(exp.type, received.type)


def test_next():
    stream = TokenStream(iter(TEST_STREAM))
    for exp in TEST_STREAM:
        eq_(exp.as_tuple(), stream.current.as_tuple())
        stream.next()
    assert_equal(stream.current.type, 'eof')

def test_look():
    stream = TokenStream(iter(TEST_STREAM))
    for iexp, exp in enumerate(TEST_STREAM):
        new = stream.look()
        if new.type != 'eof':
            assert_equal(TEST_STREAM[iexp+1].as_tuple(),
                         new.as_tuple())
        stream.next()
    assert_true(stream.look().type == 'eof')
