import json
from dataclasses import is_dataclass, fields, dataclass
from typing import Any, Type, get_origin, get_args

def serialize(obj: Any) -> Any:
    if is_dataclass(obj):
        return {
            field.name: serialize(getattr(obj, field.name))
            for field in fields(obj)
        }
    elif isinstance(obj, list):
        return [serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize(value) for key, value in obj.items()}
    else:
        return obj

def deserialize(data: Any, cls: Type) -> Any:
    if is_dataclass(cls):
        field_types = {field.name: field.type for field in fields(cls)}
        return cls(**{
            field_name: deserialize(data.get(field_name), field_type)
            for field_name, field_type in field_types.items()
        })
    elif get_origin(cls) == list:
        item_type = get_args(cls)[0]
        return [deserialize(item, item_type) for item in data]
    elif get_origin(cls) == dict:
        key_type, value_type = get_args(cls)
        return {
            deserialize(key, key_type): deserialize(value, value_type)
            for key, value in data.items()
        }
    else:
        return data

def to_json(obj: Any) -> str:
    return json.dumps(serialize(obj))

def from_json(json_str: str, cls: Type) -> Any:
    data = json.loads(json_str)
    return deserialize(data, cls)

