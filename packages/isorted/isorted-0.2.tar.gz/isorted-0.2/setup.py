#!/usr/bin/env python

# Copyright (c) 2009 Douglas Soares de Andrade.
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.

from distutils.core import setup

setup(name='isorted',
      version='0.2',
      author="Douglas Soares de Andrade",
      author_email="contato@douglasandrade.com",
      url="http://douglasandrade.com",
      download_url="http://pypi.python.org/pypi/isorted",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      py_modules=['isorted'],
      platforms=["Any"],
      license="GPL v 3",
      keywords=["sorted", "ordered", "dict", "data structure", "key", "locale"],
      description="Sorts objects/dictionaries by keys/attributes",
      long_description="""
Sorts a list of dictionaries/objects by key/attribute taking user locale
in consideration.
        
It has been tested in django systems and also in some python libraries
that deal with accents and special characters, as python sorted/sort
methods does not deal with this kind of data.
"""
      )
