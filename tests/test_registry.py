# flake8: noqa
import pytest

from hydra_slayer.registry import Registry
from .foobar import foo
from . import foobar as module


def test_add_function():
    r = Registry()

    r.add(foo)

    assert "foo" in r._factories


def test_add_function_name_override():
    r = Registry()

    r.add(foo, name="bar")

    assert "bar" in r._factories


def test_add_lambda_fail():
    r = Registry()

    with pytest.raises(ValueError):
        r.add(lambda x: x)


def test_add_lambda_override():
    r = Registry()

    r.add(lambda x: x, name="bar")

    assert "bar" in r._factories


def test_fail_multiple_with_name():
    r = Registry()

    with pytest.raises(ValueError):
        r.add(foo, foo, name="bar")


def test_fail_double_add_different():
    r = Registry()
    r.add(foo)

    with pytest.raises(LookupError):

        def bar():
            pass

        r.add(foo=bar)


def test_double_add_same_nofail():
    r = Registry()
    r.add(foo)
    # It's ok to add same twice, forced by python relative import
    # implementation
    # https://github.com/catalyst-team/catalyst/issues/135
    r.add(foo)


def test_instantiations():
    r = Registry()

    r.add(foo)

    res = r.get_instance("foo", 1, 2)()
    assert res == {"a": 1, "b": 2}

    res = r.get_instance("foo", 1, b=2)()
    assert res == {"a": 1, "b": 2}

    res = r.get_instance("foo", a=1, b=2)()
    assert res == {"a": 1, "b": 2}

    res = r.get_instance(_target_="foo", a=1, b=2)()
    assert res == {"a": 1, "b": 2}


def test_fail_instantiation():
    r = Registry()

    r.add(foo)

    with pytest.raises((RuntimeError, TypeError)) as e_ifo:
        r.get_instance("foo", c=1)()

    assert hasattr(e_ifo.value, "__cause__")


def test_decorator():
    r = Registry()

    @r.add
    def bar():
        pass

    r.get("bar")


def test_kwargs():
    r = Registry()

    r.add(bar=foo)

    r.get("bar")


def test_add_module():
    r = Registry()

    r.add_from_module(module)

    r.get("foo")

    with pytest.raises(LookupError):
        r.get_instance("bar")


def test_from_config():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(**{"_target_": "foo", "a": 1, "b": 2})()
    assert res == {"a": 1, "b": 2}

    res = r.get_from_params(_target_="foo")(a=1, b=2)
    assert res == {"a": 1, "b": 2}

    res = r.get_from_params(**{})
    assert res == {}


def test_name_key():
    r = Registry(name_key="name")

    r.add(foo)

    res = r.get_from_params(**{"name": "foo", "a": 1, "b": 2})()
    assert res == {"a": 1, "b": 2}

    res = r.get_from_params(**{"_target_": "foo", "a": 1, "b": 2})
    assert res == {"_target_": "foo", "a": 1, "b": 2}


def test_get_from_params_meta_factory():
    def meta_factory1(fn, args, kwargs):
        return fn

    def meta_factory2(fn, args, kwargs):
        return 1

    r = Registry()

    r.add(foo)

    res = r.get_from_params(**{"_target_": "tests.foobar.foo"}, _meta_factory_=meta_factory1)
    assert res == foo

    res = r.get_from_params(**{"_target_": "tests.foobar.foo"}, _meta_factory_=meta_factory2)
    assert res == 1


def test_get_from_recursive_params():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "_target_": "foo",
            "a": {"_target_": "foo", "_mode_": "call", "a": 1, "b": 2},
            "b": {"_target_": "foo", "_mode_": "call", "a": 3, "b": 4},
        },
    )()
    assert res["a"] == {"a": 1, "b": 2} and res["b"] == {"a": 3, "b": 4}


def test_get_from_params_shared_params():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{"_target_": "foo", "a": {"_target_": "foo", "a": 1}},
        shared_params={"b": 2, "_mode_": "call"},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": 2}

    res = r.get_from_params(
        **{"_target_": "foo", "a": {"_target_": "foo", "a": 1, "b": 2}},
        shared_params={"_mode_": "call", "b": 3},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": 3}


def test_get_from_params_nested_dicts_support():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "a": {"_target_": "foo", "a": 1, "b": 2},
            "b": {"_target_": "foo", "a": 3, "b": 4},
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": {"a": 3, "b": 4}}

    res = r.get_from_params(
        **{
            "_target_": "foo",
            "a": {
                "c": {"_target_": "foo", "a": 1, "b": 2},
                "d": {"_target_": "foo", "a": 3, "b": 4},
            },
            "b": 5,
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": {"c": {"a": 1, "b": 2}, "d": {"a": 3, "b": 4}}, "b": 5}

    res = r.get_from_params(
        **{
            "_target_": "foo",
            "a": {
                "c": {
                    "_target_": "foo",
                    "a": {"_target_": "foo", "a": 1, "b": 2},
                    "b": {"b": 3},
                },
                "d": {
                    "_target_": "foo",
                    "a": {"a": 4},
                    "b": {"_target_": "foo", "a": 5, "b": 6},
                },
            },
            "b": {"e": {"f": {"g": {"_target_": "foo", "a": 7, "b": 8}}}},
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
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "_target_": "foo",
            "a": [
                {"_target_": "foo", "a": 1, "b": 2},
                {"_target_": "foo", "a": 3, "b": 4},
            ],
            "b": 5,
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": [{"a": 1, "b": 2}, {"a": 3, "b": 4}], "b": 5}

    res = r.get_from_params(
        **{
            "_target_": "foo",
            "a": [[[[[{"_target_": "foo", "a": 1, "b": 2}]]]]],
            "b": 3,
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": [[[[[{"a": 1, "b": 2}]]]]], "b": 3}


def test_recursive_get_from_params_nested_structures():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "_target_": "foo",
            "a": {
                "_target_": "foo",
                "a": {"_target_": "foo", "a": 1, "b": 2},
                "b": 2,
            },
            "b": [
                {"_target_": "foo", "a": 1, "b": 2},
                {"_target_": "foo", "a": 1, "b": 2},
            ],
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {
        "a": {"a": {"a": 1, "b": 2}, "b": 2},
        "b": [{"a": 1, "b": 2}, {"a": 1, "b": 2}],
    }


def test_get_from_params_var():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "a": {"_var_": "x", "_target_": "foo", "a": 1, "b": 2},
            "b": {"_target_": "foo", "a": {"_var_": "x"}, "b": 3},
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": {"a": {"a": 1, "b": 2}, "b": 3}}


def test_get_from_params_var_keyword():
    r = Registry(var_key="_variable_")

    r.add(foo)

    res = r.get_from_params(
        **{
            "a": {"_variable_": "x", "_target_": "foo", "a": 1, "b": 2},
            "b": {"_target_": "foo", "a": {"_variable_": "x"}, "b": 3},
        },
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": {"a": {"a": 1, "b": 2}, "b": 3}}


def test_get_from_params_vars_dict():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{"_var_": "x", "_target_": "foo", "a": 1, "b": 2},
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": 1, "b": 2}

    res = r.get_from_params(
        **{"_target_": "foo", "a": {"_var_": "x"}, "b": 3},
        shared_params={"_mode_": "call"},
    )
    assert res == {"a": {"a": 1, "b": 2}, "b": 3}


def test_get_from_params_var_attr():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "a": {
                "_var_": "x",
                "_target_": "tests.foobar.grault",
                "_mode_": "call",
                "a": 3,
                "b": 4,
            },
            "b": {"_var_": "x.waldo"},
        },
    )
    assert res["b"] == {"a": 3, "b": 4}


def test_get_from_params_var_method_without_params():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "a": {
                "_var_": "x",
                "_target_": "tests.foobar.grault",
                "_mode_": "call",
                "a": 3,
                "b": 4,
            },
            "b": {"_var_": "x.b"},
        },
    )
    assert res["b"] == 4


def test_get_from_params_var_method_with_params():
    r = Registry()

    r.add(foo)

    res = r.get_from_params(
        **{
            "a": {
                "_var_": "x",
                "_target_": "tests.foobar.grault",
                "_mode_": "call",
                "a": 3,
                "b": 4,
            },
            "b": {"_var_": "x.garply", "a": 1, "b": 2},
        },
    )
    assert res["b"] == {"a": 1, "b": 2}


def test_get_from_params_attrs_keyword():
    r = Registry(attrs_delimiter="/")

    r.add(foo)

    res = r.get_from_params(
        **{
            "a": {
                "_var_": "x",
                "_target_": "tests.foobar.grault",
                "_mode_": "call",
                "a": 3,
                "b": 4,
            },
            "b": {"_var_": "x/waldo"},
        },
    )
    assert res["b"] == {"a": 3, "b": 4}


def test_get_from_params_vars_dict():
    r = Registry()

    r.add(foo)

    r.get_from_params(
        **{
            "a": {
                "_var_": "x",
                "_target_": "tests.foobar.grault",
                "_mode_": "call",
                "a": 3,
                "b": 4,
            },
        },
    )

    res = r.get_from_params(
        **{
            "b": {"_var_": "x.b"},
        },
    )
    assert res["b"] == 4
