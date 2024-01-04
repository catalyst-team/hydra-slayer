# flake8: noqa
import pytest

from hydra_slayer import factory
from . import foobar


def test_call_meta_factory():
    res = factory.call_meta_factory(int, (42,), {})

    assert res == 42

    res = factory.call_meta_factory(dict, (), {"a": 1, "b": 2})

    assert res == {"a": 1, "b": 2}

    res = factory.call_meta_factory(int, ("101",), {"base": 2})

    assert res == 5


def test_partial_meta_factory():
    res = factory.partial_meta_factory(int, ("101",), {})

    assert callable(res)

    assert res() == 101

    assert res(base=2) == 5


def test_default_meta_factory():
    # `int` is class, so `call_meta_factory` is expected
    res = factory.default_meta_factory(int, (42,), {})

    assert res == 42

    # `lambda` is function, so `partial_meta_factory` is expected
    res = factory.default_meta_factory(lambda x: x, (42,), {})

    assert res() == 42


def test_fail_get_factory():
    error_msg = "factory '.+' is not callable"
    with pytest.raises(ValueError, match=error_msg):
        factory.default_meta_factory(5, tuple(), {})


def test_metafactory_factory_meta_factory_arg():
    res = factory.metafactory_factory(int, (42,), {"_meta_factory_": factory.call_meta_factory})

    assert res == 42

    res = factory.metafactory_factory(
        lambda x: x, (42,), {"_meta_factory_": factory.call_meta_factory}
    )

    assert res == 42

    res = factory.metafactory_factory(int, (42,), {"_meta_factory_": factory.partial_meta_factory})

    assert res() == 42

    res = factory.metafactory_factory(
        lambda x: x, (42,), {"_meta_factory_": factory.partial_meta_factory}
    )

    assert res() == 42


def test_metafactory_factory_modes():
    # `int` is class, so `call_meta_factory` is expected
    res = factory.metafactory_factory(int, (42,), {"_mode_": "auto"})

    assert res == 42

    # `lambda` is function, so `partial_meta_factory` is expected
    res = factory.metafactory_factory(lambda x: x, (42,), {"_mode_": "auto"})

    assert res() == 42

    # _mode_='call', so `call_meta_factory` is expected
    res = factory.metafactory_factory(int, (42,), {"_mode_": "call"})

    assert res == 42

    # _mode_='call', so `call_meta_factory` is expected
    res = factory.metafactory_factory(lambda x: x, (42,), {"_mode_": "call"})

    assert res == 42

    # _mode_='partial', so `partial_meta_factory` is expected
    res = factory.metafactory_factory(int, (42,), {"_mode_": "partial"})

    assert res() == 42

    # _mode_='partial', so `partial_meta_factory` is expected
    res = factory.metafactory_factory(lambda x: x, (42,), {"_mode_": "partial"})

    assert res() == 42


def test_fail_metafactory_factory_modes():
    error_msg = "'.+' is not a valid call mode"
    with pytest.raises(ValueError, match=error_msg):
        factory.metafactory_factory(int, (42,), {"_mode_": "foo"})


def test_metafactory_from_params():
    res = factory.metafactory_factory(foobar.fred, (), {"a": 42})

    assert res.a == 42
