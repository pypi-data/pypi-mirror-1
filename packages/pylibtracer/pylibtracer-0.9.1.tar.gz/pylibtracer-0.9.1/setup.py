#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Olli Wang (olliwang@ollix.com) on 2009-11-19.
Copyright (c) 2009 Ollix. All rights reserved.
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import pylibtracer


setup(name='pylibtracer',
      version='0.9.1',
      description='pylibtracer is a Python library used to find Python ' \
                  'modules you are using in a project.',
      license="MIT",
      author='Olli Wang',
      author_email='olliwang@ollix.com',
      url='http://opensource.ollix.com/pylibtracer',
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
          'Topic :: Utilities',
      ],
)
