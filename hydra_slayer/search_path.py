from typing import Any, List, Optional, Sequence, Union
from dataclasses import dataclass
import pydoc

SearchPathEntryDescription = Union[str, Sequence[str]]


@dataclass
class SearchPathEntry:
    """
    A single search path entry. Consists of an actual path to a Python object and its alias.
    If alias wasn't provided then the last dot-separated part of path is treated as an alias.
    """

    path: str
    alias: str

    def is_referenced_by(self, name: str) -> bool:
        """
        Args:
            name: An import path to some Python object

        Returns:
            True: when this SearchPathEntry corresponds to an object referenced by name
            or to its top-level parent module.
            False: otherwise
        """
        name_prefix = name.split(".")[0]
        return name_prefix == self.alias

    def resolve(self, name: str) -> str:
        """
        Resolve path to a python object referenced by name.

        Args:
            name: an import path to a Python object

        Returns:
            A full path to a Python object resolved with this SearchPathEntry

        Raises:
            ValueError: When name can't be resolved with this instance of SearchPathEntry.
                Check it with SearchPathEntry.is_referenced_by before
        """
        if not self.is_referenced_by(name):
            raise ValueError(
                f"Can't resolve {name}. It is not referenced by the current SearchPathEntry"
            )

        name = name.split(".")
        return ".".join([self.path] + name[1:])

    @staticmethod
    def from_description(description: SearchPathEntryDescription) -> "SearchPathEntry":
        """
        Args:
            description: Config description of a SearchPathEntry.
            Either a string or Tuple[str, str].
            When passing a Tuple[str, str], its second component
            is treated as an alias for a provided path.

        Returns:
            A SearchPathEntry object corresponding to provided description

        Raises:
            TypeError: when description is of invalid type
        """
        if isinstance(description, str):
            path = description
            _, _, alias = description.rpartition(".")
        elif SearchPathEntry._is_valid_descriptor_with_alias(description):
            path, alias = description
        else:
            raise TypeError(
                f"{description} is not a valid descriptor for SearchPathEntry, "
                f"provide either str or Sequence[str] of length two"
            )

        return SearchPathEntry(path=path, alias=alias)

    @staticmethod
    def _is_valid_descriptor_with_alias(descriptor):
        return (
            isinstance(descriptor, Sequence)
            and all(isinstance(x, str) for x in descriptor)
            and len(descriptor) == 2
        )


class SearchPath:
    """
    This class represents search path for Python objects which wasn't added to Registry explicitly,
    but referenced by their import path with possible aliases.

    This class contains a list of locations to look for Python objects,
    with possible aliases for these locations.
    """

    def __init__(self, path_entries: List[SearchPathEntry] = None):
        """Constructor"""
        self.path_entries = path_entries or []

    def locate(self, name: str) -> Optional[Any]:
        """
        Args:
            name: import path of some python object

        Returns:
            Python object referenced by name or None if such objects can't be found.
        """
        res = pydoc.locate(name)
        if res is not None:
            return res

        for entry in self.path_entries:
            if not entry.is_referenced_by(name):
                continue

            res = pydoc.locate(entry.resolve(name))
            if res is not None:
                return res

    def __eq__(self, other):
        """Just a generic equality method"""
        return isinstance(other, SearchPath) and self.path_entries == other.path_entries

    @staticmethod
    def from_description(description: List[SearchPathEntryDescription]):
        """
        Args:
            description: Config description of a SearchPath.
            A list of config descriptions of SearchPathEntries.

        Returns:
            A SearchPath object corresponding to provided description
        """
        path_entries = [SearchPathEntry.from_description(x) for x in description]
        return SearchPath(path_entries)
