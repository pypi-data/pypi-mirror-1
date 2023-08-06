#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
Tools for working with projects that have many dependencies.

ETSProjectTools provides commands to make it easier for developers
to work on projects that have a large number of dependencies, such as
the ETS project itself.  These commands are all predicated on a concept we
call a "checkout", which is the coherent set of projects and versions that
are required to satisfy all documented dependencies for the user-requested
project(s).

ETSProjectTools provides the 'ets' command, which has many sub-commands.

The first set of sub-commands make it easy to create and interact with
"checkouts" and their contained projects' original source control repositories
(currently only Subversion is supported).  This is done by providing commands
like "co" (checkout), "up" (update), "st" (status), and "rev" (revert).  The
syntax and semantics of these commands are similar most source control systems.
You can specify which repositories the 'ets' command knows about by editing
the ".ets.cfg" file in your home directory.

The second set of 'ets' sub-commands make it easy to build, develop, or install
these projects into a python environment.  This set includes the 'build',
'develop', and 'install' commands.  These all basically invoke the 'python
setup.py' command of the same name on all projects within the "checkout".

The last set of 'ets' sub-commands are used to explore the dependencies of
projects and enhance performance of the tool itself by generating a cache of
projects within a repository, called a map, so that each client doesn't have
to examine the repo on its own.  These sub-commands are: depends, graph,
pkgurl, and map.

"""


from distutils import log
from distutils.command.build import build as distbuild
from make_docs import HtmlBuild
from pkg_resources import DistributionNotFound, parse_version, require, \
    VersionConflict
from setup_data import INFO
from setuptools import setup, find_packages
from setuptools.command.develop import develop
import os
import zipfile


# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Functions to build docs from sources when building this project.
def generate_docs():
    """ If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')
    source_dir = os.path.join(doc_dir, 'source')
    html_zip = os.path.join(doc_dir,  'html.zip')
    dest_dir = doc_dir

    required_sphinx_version = "0.4.1"
    sphinx_installed = False
    try:
        require("Sphinx>=%s" % required_sphinx_version)
        sphinx_installed = True
    except (DistributionNotFound, VersionConflict):
        log.warn('Sphinx install of version %s could not be verified.'
            ' Trying simple import...' % required_sphinx_version)
        try:
            import sphinx
            if parse_version(sphinx.__version__) < parse_version(
                required_sphinx_version):
                log.error("Sphinx version must be >=" + \
                    "%s." % required_sphinx_version)
            else:
                sphinx_installed = True
        except ImportError:
            log.error("Sphnix install not found.")

    if sphinx_installed:
        log.info("Generating %s documentation..." % INFO['name'])
        docsrc = source_dir
        target = dest_dir

        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': docsrc,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False
                }, [])
            del build

        except:
            log.error("The documentation generation failed.  Falling back to "
                "the zip file.")

            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, doc_dir)
    else:
        # Unzip the docs into the 'html' folder.
        log.info("Installing %s documentaion from zip file.\n" % INFO['name'])
        unzip_html_docs(html_zip, doc_dir)

def unzip_html_docs(src_path, dest_dir):
    """ Given a path to a zipfile, extract its contents to a given 'dest_dir'.
    """
    file = zipfile.ZipFile(src_path)
    for name in file.namelist():
        cur_name = os.path.join(dest_dir, name)
        if not name.endswith('/'):
            out = open(cur_name, 'wb')
            out.write(file.read(name))
            out.flush()
            out.close()
        else:
            if not os.path.exists(cur_name):
                os.mkdir(cur_name)
    file.close()

class my_develop(develop):
    def run(self):
        develop.run(self)
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        generate_docs()


# The actual setup call itself.
setup(
    author = 'Dave Peterson, et. al.',
    author_email = 'dpeterson@enthought.com',
    classifiers = [c.strip() for c in """\
        Development Status :: 3 - Alpha
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: C
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.split()) > 0],
    cmdclass = {
        'develop': my_develop,
        'build': my_build
    },
    description = DOCLINES[1],
    entry_points = {
        'console_scripts': [
            'ets = enthought.ets.ets:main',
            'etsco = enthought.ets.deprecated:deprecated',
            'etsdevelop = enthought.ets.deprecated:deprecated',
            'etsrev = enthought.ets.deprecated:deprecated',
            'etsst = enthought.ets.deprecated:deprecated',
            'etsup = enthought.ets.deprecated:deprecated',
            ],
        "distutils.commands": [
            'etscollect = enthought.setuptools.collector:Collector',
            'etsdeps = enthought.setuptools.validate_deps:ValidateDeps',
            'install_examples = enthought.setuptools.install_examples:InstallExamples',
            ],
        "distutils.setup_keywords": [
            "examples = enthought.setuptools.examples_writer:validate_examples",
            "examples_map = enthought.setuptools.examples_writer:validate_examples_map",
            "docs = enthought.setuptools.docs_writer:validate_docs",
            "docs_map = enthought.setuptools.docs_writer:validate_docs_map"
            ],
        "egg_info.writers": [
            "docs.txt = enthought.setuptools.docs_writer:docs_writer",
            "examples.txt = enthought.setuptools.examples_writer:examples_writer",
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
    packagetools_externals = [
        'configobj',
        ],
    tests_require = [
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/ets_project_tools.php',
    version = INFO['version'],
    zip_safe = False,
    )

