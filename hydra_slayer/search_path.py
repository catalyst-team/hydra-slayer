from typing import Any, List, Optional, Tuple, Union
from dataclasses import dataclass
import pydoc

SearchPathEntryDescription = Union[str, Tuple[str, str]]


@dataclass
class SearchPathEntry:
    path: str
    alias: str

    def is_referenced_by(self, name: str) -> bool:
        """@TODO: Docs. Contribution is welcome."""
        name_prefix = name.split(".")[0]
        return name_prefix == self.alias

    def resolve(self, name: str) -> str:
        """@TODO: Docs. Contribution is welcome."""
        if not self.is_referenced_by(name):
            raise ValueError("Can't resolve")  # FIXME: change to a specific excpetion

        name = name.split(".")
        return ".".join([self.path] + name[1:])

    @staticmethod
    def from_description(description: SearchPathEntryDescription) -> "SearchPathEntry":
        """@TODO: Docs. Contribution is welcome."""
        if isinstance(description, str):
            path = description
            _, _, alias = description.rpartition(".")
        else:
            path, alias = description

        return SearchPathEntry(path=path, alias=alias)


class SearchPath:
    def __init__(self, path_entries: List[SearchPathEntry] = None):
        """@TODO: Docs. Contribution is welcome."""
        self.path_entries = path_entries or []

    def locate(self, name: str) -> Optional[Any]:
        """@TODO: Docs. Contribution is welcome."""
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
        if not isinstance(other, SearchPath):
            return False
        return self.path_entries == other.path_entries

    @staticmethod
    def from_description(description: List[SearchPathEntryDescription]):
        """@TODO: Docs. Contribution is welcome."""
        path_entries = [SearchPathEntry.from_description(x) for x in description]
        return SearchPath(path_entries)
