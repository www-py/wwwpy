import pytest
import base64

from wwwpy.common.files import bytes_gzip, bytes_ungzip, str_gzip, str_ungzip


def test_bytes_gzip_and_ungzip():
    content = b"Binary data \x00\x01\x02"
    compressed = bytes_gzip(content)
    decompressed = bytes_ungzip(compressed)
    assert content == decompressed, "Decompressed bytes should match the original bytes"


def test_str_gzip_and_ungzip():
    content = "Hello, World!"
    compressed = str_gzip(content)
    decompressed = str_ungzip(compressed)
    assert content == decompressed, "Decompressed string should match the original string"


def test_str_gzip_returns_bytes():
    content = "Test string"
    compressed = str_gzip(content)
    assert isinstance(compressed, bytes), "str_gzip should return bytes"


def test_bytes_gzip_returns_bytes():
    content = b"Test bytes"
    compressed = bytes_gzip(content)
    assert isinstance(compressed, bytes), "bytes_gzip should return bytes"


def test_str_base64_encoding():
    content = "Base64 test string"
    compressed = str_gzip(content)
    encoded = base64.b64encode(compressed).decode('utf-8')
    # Decode and decompress
    decoded_compressed = base64.b64decode(encoded)
    decompressed = str_ungzip(decoded_compressed)
    assert content == decompressed, "Base64 encoding and decoding should preserve the string content"


def test_bytes_base64_encoding():
    content = b"Base64 test bytes \x00\xFF"
    compressed = bytes_gzip(content)
    encoded = base64.b64encode(compressed).decode('utf-8')
    # Decode and decompress
    decoded_compressed = base64.b64decode(encoded)
    decompressed = bytes_ungzip(decoded_compressed)
    assert content == decompressed, "Base64 encoding and decoding should preserve the bytes content"


def test_empty_string():
    content = ""
    compressed = str_gzip(content)
    decompressed = str_ungzip(compressed)
    assert content == decompressed, "Empty string should be handled correctly"


def test_empty_bytes():
    content = b""
    compressed = bytes_gzip(content)
    decompressed = bytes_ungzip(compressed)
    assert content == decompressed, "Empty bytes should be handled correctly"


def test_unicode_characters():
    content = "こんにちは世界"  # "Hello, World!" in Japanese
    compressed = str_gzip(content)
    decompressed = str_ungzip(compressed)
    assert content == decompressed, "Unicode characters should be handled correctly"


def test_large_string():
    content = "A" * 100000  # 100,000 characters
    compressed = str_gzip(content)
    decompressed = str_ungzip(compressed)
    assert content == decompressed, "Large strings should be handled correctly"


def test_large_bytes():
    content = b"A" * 100000  # 100,000 bytes
    compressed = bytes_gzip(content)
    decompressed = bytes_ungzip(compressed)
    assert content == decompressed, "Large bytes should be handled correctly"


def test_bytes_input_to_str_gzip_raises_error():
    with pytest.raises(AttributeError):
        str_gzip(b"Some bytes")  # Passing bytes instead of a string


def test_str_input_to_bytes_gzip_raises_error():
    with pytest.raises(TypeError):
        bytes_gzip("Some string")  # Passing string instead of bytes
