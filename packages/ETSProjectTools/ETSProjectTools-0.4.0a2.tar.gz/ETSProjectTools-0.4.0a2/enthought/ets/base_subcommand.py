"""
A base class for sub-command parsers.

This class should contain methods common to one or more sub-commands.  This
pattern is preferred over sub-classing of sub-commands because there is no
mechanism to order the options beyond the order they are added and we'd
prefer that options gets listed in the help message in alphabetical order.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import sys

# Project imports
from enthought.ets.tools.project_set import ProjectMapNotFound, \
    ProjectNotFound, ProjectSet
from enthought.proxy.api import setup_proxy, setup_authentication


class BaseSubcommand(object):

    def build_project_set(self, args, cfg):
        """
        Build and return a project set based on the user's request.

        """

        # Setup handling of urls in case the user uses a proxy.
        self.setup_url_handler(args, cfg)

        # Create a project database.  If the user specified a project map to
        # use, then use it instead of inspecting the repositories.
        project_set = ProjectSet(args.verbose)
        if len(args.local_map_file) < 1:
            if not hasattr(args, 'repos'):
                args.repos = []
            repos = self.merge_repos(cfg, args.repos)
            project_set.inspect_repositories(repos)
        else:
            try:
                project_set.load_project_map(args.local_map_file)
            except ProjectMapNotFound, e:
                print >>sys.stderr, 'Project map no found: %s' % ags.repos
                raise

        # Add all the user-specified projects.
        try:
            for project in args.project:
                project_set.add(project)
        except ProjectNotFound, e:
            print >>sys.stderr, "Project %s not found" % project
            raise

        return project_set


    def dry_run(self, parser):
        parser.add_argument('-d', '--dry-run',
            action = 'store_true',
            default = False,
            dest = 'dry_run',
            help = 'Do not actually check anything out',
            )

        return


    def merge_repos(self, cfg, repos):
        result = []

        # Add in repos from configuration file.
        section = 'svn repo'
        if cfg.has_section(section):
            for dummy, url in cfg.items(section):
                result.append(url)

        # Add in any explicitly specified repos.
        result.extend(repos)

        return result


    def no_deps(self, parser):
        parser.add_argument('-N', '--no-deps',
            action = 'store_true',
            default = False,
            dest = 'nodeps',
            help = 'Do not analyze the explicitly specified projects for their '
                'dependencies. Thus limiting the checked-out source to what '
                'the user explicitly requested.',
            )

        return


    def proxy(self, parser):
        parser.add_argument('--proxy',
            default = None,
            dest = 'proxy',
            help = 'Specify user:password@proxy.server:portnum to use a proxy for '
                'accessing repositories. (user, password, and portnum are '
                'optional.)  If you provide a user but not a password, you will '
                'be prompted for the password.  Note that you will also need to '
                'configure svn itself to use the proxy!',
            )

        return


    def setup_url_handler(self, args, cfg):

        # Always try to setup a proxy handler in case the user specified it
        # via environment variables.
        proxy = getattr(args, 'proxy', '')
        try:
            installed = setup_proxy(proxy)
        except ValueError, e:
            print >>sys.stderr, 'Proxy configuration error: %s' % e
            return 2

        # If proxy handling was NOT installed, then ensure we have
        # authentication handling installed for url's that we require
        # authentication.
        if not installed:
            setup_authentication(cfg)

        return


    def use_project_map(self, parser):
        parser.add_argument('-m', '--use-map',
            default = '',
            dest = 'local_map_file',
            help = 'Use the specified project map instead of inspecting any '
                'repositories.',
            )

        return


