#!/usr/bin/python

from simpleopt import annotation


def test_annotation_simple():
    @annotation(a=str, b=int)
    def f(a, b):
        pass
    assert f.__annotations__ == dict(a=str, b=int)


def test_annotation_with_varargs():
    @annotation(a=bool, b=int, c=str)
    def f(a, b, *c):
        pass
    assert f.__annotations__ == dict(a=bool, b=int, c=str)


def test_annotation_with_varargs_and_varkwargs():
    @annotation(a=str, b=int, c=float, d=str, e=str)
    def f(a, b=1, c=None, *d, **e):
        pass
    assert f.__annotations__ == dict(a=str, b=int, c=float, d=str, e=str)


def test_annotation_incomplete():
    @annotation(a=str)
    def f(a, b, c, *d, **e):
        pass
    assert f.__annotations__ == dict(a=str)
