#!/usr/bin/env

import sys
if sys.version_info[0] <= 2:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, Extension
else:
    from distutils.core import setup, Extension

setup(name='blist',
      version='1.0.1',
      description='a list-like type with better asymptotic performance and similar performance on small lists',
      author='Stutzbach Enterprises, LLC',
      author_email='daniel@stutzbachenterprises.com',
      url='http://stutzbachenterprises.com/blist/',
      license = "BSD",
      keywords = "blist list b+tree btree fast copy-on-write sparse array",
      ext_modules=[Extension('blist', ['blist.c'])],
      provides = ['blist'],
      test_suite = "test_blist.test_suite",
      zip_safe = False, # zips are broken on cygwin for C extension modules
      classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: C',
            'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.0',
            'Programming Language :: Python :: 3.1',
            ],

      long_description="""
BList: a list-like type with better performance
===============================================

The BList is a type that looks, acts, and quacks like a Python list,
but has better performance for for modifying large lists.

For small lists (fewer than 128 elements), BLists and the built-in
list have very similar performance, although BLists are memory
inefficient if you need to create a larger number of small lists.

Here are some of the use cases where the BLists is dramatically faster
than the built-in list:

1. Insertion into or removal from a large list (O(log n) vs. O(n))
2. Taking large slices of large lists (O(log n) vs O(n))
3. Making shallow copies of large lists (O(1) vs. O(n))
4. Changing large slices of large lists (O(log n + log k) vs. O(n + k))
5. Multiplying a list to make a large, sparse list (O(log k) vs. O(kn))

You've probably noticed that we keep referring to "large lists".  

So you can see the performance of the BList in more detail, several
performance graphs available at the following link: http://stutzbachenterprises.com/blist/

Example usage:

>>> from blist import *
>>> x = blist([0])             # x is a BList with one element
>>> x *= 2**29                 # x is a BList with > 500 million elements
>>> x.append(5)                # append to x
>>> y = x[4:-234234]           # Take a 500 million element slice from x
>>> del x[3:1024]              # Delete a few thousand elements from x

For comparison, on most systems the built-in list just raises
MemoryError and calls it a day.
""",
            
      )
