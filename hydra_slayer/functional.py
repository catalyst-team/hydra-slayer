from typing import Any, Callable, Dict, Iterable, Optional, Tuple, TypeVar, Union
import copy
import inspect
import pydoc
import warnings

from hydra_slayer.factory import Factory, metafactory_factory

__all__ = ["get_factory", "get_instance", "get_from_params"]

T = TypeVar("T")

DEFAULT_FACTORY_KEY = "_target_"
DEFAULT_VAR_KEY = "_var_"
DEFAULT_ATTRS_DELIMITER = "."


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

    try:
        signature = inspect.signature(func)
        type2param = {p.kind: name for name, p in signature.parameters.items()}
    except ValueError:
        type2param = {}
        warnings.warn(
            f"No signature found for `{func}`, *args and **kwargs arguments cannot be extracted"
        )

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


def _get_instance(
    factory_key: str = DEFAULT_FACTORY_KEY,
    get_factory_func: Callable = None,
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
        args: \*args to pass to the factory
        kwargs: \*\*kwargs to pass to the factory

    Returns:
        created instance

    Raises:
        TypeError: if factory name argument is missing
        RuntimeError: if could not create object instance
    """
    get_factory_func = get_factory_func or get_factory
    args, kwargs = args or (), kwargs or {}

    # assume that name of the factory can be provided as first argument
    #  or directly by keyword
    name, args, kwarg = _extract_factory_name_arg(
        factory_key=factory_key, args=args, kwargs=kwargs
    )
    if name is None:
        raise TypeError(f"get_instance() missing at least 1 required argument: '{factory_key}'")

    factory = get_factory_func(name)

    args_, kwargs = _extract_positional_keyword_vars(factory, kwargs=kwargs)
    args = *args, *args_

    try:
        instance = metafactory_factory(factory=factory, args=args, kwargs=kwargs)
        return instance
    except Exception as e:
        raise RuntimeError(f"Factory '{name}' call failed: args={args} kwargs={kwargs}") from e


def get_instance(*args, **kwargs) -> Any:
    """Creates instance by calling specified factory with ``instantiate_fn``.

    Note:
        The name of the factory to use should be provided as the first argument
        or directly by ``'_target_'`` keyword.

    Args:
        *args: positional arguments to pass to the factory
        **kwargs: named parameters to pass to the factory

    Returns:
        created instance

    Examples:
        >>> get_instance(int, "42", base=10)
        42
    """
    instance = _get_instance(args=args, kwargs=kwargs)
    return instance


def _get_from_params(
    factory_key: str,
    get_factory_func: Callable,
    params: Dict[str, Any],
    shared_params: Dict[str, Any],
    var_key: str,
    attrs_delimiter: str,
    vars_dict: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    # use additional dict to handle 'multiple values for keyword argument'
    kwargs = {**shared_params, **params}

    params.pop(var_key, None)

    alias = kwargs.pop(var_key, "")
    alias, attribute_name = (
        alias.split(attrs_delimiter) if attrs_delimiter in alias else (alias, None)
    )

    if alias and alias in vars_dict:
        if factory_key in kwargs:
            raise ValueError(
                f"`{factory_key}` and `{var_key}` (in get mode) keywords are exclusive"
            )

        obj = vars_dict[alias]
        if attribute_name is not None:
            obj_or_callable = getattr(obj, attribute_name)
            if callable(obj_or_callable):
                args, kwargs = _extract_positional_keyword_vars(obj_or_callable, kwargs=kwargs)
                obj = obj_or_callable(*args, **kwargs)
            else:
                obj = obj_or_callable
    elif factory_key in kwargs:
        obj = _get_instance(
            factory_key=factory_key,
            get_factory_func=get_factory_func,
            args=(),
            kwargs=kwargs,
        )
    else:
        obj = params

    if alias and alias not in vars_dict:
        vars_dict[alias] = obj

    return obj, vars_dict


def _recursive_get_from_params(
    factory_key: str,
    get_factory_func: Callable,
    params: Union[Dict[str, Any], Any],
    shared_params: Dict[str, Any],
    var_key: str,
    attrs_delimiter: str,
    vars_dict: Dict[str, Any],
) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(params, (dict, list)):
        return params, vars_dict

    # make a copy of params since we don't want to modify them directly
    params = copy.copy(params)
    common_params = {
        "factory_key": factory_key,
        "get_factory_func": get_factory_func,
        "shared_params": shared_params,
        "var_key": var_key,
        "attrs_delimiter": attrs_delimiter,
    }

    view = params.items() if isinstance(params, dict) else enumerate(params)
    for key, param in view:
        params[key], vars_dict = _recursive_get_from_params(
            params=param, vars_dict=vars_dict, **common_params
        )

    if isinstance(params, dict):
        instance, vars_dict = _get_from_params(params=params, vars_dict=vars_dict, **common_params)
        return instance, vars_dict
    return params, vars_dict


def get_from_params(*, shared_params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
    """
    Creates instance based in configuration dict with ``instantiation_fn``.

    Note:
        The name of the factory to use should be provided
        by ``'_target_'`` keyword.

    Args:
        shared_params: params to pass on all levels in case of
            recursive creation
        **kwargs: named parameters for factory

    Returns:
        result of calling ``instantiate_fn(factory, **sub_kwargs)``

    Examples:
        >>> get_from_params(_target_="torch.nn.Linear", in_features=20, out_features=30)
        Linear(in_features=20, out_features=30, bias=True)
    """
    instance, _ = _recursive_get_from_params(
        factory_key=DEFAULT_FACTORY_KEY,
        get_factory_func=get_factory,
        params=kwargs,
        shared_params=shared_params or {},
        var_key=DEFAULT_VAR_KEY,
        vars_dict={},
        attrs_delimiter=DEFAULT_ATTRS_DELIMITER,
    )
    return instance
