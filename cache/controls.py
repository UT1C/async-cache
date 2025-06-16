from typing import TYPE_CHECKING, Generic, TypeVar, ParamSpec
from collections.abc import Callable, Hashable, Awaitable, MutableMapping
import functools

from .key import SmartKey

T = TypeVar("T")
DefaultT = TypeVar("DefaultT")
P = ParamSpec("P")
KeyT = TypeVar("KeyT", bound=Hashable)
sentinel = object()


if TYPE_CHECKING:
    class CachedFunc(function, Generic[P, T]):  # noqa: F821
        def __call__(self, *args: P.args, use_cache: bool = True, **kwargs: P.kwargs) -> T:
            ...

        def cache_clear(self):
            ...


class Cached(Generic[T]):
    container: MutableMapping[SmartKey, T]
    skip_args: int

    def __init__(self, container: MutableMapping[SmartKey, T], skip_args: int = 0) -> None:
        """
        :param container: Use mappings (LRU, TTL, ...) from module
        :param skip_args: Use `1` to skip first arg of func in determining cache key
        """

        self.container = container
        self.skip_args = skip_args

    def cache_clear(self):
        """
        Clears the cache.

        This method empties the cache, removing all stored
        entries and effectively resetting the cache.

        :return: None
        """

        self.container.clear()

    def __call__(self, func: Callable[P, Awaitable[T]]) -> "CachedFunc[P, Awaitable[T]]":
        @functools.wraps(func)
        async def wrapper(*args: P.args, use_cache: bool = True, **kwargs: P.kwargs) -> T:
            if use_cache:
                value = sentinel
            else:
                key_args = args
                # preventing copy for no reason
                if self.skip_args:
                    key_args = key_args[self.skip_args:]
                key = SmartKey(key_args, kwargs)
                value = self.container.get(key, sentinel)

            if value is sentinel:
                value = await func(*args, **kwargs)
                self.container[key] = value
            return value

        wrapper.cache_clear = self.cache_clear
        return wrapper
