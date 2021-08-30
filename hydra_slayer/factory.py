from typing import Any, Callable, Mapping, Tuple, Type, Union
import functools
import inspect

__all__ = ["call_meta_factory", "partial_meta_factory", "default_meta_factory"]

Factory = Union[Type, Callable[..., Any]]
MetaFactory = Callable[[Factory, Tuple, Mapping], Any]


def call_meta_factory(factory: Factory, args: Tuple, kwargs: Mapping):
    """Creates a new instance from ``factory``.

    Args:
        factory: factory to create instance from
        args: \*args to pass to the factory
        kwargs: \*\*kwargs to pass to the factory

    Returns:
        Instance.

    """
    return factory(*args, **kwargs)


def partial_meta_factory(factory: Factory, args: Tuple, kwargs: Mapping):
    """
    Returns a new partial object which when called will behave like func called
    with the positional arguments ``args`` and keyword arguments ``kwargs``.

    Args:
        factory: factory to create instance from
        args: \*args to merge into the factory
        kwargs: \*\*kwargs to merge into the factory

    Returns:
        Partial object.

    """
    return functools.partial(factory, *args, **kwargs)


def default_meta_factory(factory: Factory, args: Tuple, kwargs: Mapping):
    """
    Creates a new instance from ``factory`` if ``factory`` is class
    (like :py:func:`call_meta_factory`), else returns a new partial object
    (like :py:func:`partial_meta_factory`).

    Args:
        factory: factory to create instance from
        args: \*args to pass to the factory
        kwargs: \*\*kwargs to pass to the factory

    Returns:
        Instance.

    """
    if inspect.isfunction(factory):
        return partial_meta_factory(factory, args, kwargs)
    return call_meta_factory(factory, args, kwargs)
