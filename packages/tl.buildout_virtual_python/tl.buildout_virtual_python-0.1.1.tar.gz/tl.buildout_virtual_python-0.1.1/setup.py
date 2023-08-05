#!/usr/bin/env python
#
# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe for creating a virtual Python installation
"""

import os.path
import glob

from setuptools import setup, find_packages


entry_points = {
    "zc.buildout": [
    "default = tl.buildout_virtual_python.base:Recipe",
    ],
    }

longdesc = open(os.path.join(os.path.dirname(__file__), "README.txt")).read()

data_files = [("", glob.glob("*.txt"))]

install_requires = [
    "setuptools",
    "zc.buildout",
    ]

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Environment :: Plugins",
    "Framework :: Buildout",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Zope Public License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Software Distribution",
    ]

setup(name="tl.buildout_virtual_python",
      version="0.1.1",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="buildout zc.buildout recipe virtual python",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/buildout-recipes/",
      download_url="https://svn.thomas-lotze.de/repos/public/"
                   "buildout-recipes/virtual-python/trunk"
                   "#egg=tl.buildout_virtual_python-dev",
      license="ZPL 2.1",
      packages=find_packages(),
      namespace_packages=["tl"],
      entry_points=entry_points,
      install_requires=install_requires,
      include_package_data=True,
      data_files=data_files,
      zip_safe=True,
      )
