# arc_cache
Adaptive Replacement Cache - a Python3 decorator

Mostly for self-study purposes. Use at your own risk.

## Developing

TBD

## Testing

TBD

## Releasing

TBD

## Steps

1. Implement ARC in python3 as a decorator.
1. Upload to pypi.
1. Compare `arc_cache` with `functools.lru_cache`.

## References

Python 3.5 (I believe) uses a C-implementation of `lru_cache`.

- [ARC - A Self-Tuning, Low Overhead Replacement Cache (2003)][arc]
- [Adaptive Replacement Cache on Wikipedia][wikipedia]
- [`lru_cache` in cpython 3.4][functools.py]

  [arc]: http://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.13.5210
  [wikipedia]: https://en.wikipedia.org/wiki/Adaptive_replacement_cache
  [functools.py]: https://hg.python.org/cpython/file/3.4/Lib/functools.py#l384
