#!/usr/bin/env python
#
# Copyright (c) 2009-2010 Thomas Lotze
# See also LICENSE.txt

"""Visually crop an image under various constraints.
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
    # pygtk
    "setuptools",
    ]

tests_require = [
    "zope.testing",
    ]

extras_require = {
    "test": tests_require,
    }

classifiers = """\
    Development Status :: 3 - Alpha
    Environment :: X11 Applications
    Environment :: X11 Applications :: GTK
    Intended Audience :: End Users/Desktop
    License :: OSI Approved :: Zope Public License
    Programming Language :: Python
    Topic :: Utilities
    """.strip().splitlines()

keywords = """
    gtk visual crop image are constraints interactive aspect ratio
    """

entry_points = """\
    [console_scripts]
    gcrop = tl.gcrop.app:gcrop
    """

setup(name="tl.gcrop",
      version="0.1",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords=keywords,
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://packages.python.org/tl.gcrop/",
      license="ZPL 2.1",
      packages=find_packages(),
      install_requires=install_requires,
      extras_require=extras_require,
      tests_require=tests_require,
      include_package_data=True,
      data_files=data_files,
      test_suite="tl.gcrop.tests.test_suite",
      entry_points=entry_points,
      namespace_packages=["tl"],
      zip_safe=False,
      )
