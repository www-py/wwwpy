from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional, Dict

import pytest

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


john = Person(name='John', age=30, address=Address(city='New York', zip_code=10001))


def test_ser():
    expected = john

    serialized = serialization.to_json(expected, Person)
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

    serialized = serialization.to_json(expected, Person)
    deserialized = serialization.from_json(serialized, Person)

    assert deserialized == expected


def test_datetime():
    from datetime import datetime

    expected = datetime(2000, 12, 31)

    serialized = serialization.to_json(expected, datetime)
    deserialized = serialization.from_json(serialized, datetime)

    assert deserialized == expected


def test_list():
    expected = [1, 2, 3]

    serialized = serialization.to_json(expected, List[int])
    deserialized = serialization.from_json(serialized, List[int])

    assert deserialized == expected


def test_tuple():
    expected = (1, 2.0, 'a')

    serialized = serialization.to_json(expected, Tuple[int, float, str])
    deserialized = serialization.from_json(serialized, Tuple[int, float, str])

    assert deserialized == expected


def test_wrong_type():
    with pytest.raises(Exception):
        serialization.to_json((datetime(2000, 12, 31),), datetime)  # it's a tuple
    with pytest.raises(Exception):
        serialization.to_json(john, datetime)


def test_wrong_type2():
    with pytest.raises(Exception):
        serialization.to_json(Person('bob', 42, address=datetime(2000, 12, 31)), Person)


def test_wrong_type3():
    with pytest.raises(Exception):
        serialization.to_json((1, 2.0, '3'), Tuple[int, float, int])


def test_tuple_datetime():
    expected = (datetime(2000, 12, 31),)

    serialized = serialization.to_json(expected, Tuple[datetime])
    deserialized = serialization.from_json(serialized, Tuple[datetime])

    assert deserialized == expected


def test_optional():
    expected = None

    serialized = serialization.to_json(expected, Optional[int])
    deserialized = serialization.from_json(serialized, Optional[int])

    assert deserialized == expected


def test_bytes():
    expected = b'\x80\x81\x82'

    serialized = serialization.to_json(expected, bytes)
    deserialized = serialization.from_json(serialized, bytes)

    assert deserialized == expected


def test_bytes_optional():
    expected = b'\x80\x81\x82'

    serialized = serialization.to_json(expected, Optional[bytes])
    deserialized = serialization.from_json(serialized, Optional[bytes])

    assert deserialized == expected


def test_dictionary():
    expected = {'a': 1, 'b': 2}

    serialized = serialization.to_json(expected, Dict[str, int])
    deserialized = serialization.from_json(serialized, Dict[str, int])

    assert deserialized == expected


@dataclass
class Node:
    value: int
    node: Optional['Node'] = None

def test_recursive():

    expected = Node(1, Node(2))
    serialized = serialization.to_json(expected, Node)
    deserialized = serialization.from_json(serialized, Node)

    assert deserialized == expected
