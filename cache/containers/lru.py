from typing import Generic, TypeVar
from collections.abc import Hashable
from collections import OrderedDict

T = TypeVar("T")
DefaultT = TypeVar("DefaultT")
KeyT = TypeVar("KeyT", bound=Hashable)
sentinel = object()


class LRU(OrderedDict[KeyT, T], Generic[KeyT, T]):
    maxsize: int | None

    def __init__(self, maxsize: int | None, *args, **kwargs) -> None:
        """
        :param maxsize: Use maxsize as None for unlimited size cache
        """

        self.maxsize = maxsize
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: KeyT) -> T:
        value = self.get(key, sentinel)
        if value is sentinel:
            raise KeyError(key)
        return value

    def __setitem__(self, key: KeyT, value: T):
        super().__setitem__(key, value)
        if self.maxsize is not None and len(self) > self.maxsize:
            oldest_key = next(iter(self))
            del self[oldest_key]

    def get(self, key: KeyT, default: DefaultT = None) -> T | DefaultT:
        value = super().get(key, sentinel)
        if value is not sentinel:
            self.move_to_end(key)
            return value
        else:
            return default
