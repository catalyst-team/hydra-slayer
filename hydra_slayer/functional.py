from typing import Any, Callable, Dict, Iterable, Optional, Tuple, TypeVar, Union
import copy
import inspect
import pydoc

from hydra_slayer.factory import default_meta_factory, Factory, MetaFactory

__all__ = ["get_factory", "get_instance", "get_from_params"]

T = TypeVar("T")

DEFAULT_FACTORY_KEY = "_target_"


def _extract_factory_name_arg(
    factory_key: str = DEFAULT_FACTORY_KEY, args: Iterable = None, kwargs: Dict = None
) -> Tuple[Optional[str], Iterable, Dict]:
    args, kwargs = args or (), kwargs or {}

    factory_name = kwargs.pop(factory_key, None)
    if factory_name is None and args:
        factory_name, *args = args

    return factory_name, args, kwargs


def _extract_positional_keyword_vars(func: Callable, kwargs: Dict) -> Tuple[Iterable, Dict]:
    # make a copy of kwargs since we don't want to modify them directly
    kwargs = copy.copy(kwargs)

    signature = inspect.signature(func)
    type2param = {p.kind: name for name, p in signature.parameters.items()}

    var_kwarg = kwargs.pop(type2param.get(inspect.Parameter.VAR_KEYWORD), {})
    kwargs.update(var_kwarg)

    args = kwargs.pop(type2param.get(inspect.Parameter.VAR_POSITIONAL), ())

    return args, kwargs


def get_factory(name_or_object: Union[str, T]) -> Union[Factory, T]:
    """Retrieves factory, without creating any objects with it.

    Args:
        name_or_object: factory name or any valid python object

    Returns:
        factory

    Raises:
        LookupError: if no factory with provided name was registered

    Examples:
        >>> to_int = get_factory("int")
        >>> to_int("42")
        42
    """
    if isinstance(name_or_object, str):
        factory = pydoc.locate(name_or_object)
        if not factory:
            raise LookupError(f"No factory with name '{name_or_object}' was registered")

        return factory
    return name_or_object


def _meta_factory_call(
    factory: Factory, meta_factory: MetaFactory, args: Iterable, kwargs: Dict
) -> Any:
    if hasattr(factory, "get_from_params"):
        return factory.get_from_params(*args, **kwargs)
    return meta_factory(factory, args, kwargs)


def _get_instance(
    factory_key: str = DEFAULT_FACTORY_KEY,
    get_factory_func: Callable = None,
    meta_factory: Optional[MetaFactory] = None,
    args: Optional[Iterable] = None,
    kwargs: Optional[Dict] = None,
) -> Any:
    """Creates instance by calling specified factory with ``instantiate_fn``.

    Note:
        The name of the factory to use must be provided as the first argument
        or directly by ``'_target_'`` keyword.

    Args:
        factory_key: key to extract factory name from
        get_factory_func: function that returns factory by its name.
            Default: :py:func:`.functional.get_factory`
        meta_factory: function that calls factory in the right way.
            Default: :py:func:`.factory.default_meta_factory`
        args: \*args to pass to the factory
        kwargs: \*\*kwargs to pass to the factory

    Returns:
        created instance

    Raises:
        TypeError: if factory name argument is missing
        RuntimeError: if could not create object instance
    """
    get_factory_func = get_factory_func or get_factory
    meta_factory = meta_factory or default_meta_factory
    args, kwargs = args or (), kwargs or {}

    # assume that name of the factory can be provided as first argument
    #  or directly by keyword
    name, args, kwarg = _extract_factory_name_arg(
        factory_key=factory_key, args=args, kwargs=kwargs
    )
    if name is None:
        raise TypeError(f"get_instance() missing at least 1 required argument: '{factory_key}'")

    factory = get_factory_func(name)

    try:
        instance = _meta_factory_call(
            factory=factory, meta_factory=meta_factory, args=args, kwargs=kwargs
        )
        return instance
    except Exception as e:
        raise RuntimeError(f"Factory '{name}' call failed: args={args} kwargs={kwargs}") from e


def get_instance(*args, meta_factory: Optional[MetaFactory] = None, **kwargs) -> Any:
    """Creates instance by calling specified factory with ``instantiate_fn``.

    Note:
        The name of the factory to use should be provided as the first argument
        or directly by ``'_target_'`` keyword.

    Args:
        *args: positional arguments to pass to the factory
        meta_factory: function that calls factory in the right way.
            Default: :py:func:`.factory.default_meta_factory`
        **kwargs: named parameters to pass to the factory

    Returns:
        created instance

    Examples:
        >>> get_instance(int, "42", base=10)
        42
    """
    instance = _get_instance(meta_factory=meta_factory, args=args, kwargs=kwargs)
    return instance


def _recursive_get_from_params(
    factory_key: str,
    get_factory_func: Callable,
    params: Union[Dict[str, Any], Any],
    shared_params: Dict[str, Any],
) -> Any:
    if not isinstance(params, (dict, list)):
        return params

    # make a copy of params since we don't want to modify them directly
    params = copy.copy(params)

    view = params.items() if isinstance(params, dict) else enumerate(params)
    for key, param in view:
        params[key] = _recursive_get_from_params(
            factory_key=factory_key,
            get_factory_func=get_factory_func,
            params=param,
            shared_params=shared_params,
        )

    if isinstance(params, dict) and (factory_key in params or factory_key in shared_params):
        # use additional dict to handle 'multiple values for keyword argument'
        kwargs = {**shared_params, **params}

        factory_name, _, kwargs = _extract_factory_name_arg(
            factory_key=factory_key, args=(), kwargs=kwargs
        )
        factory = get_factory_func(factory_name)
        args, kwargs = _extract_positional_keyword_vars(factory, kwargs=kwargs)
        meta_factory = kwargs.pop("meta_factory", default_meta_factory)

        instance = _meta_factory_call(
            factory=factory, meta_factory=meta_factory, args=args, kwargs=kwargs
        )

        return instance
    return params


def get_from_params(*, shared_params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """
    Creates instance based in configuration dict with ``instantiation_fn``.

    Note:
        The name of the factory to use should be provided by ``'_target_'`` keyword.

    Args:
        shared_params: params to pass on all levels in case of recursive creation
        **kwargs: named parameters for factory

    Returns:
        result of calling ``instantiate_fn(factory, **sub_kwargs)``

    Examples:
        >>> get_from_params(_target_="torch.nn.Linear", in_features=20, out_features=30)
        Linear(in_features=20, out_features=30, bias=True)
    """
    instance = _recursive_get_from_params(
        factory_key=DEFAULT_FACTORY_KEY,
        get_factory_func=get_factory,
        params=kwargs,
        shared_params=shared_params or {},
    )
    return instance
