#!/usr/bin/env python
#
# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""zc.buildout recipes for setting up an Apache web server environment.
"""

import os.path
import glob

from setuptools import setup, find_packages


project_path = lambda *names: os.path.join(os.path.dirname(__file__), *names)


entry_points = {
    "zc.buildout": [
    "httpd = tl.buildout_apache.httpd:Recipe",
    "root = tl.buildout_apache.root:Recipe",
    ],
    }

longdesc = open(project_path("README.txt")).read()

data_files = [("", glob.glob(project_path("*.txt")))]

install_requires = [
    "setuptools",
    "zc.buildout",
    "gocept.cmmi",
    ]

extras_require = {
    "test": ["zope.testing"],
    }

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

setup(name="tl.buildout_apache",
      version="0.1.3",
      description=__doc__.strip(),
      long_description=longdesc,
      keywords="buildout zc.buildout recipe apache httpd server root instance",
      classifiers=classifiers,
      author="Thomas Lotze",
      author_email="thomas@thomas-lotze.de",
      url="http://www.thomas-lotze.de/en/software/buildout-recipes/",
      download_url="https://svn.thomas-lotze.de/repos/public/"
                   "buildout-recipes/apache/trunk#egg=tl.buildout_apache-dev",
      license="ZPL 2.1",
      packages=find_packages(),
      namespace_packages=["tl"],
      entry_points=entry_points,
      test_suite="tl.buildout_apache.tests.test_suite",
      install_requires=install_requires,
      extras_require=extras_require,
      include_package_data=True,
      data_files=data_files,
      zip_safe=True,
      )
