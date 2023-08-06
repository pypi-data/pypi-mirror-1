#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Olli Wang (olliwang@ollix.com) on 2009-11-17.
Copyright (c) 2009 Ollix. All rights reserved.
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import oparse


setup(name='oparse',
      version=oparse.VERSION,
      description='oparse is a command line framework based on optparse.',
      license="MIT",
      author='Olli Wang',
      author_email='olliwang@ollix.com',
      url='http://opensource.ollix.com/oparse',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[],
      extras_require = {},
      entry_points="""
      # -*- Entry points: -*-
      """,
      classifiers=[
          'Intended Audience :: Developers',
          "License :: OSI Approved",
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Terminals',
      ],
)
