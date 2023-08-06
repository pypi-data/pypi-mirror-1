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

PKG='setuptools_trial'
VERSIONFILE = os.path.join(PKG, "_version.py")
verstr = "unknown"
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    VSRE = r"^verstr = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        print "unable to find version in %s" % (VERSIONFILE,)
        raise RuntimeError("If %s.py exists, it is required to be well-formed." % (VERSIONFILE,))

# If you want to create a new _version.py file from darcs revision control history, install the
# darcsver package and run "python ./setup.py darcsver".
# http://pypi.python.org/pypi/darcsver

# If you want to produce complete distributions (such as with "sdist" or "bdist_egg") then you
# need to install setuptools_darcs (unless there is a PKG-INFO file present which shows that
# this is itself a source distribution).
# http://pypi.python.org/pypi/setuptools_darcs

data_fnames=[ 'README.txt' ]

# In case we are building for a .deb with stdeb's sdist_dsc command, we put the
# docs in "share/doc/python-$PKG".
PKG='setuptools_trial'
doc_loc = "share/doc/python-" + PKG
data_files = [(doc_loc, data_fnames)]

setup(
    name=PKG,
    version=verstr,
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
    classifiers=trove_classifiers,
    zip_safe = False,
)
