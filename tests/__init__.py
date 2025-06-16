import unittest

from .lru_test import LRUTestCase
from .ttl_test import TTLTestCase

cases: tuple[unittest.TestCase, ...] = (LRUTestCase, TTLTestCase)
