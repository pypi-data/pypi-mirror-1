"""
Display repository information for each project within a checkout.

Copyright (c) 2009 by Enthought, Inc.
License: BSD Style.

"""

import os

from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class Info(BaseSubcommand):
    """
    Display repository information for each project within a checkout.

    """

    def __init__(self, subparsers):
        desc = ('Display repository information for each project within a '
            'checkout.')
        parser = subparsers.add_parser('info',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'The checkout(s) to display repository info for.  If no '
                'path is explicitly specified, then the current directory is '
                'treated as the root of the only checkout.',
            nargs = '*',
            )

        # Add common options
        self.command_args(parser, 'info')
        self.dry_run(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Display repository information for each project.

        """

        # If no path was specified, use the current working directory.
        if args.path is None or len(args.path) < 1:
            args.path = [os.getcwd()]

        # Create a record of the project directories within the checkouts.
        checkouts = Checkouts(args.path, verbose=args.verbose)

        # Display the info. 
        command = ['svn', 'info']
        if len(args.command_args) > 0:
            command.extend(self.split_command_line_args(args.command_args))
        command.append('.')
        checkouts.perform(command, dry_run=args.dry_run, required_files=[])

        return

