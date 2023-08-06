"""
List all the urls of the released packages to download in order to
install a given project.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
from itertools import chain
import sys

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from pkg_resources import Requirement
from setuptools.package_index import PackageIndex


class PkgURL(BaseSubcommand):
    """
    The ets pkgurl command.

    """

    def __init__(self, subparsers):
        """
        Constructor.

        Overloaded to customize our parser configuration.

        """

        # Create our parser.
        desc = ('List the urls of the released packages required to install '
             'a given project. At least one project must be specified. '
             'The project dependencies are found by consulting a project '
             'map. That map may be explicitly provided or generated '
             'by inspecting a set of source repositories. The list is '
             'restricted to the packages that can be discovered by '
             'setuptools, eventually using the links provided. This '
             'command can be used to generate lists of released '
             'dependencies of a project for packaging.')
        parser = subparsers.add_parser('pkgurl',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('project',
            nargs = "+",
            help = 'Specifications of project(s) to retrieve.  These are of '
                'the same form as setuptools\' version specifications.  For '
                'example "ets==2.7.0" or "ets >=2.7, <3.0a"',
            )

        # Add the options
        parser.add_argument('-f', '--find-links',
            dest = 'find_links',
            default = 'http://code.enthought.com/enstaller/eggs/source/',
            help = '''URL to search for packages.'''
            )
        self.use_project_map(parser)
        parser.add_argument('-p', '--platform',
            dest = 'platform',
            default = None,
            help = '''Name of the target platform the packages. Choices
            can be 'win32', 'macosx-10.3-fat', 'linux-i686'.'''
            )
        self.proxy(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func = self.main)

        return


    def get_urls(self, args, cfg):
        repository = PackageIndex()

        # Delete local site-packages from the repository
        repository._distmap = {}
        if args.platform:
            repository.platform = args.platform
        if args.find_links:
            repository.add_find_links([args.find_links])

        # Resolve project requirements in the released repository, and
        # not in the SVN.
        projects = []
        for project in args.project:
            distribution = repository.obtain( Requirement.parse(project))
            if distribution is None:
                print >>sys.stderr, 'Project %s not found ' % project + \
                    'for the specified platform'
            else:
                projects.append('%s == %s' % (distribution.project_name,
                    distribution.version))
        args.project = projects

        # Redirect stdout to stderr.
        sys.stdout = sys.stderr
        project_set = self.build_project_set(args, cfg)

        # Remove from the project map all the entries that are not in the
        # repository.
        pkg_list = ['%s_%s' % (pkg.project_name, pkg.version)
            for pkg in chain(*repository._distmap.values())]
        projects_mapped = project_set._project_map.keys()
        for project in projects_mapped:
            if not project in pkg_list:
                del project_set._project_map[project]

        # Add all the dependent projects.
        project_set.add_dependencies()
        sys.stdout = sys.__stdout__

        # Only persue if the user specified at least one project.
        if len(args.project) == 0:
            return set()

        # Here we use setuptools to inspect the available links.
        # We have to be careful to pass it only the requirements, and not
        # direct project names coming from the SVN's project_map.ini, as
        # this would pull in SVN verions.
        dependency_set = set()
        for project in args.project:
            dependency_set.add(project)
        for project_info in project_set._projects.itervalues():
            dependency_set.update(project_info['install_requires'])

        def get_url(requirement):
                package = repository.obtain(Requirement.parse(requirement))
                if hasattr(package, 'location'):
                    return package.location
                else:
                    return '%s: Not found' % (requirement)

        urls = (get_url(dependency) for dependency in dependency_set)
        urls = set(urls)

        return urls



    def main(self, args, cfg):
        """
        Execute the ets list eggs command.
        """

        urls = self.get_urls(args, cfg)
        print "\n".join(urls)

        return

