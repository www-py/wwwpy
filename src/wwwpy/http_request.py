from typing import NamedTuple, Union


class HttpRequest(NamedTuple):
    method: str
    content: Union[str, bytes]
    content_type: str
