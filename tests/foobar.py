# flake8: noqa
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
    @staticmethod
    def garply(a, b):
        return {"a": a, "b": b}
