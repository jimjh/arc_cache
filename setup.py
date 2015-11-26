# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='arc_cache',
    version='0.1.1',
    description='Memoization decorator using an adaptive replacement cache.',
    long_description=long_description,
    url='https://github.com/jimjh/arc_cache',
    author='James Lim',
    author_email='jim@jimjh.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords='cache lru memoize arc',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[]
    # XXX define test deps in tox.ini
)
