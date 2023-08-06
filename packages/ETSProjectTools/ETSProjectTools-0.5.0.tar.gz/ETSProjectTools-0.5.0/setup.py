#!/usr/bin/env python
#
# Copyright (c) 2008-2009 by Enthought, Inc.
# All rights reserved.


"""
Tools for working with projects that have many dependencies.

ETSProjectTools provides commands to make it easier for developers
to work on projects that have a large number of dependencies, such as
the ETS project itself.  These commands are all predicated on a concept we
call a "checkout", which is the coherent set of projects and versions that
are required to satisfy all documented dependencies for the user-requested
project(s).

ETSProjectTools provides its tools through the 'ets' command, which has many
sub-commands.

The first set of sub-commands make it easy to create and interact with
"checkouts" and their contained projects' original source control repositories
(currently only Subversion is supported).  This is done by providing commands
like "co" (checkout), "up" (update), "st" (status), and "rev" (revert).  The
syntax and semantics of these commands are similar to most source control
systems.  You can specify which repositories the 'ets' command knows about by
editing the ".ets.cfg" file in your home directory.

The second set of 'ets' sub-commands make it easy to build, develop, or install
these projects into a Python environment.  This set includes the 'build',
'develop', and 'install' commands.  These all basically invoke the 'python
setup.py' command of the same name on all projects within the "checkout".

The last set of 'ets' sub-commands are used to explore the dependencies of
projects and enhance performance of the tool itself by generating a cache of
projects within a repository, called a map, so that each client doesn't have
to crawl a repository on its own.  These sub-commands are: depends, graph,
pkgurl, and map.


Prerequisites
-------------
You must install the following libraries before building or installing
ETSProjectTools:

 * `Subversion <http://subversion.tigris.org/>`_ 1.4. Version 1.5 can be used,
   but requires a `patch to setuptools
   <https://svn.enthought.com/enthought/wiki/PatchSetuptools_for_SVN15>`_ if
   using setuptools 0.6c8 or earlier.
 * `setuptools <http://pypi.python.org/pypi/setuptools/0.6c8>`_.

"""


import os
import zipfile

from distutils import log
from distutils.command.build import build as distbuild
from setuptools import setup, find_packages
from setuptools.command.develop import develop


# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


class MyDevelop(develop):
    def run(self):
        develop.run(self)
        self.run_command('build_docs')


class MyBuild(distbuild):
    def run(self):
        distbuild.run(self)
        self.run_command('build_docs')


# The actual setup call itself.
setup(
    author = 'Dave Peterson, et. al.',
    author_email = 'dpeterson@enthought.com',
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.split()) > 0],
    cmdclass = {
        'develop': MyDevelop,
        'build': MyBuild
    },
    description = DOCLINES[1],
    entry_points = {
        'console_scripts': [
            'ets = enthought.ets.ets:main',
            ],
        "distutils.commands": [
            'etscollect = enthought.setuptools.collector:Collector',
            'etsdeps = enthought.setuptools.validate_deps:ValidateDeps',
            ],
        },
    extras_require = INFO['extras_require'],
    include_package_data = True,
    install_requires = INFO['install_requires'],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'ETSProjectTools',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    setup_requires = 'setupdocs>=1.0',
    tests_require = [
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/ets_project_tools.php',
    version = INFO['version'],
    zip_safe = False,
    )

