#!/usr/bin/env python

from setuptools import setup
setup(name='pyncomb',
      version='1.0.0',
      description='PYthoN COMBinatorics library',
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='http://www.site.uottawa.ca/~mraap046',
      packages=['pyncomb'],
      long_description="""
          The pyncomb (PYthoN COMBinatorics) library is a collection of
          functions to work with basic combinatorial objects (e.g. permutations,
          subsets, tuples), and provides algorithms for ranking, unranking, and
          iterating over all objects in a specified class.
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
      keywords='mathematics combinatorics permutations combinations subsets',
      license='GPL'
      )

