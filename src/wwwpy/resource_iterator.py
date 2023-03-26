from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import PathLike
from pathlib import Path
from typing import Iterator, Callable, Optional


class Content(ABC):
    @abstractmethod
    def as_bytes(self, content: bytes) -> None: ...

    @abstractmethod
    def as_string(self, content: str) -> str: ...


@dataclass(frozen=True)
class Resource(ABC):
    arcname: str

    @abstractmethod
    def access_content(self, content: Content) -> None: ...


@dataclass(frozen=True)
class StringResource(Resource):
    content: str

    def access_content(self, content: Content) -> None:
        content.as_string(self.content)


@dataclass(frozen=True)
class PathResource(Resource):
    filepath: Path

    def access_content(self, content: Content) -> None:
        content.as_bytes(self.filepath.read_bytes())


ResourceIterator = Iterator[Resource]
ResourceFilter = Callable[[Resource], Optional[Resource]]


def default_item_filter(resource: Resource) -> Optional[Resource]:
    if not isinstance(resource, PathResource):
        return resource
    filepath = resource.filepath
    if filepath.name == '.DS_Store':
        return None
    if filepath.name == '__pycache__' and filepath.is_dir():
        return None
    return resource


def from_filesystem(
        folder: Path, relative_to: Path | None = None,
        item_filter: ResourceFilter = default_item_filter
) -> ResourceIterator:
    relative_to_defined: Path = folder if relative_to is None else relative_to

    def recurse(path: Path) -> ResourceIterator:
        for f in path.glob('*'):
            rel = f.relative_to(relative_to_defined)
            candidate = PathResource(str(rel), f)
            item = item_filter(candidate)
            if item is not None:
                if f.is_file():
                    yield item
                else:
                    yield from recurse(f)

    yield from recurse(folder)
    return iter(())
