# flake8: noqa
import string

import pytest

from hydra_slayer import functional as F
from hydra_slayer.factory import call_meta_factory
from . import foobar


def test_get_factories():
    res = F.get_factory(int)
    assert res == int

    res = F.get_factory("int")
    assert res == int

    # from module
    res = F.get_factory("tests.foobar.foo")
    assert res == foobar.foo

    # from class
    res = F.get_factory("tests.foobar.grault.garply")
    assert res == foobar.grault.garply


def test_fail_get_factory():
    with pytest.raises(LookupError) as e_ifo:
        F.get_factory("tests.foobar.corge")()
        assert hasattr(e_ifo.value, "__cause__")


def test_instantiations():
    res = F.get_instance("tests.foobar.foo", 1, 2)()
    assert res == {"a": 1, "b": 2}

    res = F.get_instance("tests.foobar.foo", a=1, b=2)()
    assert res == {"a": 1, "b": 2}

    res = F.get_instance("tests.foobar.foo", 1, b=2)()
    assert res == {"a": 1, "b": 2}

    res = F.get_instance(_target_="tests.foobar.foo", a=1, b=2)()
    assert res == {"a": 1, "b": 2}

    res = F.get_instance(_target_="tests.foobar.grault.garply", a=1, b=2)()
    assert res == {"a": 1, "b": 2}


def test_fail_instantiation():
    with pytest.raises(LookupError) as e_ifo:
        F.get_instance("tests.foobar.corge")()
        assert hasattr(e_ifo.value, "__cause__")

    with pytest.raises(TypeError) as e_ifo:
        F.get_instance(a=1, b=2)()
        assert hasattr(e_ifo.value, "__cause__")

    with pytest.raises(TypeError) as e_ifo:
        F.get_instance("tests.foobar.foo", c=1)()
        assert hasattr(e_ifo.value, "__cause__")


def test_from_params():
    res = F.get_from_params(**{"_target_": "tests.foobar.foo", "a": 1, "b": 2})()
    assert res == {"a": 1, "b": 2}

    res = F.get_from_params(_target_="tests.foobar.foo")(a=1, b=2)
    assert res == {"a": 1, "b": 2}


def test_from_empty_target_params():
    res = F.get_from_params(**{})
    assert res == {}

    res = F.get_from_params(**{"a": 1, "b": 2})
    assert res == {"a": 1, "b": 2}


def test_get_from_params_meta_factory():
    def meta_factory1(fn, args, kwargs):
        return fn

    def meta_factory2(fn, args, kwargs):
        return 1

    res = F.get_from_params(**{"_target_": "tests.foobar.foo"}, _meta_factory_=meta_factory1)
    assert res == foobar.foo

    res = F.get_from_params(**{"_target_": "tests.foobar.foo"}, _meta_factory_=meta_factory2)
    assert res == 1


def test_get_from_recursive_params():
    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": {
                "_target_": "tests.foobar.foo",
                "a": 1,
                "b": 2,
                "_mode_": "call",
            },
            "b": {
                "_target_": "tests.foobar.foo",
                "a": 3,
                "b": 4,
                "_mode_": "call",
            },
        },
    )()
    assert res["a"] == {"a": 1, "b": 2} and res["b"] == {"a": 3, "b": 4}


def test_get_from_params_shared_params():
    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": {"_target_": "tests.foobar.foo", "a": 1},
        },
        shared_params={"b": 2, "_meta_factory_": call_meta_factory},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": 2}

    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
        },
        shared_params={"b": 3, "_mode_": "call"},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": 3}


def test_get_from_params_nested_dicts_support():
    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": 1,
            "b": 2,
            "_meta_factory_": {"_target_": "hydra_slayer.call_meta_factory"},
        },
    )
    assert res == {"a": 1, "b": 2}

    res = F.get_from_params(
        **{
            "a": {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
            "b": {"_target_": "tests.foobar.foo", "a": 3, "b": 4},
        },
        shared_params={"_meta_factory_": call_meta_factory},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": {"a": 3, "b": 4}}

    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": {
                "c": {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
                "d": {"_target_": "tests.foobar.foo", "a": 3, "b": 4},
            },
            "b": 5,
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": {"c": {"a": 1, "b": 2}, "d": {"a": 3, "b": 4}}, "b": 5}

    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": {
                "c": {
                    "_target_": "tests.foobar.foo",
                    "a": {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
                    "b": {"b": 3},
                },
                "d": {
                    "_target_": "tests.foobar.foo",
                    "a": {"a": 4},
                    "b": {"_target_": "tests.foobar.foo", "a": 5, "b": 6},
                },
            },
            "b": {"e": {"f": {"g": {"_target_": "tests.foobar.foo", "a": 7, "b": 8}}}},
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {
        "a": {
            "c": {"a": {"a": 1, "b": 2}, "b": {"b": 3}},
            "d": {"a": {"a": 4}, "b": {"a": 5, "b": 6}},
        },
        "b": {"e": {"f": {"g": {"a": 7, "b": 8}}}},
    }


def test_get_from_params_nested_lists_support():
    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": [
                {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
                {"_target_": "tests.foobar.foo", "a": 3, "b": 4},
            ],
            "b": 5,
        },
        shared_params={"_meta_factory_": call_meta_factory},
    )
    assert res == {"a": [{"a": 1, "b": 2}, {"a": 3, "b": 4}], "b": 5}

    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": [[[[[{"_target_": "tests.foobar.foo", "a": 1, "b": 2}]]]]],
            "b": 3,
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": [[[[[{"a": 1, "b": 2}]]]]], "b": 3}


def test_recursive_get_from_params_nested_structures():
    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.foo",
            "a": {
                "_target_": "tests.foobar.foo",
                "a": {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
                "b": 2,
            },
            "b": [
                {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
                {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
            ],
        },
        shared_params={"_meta_factory_": call_meta_factory},
    )
    assert res == {
        "a": {"a": {"a": 1, "b": 2}, "b": 2},
        "b": [{"a": 1, "b": 2}, {"a": 1, "b": 2}],
    }


def test_get_from_params_args_support():
    res = F.get_from_params(**{"_target_": "tests.foobar.baz", "args": [1, 2, 3]})()
    assert res == (1, 2, 3)

    res = F.get_from_params(**{"_target_": "tests.foobar.qux", "argss": [1, 2, 3], "b": 4})()
    assert res == (1, 2, 3, 4)

    res = F.get_from_params(**{"_target_": "tests.foobar.qux", "a": 1, "b": 2})()
    assert res == (1, 2)

    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.baz",
            "args": [
                {"_target_": "tests.foobar.foo", "a": 1, "b": 2},
                {"_target_": "tests.foobar.foo", "a": 3, "b": 4},
            ],
        },
        shared_params={"_mode_": "call"},
    )
    assert res == ({"a": 1, "b": 2}, {"a": 3, "b": 4})


def test_get_from_params_kwargs_support():
    res = F.get_from_params(**{"_target_": "tests.foobar.quux", "a": 3, "b": 4})()
    assert res == {"a": 3, "b": 4}

    res = F.get_from_params(
        **{"_target_": "tests.foobar.quux", "a": 1, "b": 2, "kwargs": {"c": 3}}
    )()
    assert res == {"a": 1, "b": 2, "c": 3}

    res = F.get_from_params(
        **{"_target_": "tests.foobar.quux", "kwargs": {"c": 1, "b": 2, "a": 3}}
    )()
    assert res == {"a": 3, "b": 2, "c": 1}

    res = F.get_from_params(
        **{
            "_target_": "tests.foobar.quux",
            "a": 1,
            "b": 2,
            "kwargs": {"c": 3, "b": 4, "a": 5},
        }
    )()
    assert res == {"a": 5, "b": 4, "c": 3}

    res = F.get_from_params(
        **{"_target_": "tests.foobar.quuz", "params": {"a": 1, "b": 2, "c": 3}}
    )()
    assert res == {"a": 1, "b": 2}


def test_get_from_params_var_keyword():
    res = F.get_from_params(
        **{
            "a": {"_target_": "tests.foobar.foo", "a": 1, "b": 2, "_var_": "x"},
            "b": {"_target_": "tests.foobar.foo", "a": {"_var_": "x"}, "b": 3},
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": {"a": {"a": 1, "b": 2}, "b": 3}}
