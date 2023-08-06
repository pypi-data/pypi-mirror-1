#!/usr/bin/env python

# setuptools plugin for pyflakes
# Author: Zooko O'Whielacronx

# Permission is hereby granted to any person obtaining a copy of this work to
# deal in this work without restriction (including the rights to use, modify,
# distribute, sublicense, and/or sell copies).

# See README.txt for instructions.

# Thanks to Ian Bicking for his buildutils plugin -- I copied liberally from
# that code to form this code.  Thanks to the authors of pyflakes and
# setuptools.

import os, re, sys

from setuptools import setup, find_packages

trove_classifiers=[
    "Framework :: Setuptools Plugin",
    "Development Status :: 5 - Production/Stable",
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

PKG='setuptools_pyflakes'
VERSIONFILE = os.path.join(PKG, "_version.py")
verstr = "unknown"
VSRE = re.compile("^verstr = ['\"]([^'\"]*)['\"]", re.M)
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    mo = VSRE.search(verstrline)
    if mo:
        verstr = mo.group(1)
    else:
        print "unable to find version in %s" % (VERSIONFILE,)
        raise RuntimeError("If %s.py exists, it is required to be well-formed." % (VERSIONFILE,))

setup_requires = []

# darcsver is needed only if you want "./setup.py darcsver" to write a new
# version stamp in pycryptopp/_version.py, with a version number derived from
# darcs history.  http://pypi.python.org/pypi/darcsver
if "darcsver" in sys.argv[1:]:
    setup_requires.append('darcsver >= 1.0.0')

long_description="""
.. _flakes:

``flakes`` -- Find Lint
-----------------------

From the pyflakes_ project page:

    Pyflakes is a simple program which checks Python source files for
    errors. It is similar to PyChecker in scope, but differs in that it
    does not execute the modules to check them. This is both safer and
    faster, although it does not perform as many checks. Unlike PyLint,
    Pyflakes checks only for logical errors in programs; it does not
    perform any checks on style.

Synopsis
~~~~~~~~

Running the ``flakes`` command on the ``pycryptopp`` project::

HACK wonwin-mcbrootles-computer:~/playground/pycryptopp/pycryptopp$ ./setup.py flakes
running flakes
pycryptopp/test/test_aes.py:3: 'cStringIO' imported but unused
pycryptopp/test/test_rsa.py:3: 'cStringIO' imported but unused
pycryptopp/test/test_rsa.py:3: 're' imported but unused
pycryptopp/test/test_rsa.py:3: 'os' imported but unused
pycryptopp/test/test_sha256.py:3: 'cStringIO' imported but unused

Options
~~~~~~~

There are no options for the ``flakes`` command.

.. _pyflakes: http://divmod.org/trac/wiki/DivmodPyflakes
"""

setup(
    name=PKG,
    version=verstr,
    description='setuptools plugin for pyflakes',
    long_description=long_description,
    author="Zooko O'Whielacronx",
    author_email='zooko@zooko.com',
    url='http://allmydata.org/trac/' + PKG,
    license='BSD',
    setup_requires=setup_requires,
    install_requires=['pyflakes >= 0.3'],
    packages=find_packages(),
    include_package_data=True,
    classifiers=trove_classifiers,
    keywords='distutils setuptools setup pyflakes',
    entry_points={
        'distutils.commands': [ 'flakes = setuptools_pyflakes.setuptools_command:PyflakesCommand', ],
        },
    zip_safe=False, # I prefer unzipped for easier access.
    )
