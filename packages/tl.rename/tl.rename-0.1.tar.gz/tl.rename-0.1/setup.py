#!/usr/bin/env python
#
# Copyright (c) 2007-2008 Thomas Lotze
# See also LICENSE.txt

"""A ``rename`` implementation that does more than substring replacement.
"""

import os.path
import glob
from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)

longdesc = open(project_path("README.txt")).read()

data_files = [("", glob.glob(project_path("*.txt")))]

entry_points = {
    "console_scripts": [
    "rename = tl.rename.cli:rename",
    ],
    }

install_requires = [
    "setuptools",
    "tl.cli",
    ]

tests_require = [
    "zope.testing",
    "tl.testing",
    ]

extras_require = {
    "test": tests_require,
    }

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: Zope Public License",
    "Natural Language :: English",
    "Operating System :: POSIX",
    ]

setup(name="tl.rename",
      version="0.1",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="rename files",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/tl.rename/",
      license="ZPL 2.1",
      packages=find_packages(),
      entry_points=entry_points,
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      include_package_data=True,
      data_files=data_files,
      test_suite="tl.rename.tests.test_suite",
      namespace_packages=["tl"],
      zip_safe=False,
      )
