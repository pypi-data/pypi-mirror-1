#!/usr/bin/env python
#
# Copyright (c) 2008-2009 Thomas Lotze
# See also LICENSE.txt

"""Utilities for writing tests: sandbox directories, mock external programs,
graphical doc-tests for cairo surfaces.
"""

import os.path
import glob
from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)

longdesc = "\n\n".join((open(project_path("README.txt")).read(),
                        open(project_path("ABOUT.txt")).read()))

root_files = glob.glob(project_path("*.txt"))
data_files = [("", [name for name in root_files
                    if os.path.split(name)[1] != "index.txt"])]

install_requires = [
    "setuptools",
    ]

cairo_requires = [
    'manuel>=1.0.0b2',
    #'pycairo',
    ]

tests_require = [
    "zope.testing",
    ] + cairo_requires

extras_require = {
    'cairo': cairo_requires,
    "test": tests_require,
    }

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Zope Public License",
    "Programming Language :: Python",
    "Topic :: Software Development :: Testing",
    ]

setup(name="tl.testing",
      version="0.3",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords=("testing unittest doctest file directory tree sandbox helper "
                "ls mkdir mock script manuel cairo graphics image"),
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/",
      license="ZPL 2.1",
      packages=find_packages(),
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      setup_requires=['setuptools_hg'],
      include_package_data=True,
      data_files=data_files,
      test_suite="tl.testing.tests.test_suite",
      namespace_packages=["tl"],
      zip_safe=False,
      )
