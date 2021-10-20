from typing import Any, Callable, Mapping, Tuple, Type, Union
import copy
import functools
import inspect

__all__ = ["call_meta_factory", "partial_meta_factory", "default_meta_factory"]

Factory = Union[Type, Callable[..., Any]]
MetaFactory = Callable[[Factory, Tuple, Mapping], Any]

DEFAULT_CALL_MODE_KEY = "_mode_"


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
    """Returns a new instance or a new partial object.

      * _mode_='auto'

        Creates a new instance from ``factory`` if ``factory`` is class
        (like :py:func:`call_meta_factory`), else returns a new partial object
        (like :py:func:`partial_meta_factory`).

      * _mode_='call'

        Returns a result of the factory called with the positional arguments
        ``args`` and keyword arguments ``kwargs``.

      * _mode_='partial'

        Returns a new partial object which when called will behave like factory
        called with the positional arguments ``args`` and keyword arguments
        ``kwargs``.

    Args:
        factory: factory to create instance from
        args: \*args to pass to the factory
        kwargs: \*\*kwargs to pass to the factory

    Returns:
        Instance.

    Raises:
        ValueError: if mode not in list: ``'auto'``, ``'call'``, ``'partial'``.

    Examples:
        >>> default_meta_factory(int, (42,))
        42

        >>> # please note that additional () are used
        >>> default_meta_factory(lambda x: x, (42,))()
        42

        >>> default_meta_factory(int, ('42',), {"base": 16})
        66

        >>> # please note that additional () are not needed
        >>> default_meta_factory(lambda x: x, (42,), {"_mode_": "call"})
        42

        >>> default_meta_factory(lambda x: x, ('42',), {"_mode_": "partial", "base": 16})()
        66
    """
    # make a copy of kwargs since we don't want to modify them directly
    kwargs = copy.copy(kwargs)
    mode = kwargs.pop(DEFAULT_CALL_MODE_KEY, "auto")
    if mode not in {"auto", "call", "partial"}:
        raise ValueError(f"`{mode}` is not a valid call mode")

    if mode == "auto" and inspect.isfunction(factory) or mode == "partial":
        return partial_meta_factory(factory, args, kwargs)
    return call_meta_factory(factory, args, kwargs)
