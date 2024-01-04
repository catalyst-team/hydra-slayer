# flake8: noqa
import pytest

from hydra_slayer.registry import Registry
from .foobar import foo, bar
from . import foobar as module


def test_add_function():
    r = Registry()

    r.add(foo)

    assert "foo" in r._factories


def test_add_function_name_override():
    r = Registry()

    r.add(foo, name="bar")

    assert "bar" in r._factories


def test_add_fail_on_lambda():
    r = Registry()

    error_msg = "Name for lambda factories must be provided"
    with pytest.raises(ValueError, match=error_msg):
        r.add(lambda x: x)


def test_add_fail_on_no_name():
    r = Registry()

    obj = 42

    error_msg = "Factory '.+' has no '__name__' and no name was provided"
    with pytest.raises(ValueError, match=error_msg):
        r.add(obj, name=None)


def test_add_lambda_override():
    r = Registry()

    r.add(lambda x: x, name="bar")

    assert "bar" in r._factories


def test_fail_multiple_with_name():
    r = Registry()

    error_msg = "Multiple factories with single name are not allowed"
    with pytest.raises(ValueError, match=error_msg):
        r.add(foo, foo, name="bar")


def test_fail_double_add_different():
    r = Registry()

    r.add(foo)

    error_msg = "Factory with name '.+' is already present\nAlready registered: '.+'\nNew: '.+'"
    with pytest.raises(LookupError, match=error_msg):
        r.add(foo=bar)


def test_double_add_same_nofail():
    r = Registry()

    r.add(foo)

    # It's ok to add same twice, forced by python relative import
    # implementation
    # https://github.com/catalyst-team/catalyst/issues/135
    r.add(foo)


def test_add_args_support():
    r = Registry()

    r.add(foo, bar)

    assert "foo" in r._factories and "bar" in r._factories


def test_add_kwargs_support():
    r = Registry()

    r.add(foo=foo)

    assert "foo" in r._factories


def test_add_warns_on_empty_kwargs():
    r = Registry()

    warn_msg = "No factories were provided!"
    with pytest.warns(UserWarning, match=warn_msg):
        r.add(**{})


def test_get_empty():
    r = Registry()

    res = r.get(None)
    assert res is None


def test_get_if_str():
    r = Registry()

    r.add(foo=foo)

    res = r.get_if_str("foo")
    assert res == foo

    res = r.get_if_str(42)
    assert res == 42


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

    assert r.add(foo) is not None

    error_msg = ".+ got an unexpected keyword argument '.+'"
    with pytest.raises((RuntimeError, TypeError), match=error_msg):
        r.get_instance("foo", c=1)()


def test_decorator():
    r = Registry()

    @r.add
    def bar():
        pass

    assert r.get("bar") is not None


def test_kwargs():
    r = Registry()

    r.add(bar=foo)

    assert r.get("bar") is not None


def test_late_add():
    def callback(registry: Registry) -> None:
        registry.add(foo)

    r = Registry()

    r.late_add(callback)

    assert r._factories == {}

    assert r.all() == ("foo",)


def test_add_module():
    r = Registry()

    r.add_from_module(module)

    assert r.get("foo") is not None

    error_msg = "No factory with name '.+' was registered"
    with pytest.raises(LookupError, match=error_msg):
        r.get_instance("bar")


def test_add_module_adds_all():
    r = Registry()

    r.add_from_module(module, ignore_all=True)

    assert "foo" in r._factories and "bar" in r._factories


def test_add_module_prefix_support():
    r = Registry()

    r.add_from_module(module, prefix="m.")

    r.get("m.foo")

    error_msg = "No factory with name '.+' was registered"
    with pytest.raises(LookupError, match=error_msg):
        r.get_instance("foo")


def test_add_from_module_fails_on_invalid_prefix():
    r = Registry()

    error_msg = "All prefix in list must be strings"
    with pytest.raises(TypeError, match=error_msg):
        r.add_from_module(module, prefix=["42", 42])

    error_msg = "Prefix must be a list or a string, got .+"
    with pytest.raises(TypeError, match=error_msg):
        r.add_from_module(module, prefix=42)


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


def test_all_magic_method():
    r = Registry()

    r.add(foo)

    res = r.all()
    assert res == ("foo",)

    r.add(bar)

    res = r.all()
    assert res == ("foo", "bar")


def test_str_magic_method():
    r = Registry()

    r.add(foo)

    res = r.__str__()
    assert res == "('foo',)"

    r.add(bar)

    res = r.__str__()
    assert res == "('foo', 'bar')"


def test_repr_magic_method():
    r = Registry()

    r.add(foo)

    res = r.__repr__()
    assert res == "('foo',)"

    r.add(bar)

    res = r.__repr__()
    assert res == "('foo', 'bar')"


def test_len_magic_method():
    r = Registry()

    r.add(foo)

    res = len(r)
    assert res == 1

    r.add(bar)

    res = len(r)
    assert res == 2


def test_getitem_magic_method():
    r = Registry()

    r.add(foo)

    res = r["foo"]
    assert res == foo


def test_iter_magic_method():
    r = Registry()

    r.add(foo)

    res = next(iter(r))
    assert res == "foo"


def test_contains_magic_method():
    r = Registry()

    r.add(foo)

    assert "foo" in r


def test_setitem_magic_method():
    r = Registry()

    r["bar"] = foo

    assert "bar" in r._factories


def test_delitem_magic_method():
    r = Registry()

    r.add(foo)

    del r["foo"]
    assert r._factories == {}
