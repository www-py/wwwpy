# Example usage
from dataclasses import dataclass

from wwwpy.common.rpc import serialization


@dataclass
class Address:
    city: str
    zip_code: int


@dataclass
class Person:
    name: str
    age: int
    address: Address


def test_ser():
    expected = Person(name='John', age=30, address=Address(city='New York', zip_code=10001))

    serialized = serialization.to_json(expected)
    deserialized = serialization.from_json(serialized, Person)

    assert deserialized == expected

def test_dc_datetime():
    from datetime import datetime
    from dataclasses import dataclass
    from wwwpy.common.rpc import serialization

    @dataclass
    class Person:
        name: str
        birthdate: datetime

    expected = Person(name='John', birthdate=datetime(2000, 1, 1))

    serialized = serialization.to_json(expected)
    deserialized = serialization.from_json(serialized, Person)

    assert deserialized == expected


def test_dc_datetime():
    from datetime import datetime

    expected = datetime(2000, 12, 31)

    serialized = serialization.to_json(expected)
    deserialized = serialization.from_json(serialized, datetime)

    assert deserialized == expected

def test_list():
    expected = [1, 2, 3]

    serialized = serialization.to_json(expected)
    deserialized = serialization.from_json(serialized, list)

    assert deserialized == expected

def test_tuple():
    expected = (1, 2, 3)

    serialized = serialization.to_json(expected)
    deserialized = serialization.from_json(serialized, tuple)

    assert deserialized == expected