from __future__ import annotations

import inspect
import zipfile
from abc import ABC
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterator, Callable, Optional, TypeVar, Iterable
from zipfile import ZipFile

from wwwpy.common.iterlib import CallableToIterable

parent = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Resource(ABC):
    """represents something (a file) to be transferred to the remote"""
    arcname: str


@dataclass(frozen=True)
class StringResource(Resource):
    content: str


@dataclass(frozen=True)
class PathResource(Resource):
    filepath: Path


# https://docs.python.org/3/library/collections.abc.html
# https://wiki.python.org/moin/Iterator
TResource = TypeVar("TResource", bound=Resource)

ResourceAccept = Callable[[TResource], bool]

_directory_blacklist = {'.mypy_cache', '__pycache__'}


def default_resource_accept(resource: Resource) -> bool:
    if not isinstance(resource, PathResource):
        return True
    filepath = resource.filepath
    if filepath.name == '.DS_Store':
        return False
    if filepath.is_dir() and filepath.name in _directory_blacklist:
        return False
    return True


def from_filepath(file: Path, relative_to: Path) -> Iterable[PathResource]:
    def bundle() -> Iterator[PathResource]:
        rel = file.relative_to(relative_to)
        if file.is_file() and file.exists():
            yield PathResource(str(rel), file)

    return CallableToIterable(bundle)


def _recurse(path: Path, relative_to: Path, resource_accept: ResourceAccept) -> Iterator[PathResource]:
    for f in path.glob('*'):
        rel = f.relative_to(relative_to)
        candidate = PathResource(str(rel), f)
        if resource_accept(candidate):
            if f.is_file():
                yield candidate
            else:
                yield from _recurse(f, relative_to, resource_accept)


def from_filesystem(
        folder: Path, relative_to: Path | None = None,
        resource_accept: ResourceAccept = default_resource_accept
) -> Iterable[PathResource]:
    relative_to_defined: Path = folder if relative_to is None else relative_to

    def bundle() -> Iterator[PathResource]:
        yield from _recurse(folder, relative_to_defined, resource_accept)

    return CallableToIterable(bundle)


def build_archive(resource_iterator: Iterator[Resource]) -> bytes:
    """builds a zip archive from the given resources and returns the bytes"""
    stream = BytesIO()
    zip_file = ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1)
    for resource in resource_iterator:
        if isinstance(resource, PathResource):
            zip_file.write(resource.filepath, resource.arcname)
        elif isinstance(resource, StringResource):
            zip_file.writestr(resource.arcname, resource.content)
        else:
            raise Exception(f'Unhandled class \n  type={type(resource).__name__} \n  data={resource}')
    zip_file.close()

    stream.seek(0)
    return stream.getbuffer().tobytes()


def stacktrace_pathfinder(stack_backtrack: int = 1) -> Optional[Path]:
    wwwpy_root = parent

    for stack in inspect.stack():
        source_path = Path(stack.filename).resolve()
        if not _is_path_contained(source_path, wwwpy_root):
            stack_backtrack -= 1
            if stack_backtrack == 0:
                return source_path

    return None


def _is_path_contained(child: Path, parent: Path) -> bool:
    cl = len(child.parts)
    cp = len(parent.parts)
    if cl < cp:
        return False
    m = min(cl, cp)
    child_parts = child.parts[:m]
    parent_parts = parent.parts[:m]
    return child_parts == parent_parts


def library_resources() -> Iterable[PathResource]:
    """returns the resources from the wwwpy library itself"""
    return from_filesystem(parent, relative_to=parent.parent)
