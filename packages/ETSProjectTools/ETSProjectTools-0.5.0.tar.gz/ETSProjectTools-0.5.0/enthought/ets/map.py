"""
Interact with project maps.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import sys

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.project_set import ProjectMapNotFound, ProjectSet


class Map(BaseSubcommand):
    """
    Interact with project maps.

    """

    def __init__(self, subparsers):
        desc = (
            'Interact with project maps.  By default, this outputs a map '
            'across the known repositories.  It can also be used to '
            'write the map to a file, or output information about a local '
            'map file.'
            )
        parser = subparsers.add_parser('map',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('repository',
            default = [],
            help = 'A repository to map in addition to those documented in '
                'the config file',
            nargs = '*',
            )

        # Add common options
        parser.add_argument('-i', '--ignore-repo-map',
            action = 'store_true',
            default = False,
            dest = 'ignore_repo_map',
            help = 'Ignore any pre-built project maps in repositories and '
                'always build our own.',
            )
        self.use_project_map(parser)
        parser.add_argument('-n', '--no-display',
            action = 'store_false',
            default = True,
            dest = 'display',
            help = 'Do not display the map on stdout',
            )
        parser.add_argument('-o', '--output',
            default = None,
            dest = 'map_file',
            help = 'Write the project map to the specified file, creating the file '
                'if it does not already exist.',
            )
        self.proxy(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Build each project within a checkout.

        """

        # Setup handling of urls.
        self.setup_url_handler(args, cfg)

        # Create a project database.  If the user specified a project map to
        # use then do so instead of inspecting the repositories.
        project_set = ProjectSet(args.verbose)
        if len(args.local_map_file) < 1:
            repos = self.merge_repos(cfg, args.repository)
            project_set.inspect_repositories(repos, args.ignore_repo_map)
        else:
            try:
                project_set.load_project_map(args.local_map_file)
            except ProjectMapNotFound, e:
                print >>sys.stderr, 'ERROR: %s' % str(e)
                return 3

        # Only write a map file if the user requested it.
        if args.map_file is not None:
            project_set.save_map_file(args.map_file)

        # Only display the map if the user requested it.
        if args.display:
            project_set.print_project_map()

        return

