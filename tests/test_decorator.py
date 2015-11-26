"""Tests for :py:mod`arc_cache.decorator`."""

from collections import OrderedDict
from unittest import TestCase

from arc_cache import decorator, arc_cache


class TestHelpers(TestCase):
    """Tests for helpers in ``decorator.py``."""

    def test_shift(self):
        # given src and dst
        src = OrderedDict()
        src['x'] = 0
        src['y'] = 1
        dst = [-2, -1]
        # when #_shift is invoked
        decorator._shift(src, dst)
        # then the LRU in src becomes MRU in dst
        self.assertEqual({'y': 1}, src)
        self.assertEqual([-2, -1, 'x'], dst)

    def test_pop(self):
        # given list
        src = [0, 1, 2]
        # when #pop is invoked
        decorator._pop(src)
        # then the LRU in src is removed
        self.assertEqual([1, 2], src)

    def test_delta_large(self):
        # given lists x and y
        x = [6, 7]
        y = [0, 1, 2, 3, 4]
        # when #_delta is invoked
        delta = decorator._delta(x, y)
        # then a float is returned
        self.assertAlmostEqual(2.5, delta)
        self.assertIsInstance(delta, float)

    def test_delta_small(self):
        # given lists x and y
        x = [6, 7]
        y = [0]
        # when #_delta is invoked
        delta = decorator._delta(x, y)
        # then a float is returned
        self.assertAlmostEqual(1.0, delta)
        self.assertIsInstance(delta, float)

    def test_adapt_plus_large(self):
        # given lists x and y
        x = [6, 7]
        y = [0, 1, 2, 3, 4]
        # when #_adapt_plus is invoked
        p = decorator._adapt_plus(x, y, 10, 0.1)
        # then a float is returned
        self.assertAlmostEqual(2.6, p)
        self.assertIsInstance(p, float)

    def test_adapt_plus_small(self):
        # given lists x and y
        x = [6, 7]
        y = [0, 1, 2, 3, 4]
        # when #_adapt_plus is invoked
        p = decorator._adapt_plus(x, y, 2, 0.1)
        # then a float is returned
        self.assertAlmostEqual(2.0, p)
        self.assertIsInstance(p, float)

    def test_adapt_minus_large(self):
        # given lists x and y
        x = [6, 7]
        y = [0, 1, 2, 3, 4]
        # when #_adapt_plus is invoked
        p = decorator._adapt_minus(x, y, 2.6)
        # then a float is returned
        self.assertAlmostEqual(0.1, p)
        self.assertIsInstance(p, float)

    def test_adapt_minus_small(self):
        # given lists x and y
        x = [6, 7]
        y = [0, 1, 2, 3, 4]
        # when #_adapt_plus is invoked
        p = decorator._adapt_minus(x, y, 1.0)
        # then a float is returned
        self.assertAlmostEqual(0.0, p)
        self.assertIsInstance(p, float)


@arc_cache(max_size=4)
def slow_function(arg0, kwarg1='foo'):
    pass


class TestCache(TestCase):
    """Tests for ``@arc_cache``."""

    def setUp(self):
        for i in range(4):
            slow_function(i)

    def tearDown(self):
        slow_function.cache_clear()

    def test_cold_cache(self):
        """populates a cold cache and count number of hits/misses"""
        info = slow_function.cache_info()
        self.assertEqual((0, 4, 4, 4, 0, 2), info)

    def test_hit_t1(self):
        """hits the same item twice to move it to t2"""
        slow_function(0)
        info = slow_function.cache_info()
        self.assertEqual((1, 4, 4, 3, 1, 2), info)

    def test_hit_t2(self):
        """hits the same item twice to move it to the MRU in t2"""
        slow_function(0)
        slow_function(0)
        info = slow_function.cache_info()
        self.assertEqual((2, 4, 4, 3, 1, 2), info)

    def test_hit_b1(self):
        """ghost hits in b1"""
        slow_function(2)  # mru in t2
        slow_function(4)  # miss in t1
        slow_function(0)  # hit in b1
        info = slow_function.cache_info()
        self.assertEqual((1, 6, 4, 3, 1, 3.0), info)

    def test_hit_b2(self):
        """ghost hits in b2"""
        slow_function(0)  # mru in t2
        slow_function(1)  # mru in t2
        slow_function(2)  # mru in t2
        slow_function(0)  # hit in b2
        info = slow_function.cache_info()
        self.assertEqual((3, 5, 4, 2, 2, 1.0), info)
