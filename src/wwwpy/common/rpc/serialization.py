import json
from dataclasses import is_dataclass, fields, dataclass
from datetime import datetime
from typing import Any, Type, get_origin, get_args


# todo this should also receive the expected cls Type.
# this way we can check that the instance is of the expected type
def serialize(obj: Any, cls: Type) -> Any:
    origin = get_origin(cls)
    if origin is not None:
        if not isinstance(obj, origin):
            raise ValueError(f"Expected object of type {origin}, got {type(obj)}")
    elif not isinstance(obj, cls):
        raise ValueError(f"Expected object of type {cls}, got {type(obj)}")
    if is_dataclass(obj):
        return {
            field.name: serialize(getattr(obj, field.name), field.type)
            for field in fields(obj)
        }
    elif isinstance(obj, list):
        item_type = get_args(cls)[0]
        return [serialize(item, item_type) for item in obj]
    elif isinstance(obj, tuple):
        return [serialize(item, get_args(cls)[i]) for i, item in enumerate(obj)]
        # return [serialize(item) for item in obj]
    # elif isinstance(obj, dict):
    #     return {key: serialize(value) for key, value in obj.items()}
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


def deserialize(data: Any, cls: Type) -> Any:
    if is_dataclass(cls):
        field_types = {field.name: field.type for field in fields(cls)}
        return cls(**{
            field_name: deserialize(data.get(field_name), field_type)
            for field_name, field_type in field_types.items()
        })
    elif get_origin(cls) == list or cls == list:
        item_type = get_args(cls)[0]
        return [deserialize(item, item_type) for item in data]
    elif get_origin(cls) == tuple or cls == tuple:
        item_type = get_args(cls)[0]
        return tuple(deserialize(item, item_type) for item in data)
    # elif get_origin(cls) == dict:
    #     key_type, value_type = get_args(cls)
    #     return {
    #         deserialize(key, key_type): deserialize(value, value_type)
    #         for key, value in data.items()
    #     }
    elif cls == datetime:
        return datetime.fromisoformat(data)
    else:
        return data


def to_json(obj: Any, cls: Type) -> str:
    return json.dumps(serialize(obj, cls))


def from_json(json_str: str, cls: Type) -> Any:
    data = json.loads(json_str)
    return deserialize(data, cls)
