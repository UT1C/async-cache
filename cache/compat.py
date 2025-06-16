""" basic compatability """

from typing import TypeVar

from .controls import Cached
from .containers import LRU, TTL

T = TypeVar("T")


def AsyncLRU(maxsize: int | None = 128) -> Cached:
    """
    :param maxsize: Use maxsize as None for unlimited size cache
    """

    return Cached(LRU(maxsize=maxsize))


def AsyncTTL(
    time_to_live: int | None = 60,
    maxsize: int | None = 1024,
    skip_args: int = 0
) -> Cached:
    """
    :param time_to_live: Use time_to_live as None for non expiring cache
    :param maxsize: Use maxsize as None for unlimited size cache
    :param skip_args: Use `1` to skip first arg of func in determining cache key
    """

    if time_to_live is None:
        return Cached(LRU(maxsize=maxsize), skip_args=skip_args)
    return Cached(TTL(ttl=time_to_live, maxsize=maxsize), skip_args=skip_args)
