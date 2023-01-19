from typing import Iterator


def chunked(source: bytes, size: int) -> Iterator[bytes]:
    """
    Creates chunked bytes iterator of a given size.
    """

    for i in range(0, len(source), size):
        yield source[i:i + size]
