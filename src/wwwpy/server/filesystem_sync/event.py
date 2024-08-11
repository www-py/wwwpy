from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    event_type: str
    is_directory: bool
    src_path: str
    dest_path: str
