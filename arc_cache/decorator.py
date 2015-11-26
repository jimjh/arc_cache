"""Memoization decorator that caches a function's return value.

Subsequent calls of the same function with the same arguments will retrieve the
cached value, instead of re-evaluating. Adapted from the Python implementation
of ``lru_cache`` in Python 3.4.
"""

from functools import wraps, partial, _make_key
from collections import namedtuple, OrderedDict as od

_CacheInfo = namedtuple('CacheInfo', ['hits', 'misses', 'max_size',
                                      't1_size', 't2_size', 'split'])


def _shift(src, dst):
    """Pops the first item in ``src`` and moves it to ``dst``."""
    key, value = src.popitem(last=False)
    dst.append(key)


def _pop(src):
    """Pops the first item in ``src``."""
    src.pop(0)


def _delta(x, y):
    """Computes |y|/|x|."""
    return max(float(len(y))/float(len(x)), 1.0)


def _adapt_plus(b1, b2, max_size, p):
    return min(p + _delta(b1, b2), float(max_size))


def _adapt_minus(b2, b1, p):
    return max(p - _delta(b2, b1), 0.0)


def arc_cache(max_size=128, typed=False):
    """Decorator to memoize the given callable using an adaptive replacement cache.

    :param max_size: maximum number of elements in the cache
    :type max_size: int

    ``max_size`` must be a positive integer.

    If ``typed`` is True, arguments of different types will be cached separately.
    For example, ``f(3.0)`` and ``f(3)`` will be treated as distinct calls with
    distinct results.

    Arguments to the cached function must be hashable.

    View the cache statistics named tuple
    ``(hits, misses, max_size, t1_size, t2_size, split)`` with ``f.cache_info()``.
    Reset the cache using ``f.cache_clear()``.

    TODO worry about thread-safety
    """

    if not isinstance(max_size, int):
        raise TypeError('max_size must be of type int.')

    if max_size is None or 0 >= max_size:
        raise ValueError('max_size must be a positive integer. If you want an'
                         ' unbounded cache, use functools.lru_cache.')

    def decorating_function(func):

        # one instance of each var per decorated function
        # in LRU to MRU order
        t1, b1, t2, b2 = od(), [], od(), []
        p = max_size / 2
        hits = misses = 0

        # == invariants ==
        # l1: elements were used only once
        # l2: elements were used at least twice
        # len(l1) ≤ c
        # len(l2) ≤ 2c
        # len(l1) + len(l2) ≤ 2c
        # t1, t2, b1, and b2 are always pairwise disjoint
        # if len(l1) + len(l2) < c, then both b1 and b2 are empty
        #   conversely, if b1/b2 is not empty, then len(l1) + len(l2) ≥ c
        # if len(l1) + len(l2) ≥ c, then len(t1) + len(t2) = c

        evict_t1 = partial(_shift, t1, b1)
        evict_t2 = partial(_shift, t2, b2)
        evict_b1 = partial(_pop, b1)
        evict_b2 = partial(_pop, b2)
        adapt_plus = partial(_adapt_plus, b1, b2, max_size)
        adapt_minus = partial(_adapt_minus, b2, b1)

        def evict_t1_t2():
            if t1 and len(t1) > p:
                evict_t1()
            else:
                evict_t2()

        def evict_l1():  # DBL: evict from l1, slide everything back
            if b1:  # i.e. |t1| < max_size
                evict_b1()
                evict_t1_t2()
            else:
                t1.popitem(last=False)

        def evict_l2():
            total = len(t1) + len(b1) + len(t2) + len(b2)
            if total >= max_size:
                if total == 2 * max_size:
                    # DBL: if lists are full, evict from l2
                    evict_b2()
                # ARC: if cache is full, evict from t1/t2
                evict_t1_t2()
            # else: cache is not full, don't evict from t1/t2

        @wraps(func)
        def wrapper(*args, **kwargs):

            nonlocal p, hits, misses
            key = _make_key(args, kwargs, typed)

            # ARC hit: Case I
            if key in t1:
                hits += 1
                result = t1[key]
                del t1[key]
                t2[key] = result  # MRU in t2
                return result
            elif key in t2:
                hits += 1
                t2.move_to_end(key)  # MRU in t2
                return t2[key]

            # ARC miss
            misses += 1
            result = func(*args, **kwargs)
            if key in b1:  # Case II: hit in l1
                p = adapt_plus(p)
                # by invariant, the cache must be full, so evict from t1 or t2
                evict_t1_t2()
                t2[key] = result
            elif key in b2:  # Case III: hit in l2
                # by invariant, the cache must be full, so evict from t1 or t2
                p = adapt_minus(p)
                evict_t1_t2()
                t2[key] = result
            else:  # Case IV: cache miss in DBL(2c)
                len_l1 = len(t1) + len(b1)
                if len_l1 == max_size:
                    evict_l1()
                elif len_l1 < max_size:
                    evict_l2()

                # if cache is not full, add it to t1 even if we exceed p
                t1[key] = result  # MRU in t1

            return result

        def cache_info():
            return _CacheInfo(hits, misses, max_size, len(t1), len(t2), p)

        def cache_clear():
            nonlocal hits, misses, p
            nonlocal t1, b1, t2, b2
            t1, b1, t2, b2 = od(), [], od(), []
            p = max_size / 2
            hits = misses = 0

        wrapper.cache_info = cache_info
        wrapper.cache_clear = cache_clear
        return wrapper
    return decorating_function
