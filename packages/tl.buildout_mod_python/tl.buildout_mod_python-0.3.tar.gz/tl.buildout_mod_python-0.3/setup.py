#!/usr/bin/env python
#
# Copyright (c) 2007-2009 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipe to build the mod_python Apache module.
"""

import os.path
import glob

from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)


entry_points = {
    "zc.buildout": [
    "default = tl.buildout_mod_python.module:Recipe",
    ],
    }

longdesc = open(project_path("README.txt")).read()

data_files = [("", glob.glob(project_path("*.txt")))]

install_requires = [
    "setuptools",
    "zc.buildout",
    "zc.recipe.egg",
    "gocept.cmmi",
    ]

classifiers = [
    "Development Status :: 7 - Inactive",
    "Environment :: Console",
    "Environment :: Plugins",
    "Framework :: Buildout",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: Zope Public License",
    "Operating System :: Unix",
    "Programming Language :: Python",
    "Topic :: Software Development :: Build Tools",
    "Topic :: System :: Software Distribution",
    ]

setup(name="tl.buildout_mod_python",
      version="0.3",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="buildout zc.buildout recipe apache modpython mod_python",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/buildout-recipes/",
      license="ZPL 2.1",
      packages=find_packages(),
      namespace_packages=["tl"],
      entry_points=entry_points,
      install_requires=install_requires,
      include_package_data=True,
      data_files=data_files,
      zip_safe=True,
      )
