import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Any, Optional, Dict, Iterable

from wwwpy.common import tree
from wwwpy.common.rpc import serialization
from wwwpy.server.filesystem_sync import Event


@dataclass
class Operation:
    op_type: str
    is_dir: bool
    path: str
    was: str = ""
    content_bytes: Optional[bytes] = None
    content_str: Optional[str] = None


@dataclass
class Node:
    path: str
    is_directory: bool
    original_path: str = ""
    deleted: bool = False
    modified: bool = False
    children: Dict[str, 'Node'] = field(default_factory=dict)
    content_bytes: Optional[bytes] = None
    content_str: Optional[str] = None

    # validate in post init
    def __post_init__(self):
        if '//' in self.path:
            raise ValueError(f'Invalid path: {self.path}')

    def str(self):
        return f'{self.path} is_dir={self.is_directory} del={self.deleted} mod={self.modified} op={self.original_path}'


def sync_source(source: Path, events: List[Event]) -> List[Any]:
    res = make_summary(source, events)
    ser = serialization.serialize(res.root, Node)
    return ser


def _append_file(result, name, path):
    if path.is_file() and path.exists():
        operation = Operation(op_type='write', is_dir=False, path=str(name))
        _set_content(operation, path)
        result.append(operation)


def _set_content(obj, path: Path):
    assert path.exists()
    assert path.is_file()
    try:
        obj.content_str = path.read_text()
    except UnicodeDecodeError:
        obj.content_bytes = path.read_bytes()


def sync_target(target_root: Path, changes: List[Any]) -> None:
    res = serialization.deserialize(changes, Node)
    apply_summary(target_root, res)


def _apply_node(target: Path, node: Node):
    node_target = target / node.path.strip('/')
    if node.deleted:
        if node.is_directory:
            shutil.rmtree(node_target, ignore_errors=True)
        else:
            node_target.unlink()
        return

    if node.modified:
        if node.is_directory:
            node_target.mkdir(exist_ok=True)
        else:
            if node.content_str:
                node_target.write_text(node.content_str)
            elif node.content_bytes:
                node_target.write_bytes(node.content_bytes)


def apply_summary(target_root: Path, node: Node) -> None:
    for child in node.children.values():
        _apply_node(target_root, child)


def sync_init(source: Path) -> List[Any]:
    summary = _make_initial_summary(source)
    serialize = serialization.serialize(summary, List[Operation])
    return serialize


def _make_initial_summary(source: Path) -> List[Operation]:
    result = []
    for path in source.rglob('*'):
        _append_file(result, path.relative_to(source), path)
    return result


@dataclass
class _NodePrint(tree.NodeProtocol):
    node: Node

    def iterdir(self) -> Iterable[tree.NodeProtocol]:
        return [_NodePrint(child) for child in self.node.children.values()]

    def is_dir(self) -> bool:
        return self.node.is_directory

    @property
    def name(self) -> str:
        return self.node.str().strip('/')


def print_node(node: Node, printer=print):
    for line in tree.tree(_NodePrint(node)):
        printer(line)


class FileSystemTree:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.root = Node("/", True)

    def get_or_create_node(self, path: str, is_directory: bool) -> Node:
        if path == '/':
            return self.root
        parts = path.strip("/").split("/")
        current = self.root

        for i, part in enumerate(parts):
            if part not in current.children:
                is_last = i == len(parts) - 1
                is_dir = is_directory if is_last else True
                name = f'{current.path}{part}' + ('' if is_last else '/')
                current.children[part] = Node(name, is_dir)
            current = current.children[part]

        return current

    def apply_event(self, event: Event):
        if event.event_type == "created":
            node = self.get_or_create_node(event.src_path, event.is_directory)
            node.deleted = False
        elif event.event_type == "deleted":
            node = self.get_or_create_node(event.src_path, event.is_directory)
            node.deleted = True
        elif event.event_type == "modified":
            node = self.get_or_create_node(event.src_path, event.is_directory)
            node.modified = True
            if not event.is_directory:
                real_path = self.root_path / event.src_path.strip('/')
                _set_content(node, real_path)
        elif event.event_type == "moved":
            src_node = self.get_or_create_node(event.src_path, event.is_directory)
            dest_node = self.get_or_create_node(event.dest_path, event.is_directory)

            if not src_node.original_path:
                src_node.original_path = src_node.path

            dest_node.original_path = src_node.original_path
            dest_node.is_directory = src_node.is_directory
            dest_node.modified = src_node.modified
            dest_node.children = src_node.children

            parent_path = str(Path(event.src_path).parent)
            parent = self.get_or_create_node(parent_path, True)
            del parent.children[Path(event.src_path).name]

    def print(self):
        print('=' * 50)
        print_node(self.root)

    def optimize(self):
        def _optimize(node: Node):
            if node.deleted:
                node.children.clear()
                node.modified = False
            else:
                node.children = {name: child for name, child in node.children.items() if
                                 not child.deleted or child.children}
                for child in node.children.values():
                    _optimize(child)

        _optimize(self.root)


def make_summary(root_path: Path, events: List[Event]) -> FileSystemTree:
    fs_tree = FileSystemTree(root_path)

    for event in events:
        ev_stripped = event.strip_container(str(root_path))
        fs_tree.apply_event(ev_stripped)
    fs_tree.print()
    # fs_tree.optimize()
    return fs_tree
