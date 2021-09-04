from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Tuple, Union
from collections import abc
import inspect
import warnings

from hydra_slayer import functional as F
from hydra_slayer.factory import default_meta_factory, Factory, MetaFactory

__all__ = ["Registry"]

LateAddCallback = Callable[["Registry"], None]


class Registry(abc.MutableMapping):
    """
    Universal class allowing to add and access various factories by name.

    Args:
        meta_factory: default object that calls factory.
            Default: :py:func:`.factory.default_meta_factory`
        name_key: key to use to extract names of the factories from
    """

    def __init__(self, meta_factory: MetaFactory = None, name_key: str = "_target_"):
        self.meta_factory = meta_factory if meta_factory is not None else default_meta_factory
        self._factories: Dict[str, Factory] = {}
        self._late_add_callbacks: List[LateAddCallback] = []
        self.name_key = name_key

    @staticmethod
    def _get_factory_name(f, provided_name: str = None) -> str:
        if not provided_name:
            provided_name = getattr(f, "__name__", None)
            if not provided_name:
                raise ValueError(f"Factory {f} has no '__name__' and no name was provided")
            if provided_name == "<lambda>":
                raise ValueError("Name for lambda factories must be provided")
        return provided_name

    def _do_late_add(self):
        if self._late_add_callbacks:
            for cb in self._late_add_callbacks:
                cb(self)
            self._late_add_callbacks = []

    def add(
        self,
        factory: Factory = None,
        *factories: Factory,
        name: str = None,
        **named_factories: Factory,
    ) -> Factory:
        """
        Adds factory to registry with it's ``__name__`` attribute or provided
        name. Signature is flexible.

        Args:
            factory: factory instance
            factories: more instances
            name: name to use for the first factory instance,
                if a single instance is passed
            named_factories: factory and their names as \*\*kwargs

        Returns:
            first factory passed

        Raises:
            ValueError: if multiple factories with a single name are provided
            LookupError: if factory with provided name is already registered
        """
        if len(factories) > 0 and name is not None:
            raise ValueError("Multiple factories with single name are not allowed")

        if factory is not None:
            named_factories[self._get_factory_name(factory, name)] = factory

        if len(factories) > 0:
            new = {self._get_factory_name(f): f for f in factories}
            named_factories.update(new)

        if len(named_factories) == 0:
            warnings.warn("No factories were provided!")

        for name, f in named_factories.items():
            # self._factories[name] != f is a workaround for
            # https://github.com/catalyst-team/catalyst/issues/135
            if name in self._factories and self._factories[name] != f:
                raise LookupError(
                    f"Factory with name '{name}' is already present\n"
                    f"Already registered: '{self._factories[name]}'\n"
                    f"New: '{f}'"
                )

        self._factories.update(named_factories)

        return factory

    def late_add(self, cb: LateAddCallback):
        """
        Allows to prevent cycle imports by delaying some imports till next
        registry query.

        Args:
            cb: callback receives registry and must call it's methods to
                register factories
        """
        self._late_add_callbacks.append(cb)

    def add_from_module(
        self, module, prefix: Union[str, List[str]] = None, ignore_all: bool = False
    ) -> None:
        """
        Adds all factories present in module.
        If ``__all__`` attribute is present, takes ony what mentioned in it.

        Args:
            module: module to scan
            prefix: prefix string for all the module's factories.
                If prefix is a list, all values will be treated as aliases
            ignore_all: if ``True``, ignores ``__all__`` attribute of the module

        Raises:
            TypeError: if prefix is not a list or a string
        """
        factories = {
            k: v for k, v in module.__dict__.items() if inspect.isclass(v) or inspect.isfunction(v)
        }

        if ignore_all:
            names_to_add = list(factories.keys())
        else:
            # filter by __all__ if present
            names_to_add = getattr(module, "__all__", list(factories.keys()))

        if prefix is None:
            prefix = [""]
        elif isinstance(prefix, str):
            prefix = [prefix]
        elif isinstance(prefix, list):
            if any((not isinstance(p, str)) for p in prefix):
                raise TypeError("All prefix in list must be strings.")
        else:
            raise TypeError(f"Prefix must be a list or a string, got {type(prefix)}.")

        to_add = {f"{p}{name}": factories[name] for p in prefix for name in names_to_add}
        self.add(**to_add)

    def get(self, name: str) -> Optional[Factory]:
        """
        Retrieves factory, without creating any objects with it
        or raises error.

        Args:
            name: factory name

        Returns:
            factory by name
        """
        self._do_late_add()

        if name is None:
            return None

        res = self._factories.get(name, None)
        if res is None:
            res = F.get_factory(name)

        return res

    def get_if_str(self, obj: Union[str, Factory]):
        """Returns object from the registry if ``obj`` type is string."""
        if isinstance(obj, str):
            return self.get(obj)
        return obj

    def get_instance(self, *args, meta_factory: Optional[MetaFactory] = None, **kwargs):
        """
        Creates instance by calling specified factory with ``instantiate_fn``.

        Args:
            *args: \*args to pass to the factory
            meta_factory: function that calls factory the right way.
                Default: :py:func:`.factory.default_meta_factory`
            **kwargs: \*\*kwargs to pass to the factory

        Returns:
            created instance
        """
        instance = F._get_instance(
            factory_key=self.name_key,
            get_factory_func=self.get,
            meta_factory=meta_factory or self.meta_factory,
            args=args,
            kwargs=kwargs,
        )
        return instance

    def get_from_params(
        self, *, shared_params: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Union[Any, Tuple[Any, Mapping[str, Any]]]:
        """
        Creates instance based in configuration dict with ``instantiation_fn``.
        If ``config[name_key]`` is None, ``None`` is returned.

        Args:
            shared_params: params to pass on all levels in case of recursive creation
            **kwargs: \*\*kwargs to pass to the factory

        Returns:
            result of calling ``instantiate_fn(factory, **sub_kwargs)``
        """
        instance = F._recursive_get_from_params(
            factory_key=self.name_key,
            get_factory_func=self.get,
            params=kwargs,
            shared_params=shared_params or {},
        )
        return instance

    def all(self) -> Iterable[str]:
        """Returns list with names of all registered items."""
        self._do_late_add()
        result = tuple(self._factories.keys())

        return result

    def __str__(self) -> str:
        """Returns a string of registered items."""
        return self.all().__str__()

    def __repr__(self) -> str:
        """Returns a string representation of registered items."""
        return self.all().__str__()

    # mapping methods
    def __len__(self) -> int:
        """Returns length of registered items."""
        self._do_late_add()
        return len(self._factories)

    def __getitem__(self, name: str) -> Optional[Factory]:
        """Returns a value from the registry by name."""
        return self.get(name)

    def __iter__(self) -> Iterator[str]:
        """Iterates over all registered items."""
        self._do_late_add()
        return self._factories.__iter__()

    def __contains__(self, name: str):
        """Check if a particular name was registered."""
        self._do_late_add()
        return self._factories.__contains__(name)

    def __setitem__(self, name: str, factory: Factory) -> None:
        """Add a new factory by giving name."""
        self.add(factory, name=name)

    def __delitem__(self, name: str) -> None:
        """Removes a factory by giving name."""
        self._factories.pop(name)
