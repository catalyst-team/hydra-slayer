# flake8: noqa
import pytest

from hydra_slayer.factory import call_meta_factory, default_meta_factory, partial_meta_factory


def test_call_meta_factory():
    res = call_meta_factory(int, (42,), {})

    assert res == 42

    res = call_meta_factory(dict, (), {"a": 1, "b": 2})

    assert res == {"a": 1, "b": 2}

    res = call_meta_factory(int, ("101",), {"base": 2})

    assert res == 5


def test_partial_meta_factory():
    res = partial_meta_factory(int, ("101",), {})

    assert callable(res)

    assert res() == 101

    assert res(base=2) == 5


def test_default_meta_factory():
    # `int` is class, so `call_meta_factory` is expected
    res = default_meta_factory(int, (42,), {})

    assert res == 42

    # `lambda` is function, so `partial_meta_factory` is expected
    res = default_meta_factory(lambda x: x, (42,), {})

    assert res() == 42
