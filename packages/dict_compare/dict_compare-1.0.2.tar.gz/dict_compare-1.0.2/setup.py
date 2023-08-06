# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(name='dict_compare',
      version='1.0.2',
      maintainer='Agustin Villena, Marijn Vriens',
      maintainer_email="marijn+dictcompare@metronomo.cl",
      url="http://protocultura.cl/hg/dict_compare/",
      license='BSD', 
      keywords='dictionary dict compare library testing unittest',
      description='''A dictionary comparer with decent difference reporting''',
      long_description='''dict_compare compares two python dictionaries and reports on any
differences between them. 

This can be very handy when comparing dictionary structures. Typical
use case is comparing expected and received values in a unittest.

New in 1.0.2:

 - Support for output in Diff format for dictionary differences.

''',
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Software Development :: Testing"],
      py_modules=['dict_compare'],
      )

__ALL__ = ["dict_compare", "assertNoDiff", "failIfDiff"]
