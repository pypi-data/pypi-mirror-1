#!/usr/bin/env python2.5
#
# Copyright (c) 2006-2008 Thomas Lotze
# See also LICENSE.txt

"""Communicate with a mobile phone connected to your computer.
"""

import os.path
import glob
from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)

longdesc = open(project_path("README.txt")).read()

data_files = [("", glob.glob(project_path("*.txt")))]

entry_points = {
    "console_scripts": [
    "phebe = phebe.shell:shell",
    ],
    }

install_requires=[
    "tl.cli",
    ]

tests_require = [
    "zope.testing",
    ]

extras_require = {
    "test": tests_require,
    }

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "License :: OSI Approved :: Zope Public License",
    "Programming Language :: Python",
    "Topic :: Utilities",
    ]

setup(name="phebe",
      version="0.2",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="mobile phone at commands phonebook contacts sms",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/phebe/",
      license="ZPL 2.1",
      packages=find_packages(),
      entry_points=entry_points,
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      include_package_data=True,
      data_files=data_files,
      test_suite="phebe.tests.test_suite",
      )
