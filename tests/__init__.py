import unittest

from .old.lru_test import LRUTestCase
from .old.ttl_test import TTLTestCase

cases: tuple[unittest.TestCase, ...] = (LRUTestCase, TTLTestCase)
