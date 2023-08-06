"""
Perform a clean operation on the projects within a checkout.

Copyright (c) 2008 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import os
import sys

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class Clean(BaseSubcommand):
    """
    Perform a clean command on the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = ('Perform a clean command on the projects within a checkout.')
        parser = subparsers.add_parser('clean',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'The checkouts to run the clean command on.  If no path is '
                'explicitly specified, then the current directory is treated '
                'as the root of the checkout.',
            nargs = '*',
            )

        # Add common options
        self.command_args(parser, 'clean')
        self.dry_run(parser)
        self.setup_args(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Clean each project within a checkout.

        """

        # If no path was specified, use the current working directory.
        if args.path is None or len(args.path) < 1:
            args.path = [os.getcwd()]

        # Create a record of the svn checkout directories under the
        # user-specified paths.
        checkouts = Checkouts(args.path, verbose=args.verbose)

        # Perform a clean operation command against all checkouts.
        command = [sys.executable, 'setup.py']
        if len(args.setup_args) > 0:
            command.extend(self.split_command_line_args(args.setup_args))
        command.extend(['clean'])
        if len(args.command_args) > 0:
            command.extend(self.split_command_line_args(args.command_args))
        checkouts.perform(command, dry_run=args.dry_run)


        return

