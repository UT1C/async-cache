from typing import Any
from collections.abc import Hashable


class SmartKey:
    args: tuple
    kwargs: dict

    def __init__(self, *args, use_cache: bool = True, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return f"<Key object by {self.args=} {self.kwargs=}>"

    def __eq__(self, obj: Any) -> bool:
        return (hash(self) == hash(obj))

    def __hash__(self) -> int:
        return hash(self._hash(self.args) + self._hash(self.kwargs))

    @classmethod
    def _hash(cls, param: Any) -> Hashable:
        match param:
            case tuple():
                return tuple(map(cls._hash, param))
            case dict():
                return tuple(map(cls._hash, param.items()))
            case _ if hasattr(param, "__dict__"):
                return str(vars(param))
            case _:
                return str(param)
