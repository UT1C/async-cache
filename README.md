# async-cache
A caching solution for asyncio. Heavily changed fork of `async-cache` package.

## Installation
```
pip install utic-cache
```

## Basic Usage
```py
# LRU Cache
from cache import Cached, LRU


@Cached(LRU(maxsize=128))
async def func(*args, **kwargs):
    """
    maxsize: max number of results that are cached.
             if max limit is reached the oldest result is deleted.
    """
    pass
```
```py
# TTL Cache
from cache import Cached, TTL


@Cached(TTL(ttl=60, maxsize=1024), skip_args=1)
async def func(*args, **kwargs):
    """
    time_to_live: max time for which a cached result is valid (in seconds)
    maxsize: max number of results that are cached.
             if max limit is reached the oldest result is deleted.
    skip_args: Use `1` to skip first arg of func in determining cache key
    """
    pass

# Supports primitive as well as non-primitive function parameter.
# Currently TTL & LRU cache is supported.
```

## Advanced Usage
```py
from cache import Cached, LRU


class CustomDataClass:
    id: int
    value: int


@Cached(LRU(maxsize=128))
async def func(model: "CustomDataClass"):
    ...  # function logic

# async-cache will work even if function parameters are:
#   1. orm objects
#   2. request object
#   3. any other custom object type.


# To refresh the function result use the `use_cache=False` param in the function invocation
func(*args, use_cache=False, **kwargs)
```
