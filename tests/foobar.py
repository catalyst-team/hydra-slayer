# flake8: noqa
from typing import Any

__all__ = ["foo"]


def foo(a, b):
    return {"a": a, "b": b}


def bar():
    pass


def baz(*args):
    return args


def qux(a=1, *argss, b=2):
    return (a, *argss, b)


def quux(a=1, b=2, **kwargs):
    return {"a": a, "b": b, **kwargs}


def quuz(**params):
    return {"a": params["a"], "b": params["b"]}


class grault:
    def __init__(self, a: Any = 1, b: int = 2):
        self.a = a

        if not isinstance(b, int):
            raise ValueError
        self.b = b

    @staticmethod
    def garply(a, b):
        return {"a": a, "b": b}

    def waldo(self):
        return {"a": self.a, "b": self.b}
