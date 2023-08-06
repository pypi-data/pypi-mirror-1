#!/usr/bin/python

import py
from simpleopt import annotation, SimpleOpt, SimpleOptError


def test_simple_creation():
    def f():
        pass
    SimpleOpt(f, [])


def test_simple_run():
    def f():
        pass
    SimpleOpt(f, []).run()


def test_slot_creation():
    @annotation(a=float, b=int, c=bool, d=str)
    def f(a, b, c=1, d=2):
        pass
    s = SimpleOpt(f, ["--a=1.0", "--b=2", "--c", "--d=foo"])
    s._apply_func()
    slots = s.slots
    assert slots.keys() == ['a', 'b', 'c', 'd']

    assert slots['a'].type == float
    assert slots['a'].value == 1.0

    assert slots['b'].type == int
    assert slots['b'].value == 2

    assert slots['c'].type == bool
    assert slots['c'].value == True
    assert slots['c'].default == 1

    assert slots['d'].type == str
    assert slots['d'].value == 'foo'
    assert slots['d'].default == 2


def test_boolean_argument():
    @annotation(foo=bool)
    def f(foo):
        return foo

    r = SimpleOpt(f, ["--foo"])._apply_func()
    assert r

    r = SimpleOpt(f, ["--nofoo"])._apply_func()
    assert not r

    r = SimpleOpt(f, ["--foo=true"])._apply_func()
    assert r

    r = SimpleOpt(f, ["--foo=t"])._apply_func()
    assert r

    r = SimpleOpt(f, ["--foo=1"])._apply_func()
    assert r

    r = SimpleOpt(f, ["--foo=false"])._apply_func()
    assert not r

    r = SimpleOpt(f, ["--foo=f"])._apply_func()
    assert not r

    r = SimpleOpt(f, ["--foo=0"])._apply_func()
    assert not r

    py.test.raises(SimpleOptError, SimpleOpt(f, ["--foo=foo"])._apply_func)


def test_list_of_int_type_coercion():
    @annotation(numbers=[int])
    def f(numbers):
        return numbers

    r = SimpleOpt(f, ['1,2,3,4,5'])._apply_func()
    assert r == [1, 2, 3, 4, 5]


def test_two_positional_arguments_and_one_default():
    def f(a, b, c='C'):
        return (a, b, c)

    r = SimpleOpt(f, ['A', 'B'])._apply_func()
    assert r == ('A', 'B', 'C')


def test_insufficient_arguments():
    def f(a, b, c):
        return (a, b, c)

    py.test.raises(SimpleOptError, SimpleOpt(f, ['a'])._apply_func)


def test_too_many_positional_arguments():
    def f(a, b, c):
        pass

    py.test.raises(SimpleOptError, SimpleOpt(f, ['a', 'b', 'c', 'd'])._apply_func)


def test_invalid_option_argument():
    def f(foo, bar):
        pass

    py.test.raises(SimpleOptError, SimpleOpt(
        f, ['--foo=10', '--bar=20', '--baz=100'])._apply_func)


def test_duplicate_option_argument():
    def f(foo, bar):
        pass

    py.test.raises(SimpleOptError, SimpleOpt(
        f, ["--foo=10", "--bar=20", "--foo=30"])._apply_func)


def test_duplicate_boolean_argument():
    @annotation(foo=bool, bar=bool)
    def f(foo, bar):
        pass

    py.test.raises(SimpleOptError,
                   SimpleOpt(f, ["--foo", "--nofoo", "--bar"])._apply_func)

def test_help():
    def f(a, b):
        pass

    try:
        SimpleOpt(f, ["--help"])._apply_func()
    except SimpleOptError, e:
        assert e.print_usage
        return
    assert False, "failed to show usage"
