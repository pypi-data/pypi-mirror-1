#!/usr/bin/env python
# This is a setuptools plugin that adds a 'trial' command which uses the
# trial script from Twisted to run unit tests instead of pyunit.
# The functionality of this plugin was contributed from
# the Elisa project: http://elisa.fluendo.com/.

import os, re, sys

from setuptools import find_packages, setup
from setuptools_trial.setuptools_trial import TrialTest

trove_classifiers=[
    "Development Status :: 4 - Beta",
    "License :: OSI Approved :: BSD License",
    "License :: DFSG approved",
    "Intended Audience :: Developers",
    "Operating System :: Microsoft",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Unix",
    "Operating System :: POSIX :: Linux",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows :: Windows NT/2000",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
    "Topic :: Utilities",
    "Topic :: Software Development :: Libraries",
    "Framework :: Setuptools Plugin",
    ]

setup_requires = []

# Note that the darcsver command from the darcsver plugin is needed to initialize the
# distribution's .version attribute correctly.  (It does this either by examining darcs history,
# or if that fails by reading the setuptools_trial/_version.py file).
# darcsver will also write a new version stamp in setuptools_trial/_version.py, with a version
# number derived from darcs history.
# http://pypi.python.org/pypi/darcsver
setup_requires.append('darcsver >= 1.2.0')

data_fnames=[ 'README.txt' ]

# In case we are building for a .deb with stdeb's sdist_dsc command, we put the
# docs in "share/doc/python-$PKG".
PKG='setuptools_trial'
doc_loc = "share/doc/python-" + PKG
data_files = [(doc_loc, data_fnames)]

setup(
    name=PKG,
    author = "Chris Galvan",
    author_email = "cgalvan@enthought.com",
    url='http://allmydata.org/trac/' + PKG,
    description = "Setuptools plugin that makes unit tests execute with " \
        "instead of pyunit.",
    entry_points = {
        'distutils.commands': [
            'trial = setuptools_trial.setuptools_trial:TrialTest',
        ],
    },
    install_requires = ["Twisted >= 2.4.0"],
    keywords = "distutils setuptools trial setuptools_plugin",
    license = "BSD",
    packages = find_packages(),
    include_package_data=True,
    data_files=data_files,
    setup_requires=setup_requires,
    classifiers=trove_classifiers,
    zip_safe = False,
)
