import asyncio
import time
import unittest
from timeit import timeit

from cache import Cached, TTL


@Cached(TTL(60))
async def long_expiration_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


@Cached(TTL(5))
async def short_expiration_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


@Cached(TTL(3))
async def short_cleanup_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


@Cached(TTL(3))
async def cache_clear_fn(wait: int):
    await asyncio.sleep(wait)
    return wait


class TTLTestCase(unittest.TestCase):
    def cache_hit_test(self):
        t1 = time.time()
        asyncio.get_event_loop().run_until_complete(long_expiration_fn(4))
        t2 = time.time()
        asyncio.get_event_loop().run_until_complete(long_expiration_fn(4))
        t3 = time.time()
        t_first_exec = (t2 - t1) * 1000
        t_second_exec = (t3 - t2) * 1000
        assert (t_first_exec > 4000)
        assert (t_second_exec < 4000)

    def cache_expiration_test(self):
        t1 = time.time()
        asyncio.get_event_loop().run_until_complete(short_expiration_fn(1))
        t2 = time.time()
        asyncio.get_event_loop().run_until_complete(short_expiration_fn(1))
        t3 = time.time()
        time.sleep(5)
        t4 = time.time()
        asyncio.get_event_loop().run_until_complete(short_expiration_fn(1))
        t5 = time.time()
        t_first_exec = (t2 - t1) * 1000
        t_second_exec = (t3 - t2) * 1000
        t_third_exec = (t5 - t4) * 1000
        assert (t_first_exec > 1000)
        assert (t_second_exec < 1000)
        assert (t_third_exec > 1000)

    def test_cache_refreshing_ttl(self):
        t1 = timeit(
            "asyncio.get_event_loop().run_until_complete(short_cleanup_fn(1))",
            globals=globals(),
            number=1
        )
        t2 = timeit(
            "asyncio.get_event_loop().run_until_complete(short_cleanup_fn(1))",
            globals=globals(),
            number=1
        )
        t3 = timeit(
            "asyncio.get_event_loop().run_until_complete(short_cleanup_fn(1, use_cache=False))",
            globals=globals(),
            number=1
        )

        assert (t1 > t2)
        assert (t1 - t3 <= 0.1)

    def cache_clear_test(self):
        # print("call function. Cache miss.")
        t1 = time.time()
        asyncio.get_event_loop().run_until_complete(cache_clear_fn(1))
        t2 = time.time()
        # print("call function again. Cache hit")
        asyncio.get_event_loop().run_until_complete(cache_clear_fn(1))
        t3 = time.time()
        cache_clear_fn.cache_clear()
        # print("Call cache_clear() to clear the cache.")
        asyncio.get_event_loop().run_until_complete(cache_clear_fn(1))
        t4 = time.time()
        # print("call function third time. Cache miss)")

        assert (t2 - t1 > 1), t2 - t1  # Cache miss
        assert (t3 - t2 < 1), t3 - t2  # Cache hit
        assert (t4 - t3 > 1), t4 - t3  # Cache miss


if __name__ == "__main__":
    unittest.main()
