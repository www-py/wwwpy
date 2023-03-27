from __future__ import annotations

import inspect
import zipfile
from abc import ABC
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterator, Callable, Optional
from zipfile import ZipFile


@dataclass(frozen=True)
class Resource(ABC):
    arcname: str


@dataclass(frozen=True)
class StringResource(Resource):
    content: str


@dataclass(frozen=True)
class PathResource(Resource):
    filepath: Path


ResourceIterator = Iterator[Resource]
ResourceFilter = Callable[[Resource], Optional[Resource]]


def default_resource_filter(resource: Resource) -> Optional[Resource]:
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
        resource_filter: ResourceFilter = default_resource_filter
) -> ResourceIterator:
    relative_to_defined: Path = folder if relative_to is None else relative_to

    def recurse(path: Path) -> ResourceIterator:
        for f in path.glob('*'):
            rel = f.relative_to(relative_to_defined)
            candidate = PathResource(str(rel), f)
            item = resource_filter(candidate)
            if item is not None:
                if f.is_file():
                    yield item
                else:
                    yield from recurse(f)

    yield from recurse(folder)
    return iter(())


def build_archive(item_iterator: Iterator[Resource]) -> bytes:
    stream = BytesIO()
    zip_file = ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=1)
    for item in item_iterator:
        if isinstance(item, PathResource):
            zip_file.write(item.filepath, item.arcname)
        elif isinstance(item, StringResource):
            zip_file.writestr(item.arcname, item.content)
        else:
            raise Exception(f'Unhandled class \n  type={type(item).__name__} \n  data={item}')
    zip_file.close()

    stream.seek(0)
    return stream.getbuffer().tobytes()


def stacktrace_pathfinder(stack_backtrack: int = 1) -> Optional[Path]:
    wwwpy_root = Path(__file__).resolve().parent

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
