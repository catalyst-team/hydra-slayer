from typing import Any, Callable, Mapping, Tuple, Type, Union
import copy
import functools
import inspect

__all__ = [
    "metafactory_factory",
    "call_meta_factory",
    "partial_meta_factory",
    "default_meta_factory",
]

Factory = Union[Type, Callable[..., Any]]

DEFAULT_FROM_PARAMS_KEY = "get_from_params"
DEFAULT_META_FACTORY_KEY = "_meta_factory_"
DEFAULT_CALL_MODE_KEY = "_mode_"  # TODO: discuss with @scitator and rename


def metafactory_factory(factory: Factory, args: Tuple, kwargs: Mapping):
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
        >>> metafactory_factory(int, (42,))
        42
        >>> metafactory_factory(lambda x: x, (42,))()  # note that additional () are used
        42
        >>> metafactory_factory(lambda x: x, (42,), {'_mode_': 'call'})
        42
        >>> metafactory_factory(int, ('2A'), {'base': 16})
        42
        >>> hex_to_dec = metafactory_factory(int, (), {'_mode_': 'partial', 'base': 16})
        >>> hex_to_dec('2A')
        42
    """
    # make a copy of kwargs since we don't want to modify them directly
    kwargs = copy.copy(kwargs)
    meta_factory = kwargs.pop(DEFAULT_META_FACTORY_KEY, None)
    meta_factory_name = kwargs.pop(DEFAULT_CALL_MODE_KEY, "auto")

    # legacy, for the compatibility with the Catalyst library
    if hasattr(factory, DEFAULT_FROM_PARAMS_KEY):
        return getattr(factory, DEFAULT_FROM_PARAMS_KEY)(*args, **kwargs)

    if meta_factory is None:
        meta_factories = {
            "auto": default_meta_factory,
            "call": call_meta_factory,
            "partial": partial_meta_factory,
        }
        if meta_factory_name not in meta_factories.keys():
            raise ValueError(f"'{meta_factory_name}' is not a valid call mode")
        meta_factory = meta_factories[meta_factory_name]

    return meta_factory(factory, args=args, kwargs=kwargs)


def call_meta_factory(factory: Factory, args: Tuple, kwargs: Mapping):
    """Creates a new instance from ``factory``.

    Args:
        factory: factory to create instance from
        args: \*args to pass to the factory
        kwargs: \*\*kwargs to pass to the factory

    Returns:
        Instance.

    Examples:
        >>> call_meta_factory(int, (42,), {})
        42
        >>> call_meta_factory(int, ('2A',), {'base': 16})
        66
        >>> call_meta_factory(lambda x: x, (42,), {})
        42
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

    Examples:
        >>> get_answer_to_life = partial_meta_factory(lambda x: x, (42,), {})
        >>> get_answer_to_life()
        42
        >>> hex_to_dec = partial_meta_factory(int, (), {'base': 16})
        >>> hex_to_dec('2A')
        42
    """
    return functools.partial(factory, *args, **kwargs)


def default_meta_factory(factory: Factory, args: Tuple, kwargs: Mapping):
    """Returns a new instance or a new partial object.

    Creates a new instance from ``factory`` if ``factory`` is class
    (behaves like :py:func:`call_meta_factory`), else returns a new
    partial object (behaves like :py:func:`partial_meta_factory`).

    Args:
        factory: factory to create instance from
        args: \*args to pass to the factory
        kwargs: \*\*kwargs to pass to the factory

    Returns:
        Instance.

    Raises:
        ValueError: if factory object is not callable.

    Examples:
        >>> default_meta_factory(int, (42,), {})
        42
        >>> default_meta_factory(int, ('2A',), {'base': 16})
        42
        >>> get_answer_to_life = default_meta_factory(lambda x: x, (42,), {})
        >>> get_answer_to_life()
        42
    """
    if inspect.isclass(factory):
        obj = call_meta_factory(factory, args, kwargs)
    elif inspect.ismethod(factory) or inspect.isfunction(factory):
        obj = partial_meta_factory(factory, args, kwargs)
    else:
        raise ValueError(f"factory '{factory}' is not callable")
    return obj
