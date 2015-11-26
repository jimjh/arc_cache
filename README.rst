arc_cache
=========

Adaptive Replacement Cache - a Python3 decorator

Mostly for self-study purposes. Use at your own risk.

Usage
-----

.. code-block:: python

    from arc_cache import arc_cache

    @arc_cache()
    def my_heavy_function(arg1):
      do_stuff()

Developing
----------

Setup a virtualenv using

.. code-block:: console

    $ pip3 install tox
    $ tox -e develop
    $ . .venv/bin/activate

Testing
-------

Run all tests using

.. code-block:: console

    $ tox

Releasing
---------

.. code-block:: console

    $ python setup.py bdist sdist bdist_wheel
    $ gpg -u ... --detach-sign -a dist/...
    $ twine upload dist/*

References
----------

Python 3.5 (I believe) uses a C-implementation of `lru_cache`.

- `ARC`_ - A Self-Tuning, Low Overhead Replacement Cache (2003)
- `Adaptive Replacement Cache`_ on Wikipedia
- `lru_cache`_ in cpython 3.4

.. _`ARC`: http://citeseer.ist.psu.edu/viewdoc/summary?doi=10.1.1.13.5210
.. _`Adaptive Replacement Cache`: https://en.wikipedia.org/wiki/Adaptive_replacement_cache
.. _`lru_cache`: https://hg.python.org/cpython/file/3.4/Lib/functools.py#l384
