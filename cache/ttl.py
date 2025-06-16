from typing import Generic, TypeVar
from collections.abc import Hashable
from datetime import datetime, timedelta

from .key import SmartKey
from .lru import LRU, AsyncLRU

T = TypeVar("T")
DefaultT = TypeVar("DefaultT")
KeyT = TypeVar("KeyT", bound=Hashable)
sentinel = object()


class TTL(LRU[KeyT, tuple[T, datetime]], Generic[KeyT, T]):
    ttl: timedelta

    def __init__(self, ttl: int, maxsize: int | None = None) -> None:
        super().__init__(maxsize=maxsize)
        self.ttl = timedelta(seconds=ttl)

    def __contains__(self, key: KeyT) -> bool:
        if not super().__contains__(key):
            return False

        expires_at = super().__getitem__(key)[1]
        return not self._check_expired(key, expires_at)

    def __getitem__(self, key: KeyT) -> T:
        value = self.get(key, sentinel)
        if value is sentinel:
            raise KeyError(key)
        return value

    def __setitem__(self, key: KeyT, value: T):
        expires_at = datetime.now() + self.ttl
        super().__setitem__(key, (value, expires_at))

    def get(self, key: KeyT, default: DefaultT = None) -> T | DefaultT:
        pair = super().get(key, sentinel)
        if pair is sentinel or self._check_expired(key, expires_at=pair[1]):
            return default
        return pair[0]

    def _check_expired(self, key: str, expires_at: datetime) -> bool:
        if expires_at <= datetime.now():
            del self[key]
            return True
        return False


class AsyncTTL(AsyncLRU[T], Generic[T]):
    skip_args: int

    def __init__(
        self,
        ttl: int | None = 60,
        maxsize: int | None = 1024,
        skip_args: int = 0
    ) -> None:
        """

        :param ttl: Use ttl as None for non expiring cache
        :param maxsize: Use maxsize as None for unlimited size cache
        :param skip_args: Use `1` to skip first arg of func in determining cache key
        """
        super().__init__(maxsize, skip_args)
        if ttl is not None:
            self.container = TTL(ttl=ttl, maxsize=maxsize)
