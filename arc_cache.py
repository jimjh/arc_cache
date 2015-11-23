"""Memoization decorator that caches a function's return value.

Subsequent calls of the same function with the same arguments will retrieve the
cached value, instead of re-evaluating. Adapted from the Python implementation
of ``lru_cache`` in Python 3.4.
"""

from functools import wraps, partial
from collections import OrderedDict as od


class _HashedSeq(list):
    """Wraps the given tuple and hash it exactly once."""

    __slots__ = 'hashvalue'

    def __init__(self, tup, hash=hash):
        self[:] = tup  # not sure why we waste time copying here
        self.hashvalue = hash(tup)

    def __hash__(self):
        return self.hashvalue


def _make_key(args, kwargs, typed,
              kwarg_delimiter=(object(),),
              fast_types=set([int, str, frozenset, type(None)])):
    """
    Makes a cache key from optionally typed positional and keyword arguments.

    The key is a flat list to conserve memory. If ``typed`` is ``True``, append
    type information to the end of the key.

    :param args: positional arguments
    :type args: tuple
    :param kwarg_delimiter: delimiter between args and kwargs
    :param fast_types: types that are known to cache their hash values
    :return: cache key (an object with a ``__hash__`` method)
    """

    key = args
    if kwargs:
        sorted_items = sorted(kwargs.items())
        key += kwarg_delimiter
        # does not affect original args, because these are tuples
        # cannot use #extend here
        for item in sorted_items:
            key += item
    if typed:
        key += tuple(tuple(v) for v in args)
        if kwargs:
            key += tuple(tuple(v) for k, v in sorted_items)
    elif 1 == len(key) and type(key[0]) in fast_types:
        # these types already have ``__hash__``
        return key[0]
    return _HashedSeq(key)


def _shift(src, dst):
    """Pops the first item in ``src`` and moves it to ``dst``."""
    key, value = src.popitem(last=False)
    dst[key] = value


def _pop(src):
    """Pops the first item in ``src``."""
    src.popitem(last=False)


def _delta(x, y):
    """Computes |y|/|x|."""
    return min(float(len(y))/float(len(x)), 1)


def _adapt_plus(b1, b2, max_size):
    return min(p + _delta(b1, b2), max_size)


def _adapt_minus(b1, b2, max_size):
    return max(p - _delta(b2, b1), 0)


def arc_cache(max_size=128, typed=False):
    """Decorator to memoize the given callable using an adaptive replacement cache.

    TODO docs
    TODO worry about thread-safety
    TODO tests
    """

    if not isinstance(max_size, int):
        raise TypeError('max_size must be of type int.')

    if max_size is None or 0 >= max_size:
        raise ValueError('max_size must be a positive integer. If you want an'
                         ' unbounded cache, use functools.lru_cache.')

    def decorating_function(func):

        # one instance of each var per decorated function
        # in LRU to MRU order
        t1, b1, t2, b2 = od(), od(), od(), od()
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
        adapt_minus = partial(_adapt_minus, b1, b2, max_size)

        def evict_t1_t2():
            if t1 and len(t1) > p:
                evict_t1()
            else:
                evict_t2()

        def evict_l1():  # DBL: evict from l1, slide everything back
            if b1:  # i.e. |t1| < max_size
                evict_b1()
                if t1:
                    evict_t1()
            else:
                _pop(t1)

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
                p = adapt_plus()
                # by invariant, the cache must be full, so evict from t1 or t2
                evict_t1_t2()
                t2[key] = result
            elif key in b2:  # Case III: hit in l2
                # by invariant, the cache must be full, so evict from t1 or t2
                p = adapt_minus()
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
            return {'hits': hits,
                    'misses': misses,
                    'max_size': max_size,
                    'size': len(t1) + len(t2)}

        wrapper.cache_info = cache_info
        return wrapper
    return decorating_function


@arc_cache(max_size=4)
def do_stuff(arg):
    """Does stuff."""
    print('invoked: ', arg)
