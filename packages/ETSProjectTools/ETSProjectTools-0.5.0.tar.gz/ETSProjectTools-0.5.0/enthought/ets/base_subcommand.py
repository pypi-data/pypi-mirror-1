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
            except ProjectMapNotFound:
                print >>sys.stderr, 'Project map no found: %s' % args.repos
                raise

        # Add all the user-specified projects.
        try:
            for project in args.project:
                project_set.add(project)
        except ProjectNotFound:
            print >>sys.stderr, "Project %s not found" % project
            raise

        return project_set


    def command_args(self, parser, command):
        parser.add_argument('-c', '--command_args',
            default = '',
            dest = 'command_args',
            help = ('Specify extra args to be passed on to the %s command. '
                'If you have problems passing flags, try putting no space '
                'between the -c and the arguments like this: -c"-foo --bar". '
                'Likewise, you may need to avoid spaces between passed flags '
                'and their arguments like this: '
                '-c"-d/absolute/path/to/my/dir".') \
                % command,
            )

        return


    def dry_run(self, parser):
        parser.add_argument('-d', '--dry-run',
            action = 'store_true',
            default = False,
            dest = 'dry_run',
            help = 'Do not actually do anything, just print what would be done',
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


    def setup_args(self, parser):
        parser.add_argument('-s', '--setup_args',
            default = '',
            dest = 'setup_args',
            help = ('Specify extra args to be passed on to setup,py. '
                'If you have problems passing args, try putting no space '
                'between the -s and the arguments like this: -s"--prefix=~"'),
            )

        return


    def setup_url_handler(self, args, cfg):

        # Always try to setup a proxy handler in case the user specified it
        # via environment variables.
        proxy = getattr(args, 'proxy', '')
        try:
            installed = setup_proxy(proxy, cfg)
        except ValueError, e:
            print >>sys.stderr, 'Proxy configuration error: %s' % e
            return 2

        # If proxy handling was NOT installed, then ensure we have
        # authentication handling installed for url's that we require
        # authentication.
        if not installed:
            setup_authentication(cfg)

        return


    def split_command_line_args(self, args):
        """
        Return the specified args split into an array

        This tries to split intelligently by obeying double and single quotes
        for grouping purposes.

        """

        results = []

        arg = ''
        inDouble = inSingle = False
        for i in xrange(len(args)):
            c = args[i]

            # If we're in a double quoted argument, append the current
            # character to the arg being built unless it is the end of quoting.
            if inDouble:
                if c is '"':
                    inDouble = False
                    if len(arg) > 0:
                        results.append(arg)
                        arg = ''
                else:
                    arg = arg + c
                continue

            # If we're in a single quoted argument, append the current
            # character to the arg being built unless it is the end of quoting.
            if inSingle:
                if c is "'":
                    inSingle = False
                    if len(arg) > 0:
                        results.append(arg)
                        arg = ''
                else:
                    arg = arg + c
                continue

            # Start quoting if we come across a quote char.
            if c in '"\'':
                if len(arg) > 0:
                    results.append(arg)
                    arg = ''
                if c is '"':
                    inDouble = True
                else:
                    inSingle = True
                continue

            # Add the current word to the results if we've come across a space.
            if c is ' ':
                if len(arg) > 0:
                    results.append(arg)
                    arg = ''
                continue

            # Add the current character to the current argument being built
            arg = arg + c

        # Append the last argument
        if len(arg) > 0:
            results.append(arg)

        return results


    def use_project_map(self, parser):
        parser.add_argument('-m', '--use-map',
            default = '',
            dest = 'local_map_file',
            help = 'Use the specified project map instead of inspecting any '
                'repositories.',
            )

        return


