import asyncio
import time
from timeit import timeit
import unittest

from cache import Cached, LRU, TTL


@Cached(LRU(128))
async def func(wait: int):
    await asyncio.sleep(wait)


@Cached(LRU(128))
async def cache_clear_fn(wait: int):
    await asyncio.sleep(wait)


class TestClassFunc:
    @Cached(LRU(maxsize=128))
    async def obj_func(self, wait: int):
        await asyncio.sleep(wait)

    @staticmethod
    @Cached(TTL(120, maxsize=128), skip_args=1)
    async def skip_arg_func(arg: int, wait: int):
        await asyncio.sleep(wait)

    @classmethod
    @Cached(LRU(maxsize=128))
    async def class_func(cls, wait: int):
        await asyncio.sleep(wait)


class LRUTestCase(unittest.TestCase):
    def test(self):
        t1 = time.time()
        asyncio.get_event_loop().run_until_complete(func(4))
        t2 = time.time()
        asyncio.get_event_loop().run_until_complete(func(4))
        t3 = time.time()
        t_first_exec = (t2 - t1) * 1000
        t_second_exec = (t3 - t2) * 1000
        assert (t_first_exec > 4000)
        assert (t_second_exec < 4000)

    def test_obj_fn(self):
        t1 = time.time()
        obj = TestClassFunc()
        asyncio.get_event_loop().run_until_complete(obj.obj_func(4))
        t2 = time.time()
        asyncio.get_event_loop().run_until_complete(obj.obj_func(4))
        t3 = time.time()
        t_first_exec = (t2 - t1) * 1000
        t_second_exec = (t3 - t2) * 1000
        assert (t_first_exec > 4000)
        assert (t_second_exec < 4000)

    def test_class_fn(self):
        t1 = time.time()
        asyncio.get_event_loop().run_until_complete(TestClassFunc.class_func(4))
        t2 = time.time()
        asyncio.get_event_loop().run_until_complete(TestClassFunc.class_func(4))
        t3 = time.time()
        t_first_exec = (t2 - t1) * 1000
        t_second_exec = (t3 - t2) * 1000
        assert (t_first_exec > 4000)
        assert (t_second_exec < 4000)

    def test_skip_args(self):
        t1 = time.time()
        asyncio.get_event_loop().run_until_complete(TestClassFunc.skip_arg_func(5, 4))
        t2 = time.time()
        asyncio.get_event_loop().run_until_complete(TestClassFunc.skip_arg_func(6, 4))
        t3 = time.time()
        t_first_exec = (t2 - t1) * 1000
        t_second_exec = (t3 - t2) * 1000
        assert (t_first_exec > 4000)
        assert (t_second_exec < 4000)

    def test_cache_refreshing_lru(self):
        t1 = timeit(
            "asyncio.get_event_loop().run_until_complete(TestClassFunc().obj_func(1))",
            globals=globals(),
            number=1,
        )
        t2 = timeit(
            "asyncio.get_event_loop().run_until_complete(TestClassFunc().obj_func(1))",
            globals=globals(),
            number=1,
        )
        t3 = timeit(
            "asyncio.get_event_loop().run_until_complete(TestClassFunc().obj_func(1, use_cache=False))",
            globals=globals(),
            number=1,
        )

        assert (t1 > t2)
        assert (t1 - t3 <= 0.1)

    def test_cache_clear(self):
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
