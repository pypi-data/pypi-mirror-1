"""
Perform a source status check on the projects within a checkout.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import os

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class Status(BaseSubcommand):
    """
    Perform a source status check on the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = (
            'Perform a source status check on the projects within a checkout.'
            ' If no path is explicitly specified, then the current directory '
            'is treated as the root of the checkout.')
        parser = subparsers.add_parser('st',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'The checkout to compare to source control',
            nargs = '*',
            )

        # Add common options
        self.dry_run(parser)

        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Build each project within a checkout.

        """

        # If no path was specified, use the current working directory.
        if args.path is None or len(args.path) < 1:
            args.path = [os.getcwd()]

        # Create a record of the svn checkout directories under the
        # user-specified paths.
        checkouts = Checkouts(args.path, verbose=args.verbose)

        # Perform an svn update command against all checkouts.
        command = 'svn st %s'
        checkouts.perform(command, dry_run=args.dry_run)

        return

