#!/usr/bin/env python

"""Poly: rapid development of embarrassingly parallelizable applications

Poly provides a framework for rapidly developing distributed
applications where the number of work units to be performed is known
in advance. It automatically handles many of the hassles of
distributed computing, such as:

* assigning work units to jobs
* reassembling one output file from the standard outputs of many jobs
* copying files between servers and execution hosts
* cleaning up temporary files on execution hosts
* job and I/O throttling to reduce load on servers

Poly currently includes drivers for running under Platform LSF and
in standalone mode, but drivers for other distributed computing
environments can be added easily.

Poly also includes applications to distribute processing directly from
the shell, with no additional programming needed.
"""

__version__ = "0.1.1"

import commands
import os
import sys

def die(msg):
    print >>sys.stderr, msg
    sys.exit(1)

doclines = __doc__.splitlines()
name, short_description = doclines[0].split(": ")
long_description = "\n".join(doclines[2:])

def min_version(*version_info):
    if sys.version_info < version_info:
        version = ".".join(version_info)
        die("%s requires Python %s or later" % (name, version))

min_version(2, 3)

from ez_setup import use_setuptools
use_setuptools()

from setuptools import Command, Extension, setup

class checkconfig(Command):
    description = "check to ensure that your configuration is correct"
    user_options = []

    def initialize_options(self): pass
    def finalize_options(self): pass

    def _check_ssh(): # staticmethod
        if os.system('ssh -o "NumberofPasswordPrompts=0" localhost true'):
            die("""
To use and test Poly, you must be able to ssh to localhost without a password.

Please set up public-key authentication and then try to install Poly again
""")

    _check_ssh = staticmethod(_check_ssh)

    def run(self):
        self._check_ssh()

url = "http://www.ebi.ac.uk/~hoffman/software/%s/" % name.lower()
download_url = "%s/%s-%s.tar.gz" % (url, name, __version__)

classifiers = ["Development Status :: 3 - Alpha",
               "Intended Audience :: Developers",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: GNU General Public License (GPL)",
               "Natural Language :: English",
               "Programming Language :: Python",
               "Topic :: System :: Distributed Computing"]

script_basenames = ['polycat', 'polyjob', 'polylocal', 'polyrcp', 'polysub',
                    'polywatch', 'polyxargs', 'polyxjob']

scripts = [os.sep.join(["scripts", script_basename])
           for script_basename in script_basenames]

setup(name=name,
      version=__version__,
      description=short_description,
      author="Michael Hoffman",
      author_email="hoffman@ebi.ac.uk",
      url=url,
      download_url=download_url,
      license="GNU GPLv2",
      platforms=["any"],
      classifiers=classifiers,
      long_description = long_description,
      package_dir = {'poly': 'lib'},
      packages = ['poly'],
      scripts = scripts,
      cmdclass = {"checkconfig": checkconfig}
      )
