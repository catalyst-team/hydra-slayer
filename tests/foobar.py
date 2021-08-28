# flake8: noqa
__all__ = ["foo"]


def foo(a, b):
    return {"a": a, "b": b}


def bar():
    pass


def baz(*args):
    return args


def qux(a=1, *argss, b=2):
    return sum((a, b, *argss))
