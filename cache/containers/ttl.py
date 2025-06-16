from typing import Generic, TypeVar
from collections.abc import Hashable
from datetime import datetime, timedelta
import asyncio

from .lru import LRU

T = TypeVar("T")
DefaultT = TypeVar("DefaultT")
KeyT = TypeVar("KeyT", bound=Hashable)
sentinel = object()


class TTL(LRU[KeyT, tuple[T, datetime]], Generic[KeyT, T]):
    ttl: timedelta

    def __init__(self, ttl: int, maxsize: int | None = None) -> None:
        """
        :param ttl: Use ttl as None for non expiring cache
        :param maxsize: Use maxsize as None for unlimited size cache
        """

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

    def _check_expired(self, key: KeyT, expires_at: datetime) -> bool:
        if expires_at <= datetime.now():
            del self[key]
            return True
        return False


class ExpandedTTL(TTL[KeyT, T], Generic[KeyT, T]):
    """ Expands ttl on get """

    def _check_expired(self, key: KeyT, expires_at: datetime) -> bool:
        result = super()._check_expired(key, expires_at)
        if not result:
            self[key] = LRU.__getitem__(self, key)  # update `expires_at`
        return result


class NativeTTL(LRU[KeyT, tuple[T, datetime]], Generic[KeyT, T]):
    """ Expires in background (without get) """

    ttl: timedelta
    _tasks: list[asyncio.Task]

    def __init__(self, ttl: int, maxsize: int | None = None) -> None:
        """
        :param ttl: Use ttl as None for non expiring cache
        :param maxsize: Use maxsize as None for unlimited size cache
        """

        super().__init__(maxsize=maxsize)
        self.ttl = timedelta(seconds=ttl)
        self._tasks = list()

    def __getitem__(self, key: KeyT) -> T:
        value = self.get(key, sentinel)
        if value is sentinel:
            raise KeyError(key)
        return value

    def __setitem__(self, key: KeyT, value: T):
        expires_at = datetime.now() + self.ttl
        if key in self:
            self._tasks.append(
                asyncio.create_task(
                    self._scheduled_cleaner(key)
                )
            )
        super().__setitem__(key, (value, expires_at))

    def __del__(self):
        for task in self._tasks:
            task.cancel()

    def get(self, key: KeyT, default: DefaultT = None) -> T | DefaultT:
        pair = super().get(key, sentinel)
        if pair is sentinel:
            return default
        return pair[0]

    async def _scheduled_cleaner(self, key: KeyT):
        while True:
            pair = super().get(key, sentinel)
            if pair is sentinel:
                break
            expires_at = pair[1]
            now = datetime.now()
            if expires_at <= now:
                del self[key]
                break
            await asyncio.sleep((expires_at - now).total_seconds())

        self._tasks.remove(asyncio.current_task())


class ExpandedNativeTTL(NativeTTL[KeyT, T], Generic[KeyT, T]):
    """ Expands ttl on get """

    def get(self, key: KeyT, default: DefaultT = None) -> T | DefaultT:
        value = super().get(key, sentinel)
        if value is sentinel:
            return default
        self[key] = value
        return value
