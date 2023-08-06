# Copyright (c) 2009 by Enthought, Inc.
# All rights reserved.
#
# License: BSD Style.

"""\
Perform a source control update on the projects within a checkout.

"""

# Standard library imports
import os

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class Diff(BaseSubcommand):
    """\
    Perform a source control update on the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = ('Perform a source control diff on the projects within one '
            'or more checkouts.')
        parser = subparsers.add_parser('di',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'The checkout(s) to do source control diff on.  If no '
                'path is explicitly specified, then the current directory is '
                'treated as the root of the only checkout.',
            nargs = '*',
            )

        # Add common options
        self.command_args(parser, 'di')
        self.dry_run(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Update a checkout to the latest source in version control.

        """

        # If no path was specified, use the current working directory.
        if args.path is None or len(args.path) < 1:
            args.path = [os.getcwd()]

        # Create a record of the svn checkout directories under the
        # user-specified paths.
        checkouts = Checkouts(args.path, verbose=args.verbose)

        # Perform an svn update command against all checkouts.
        command = ['svn', 'diff']
        if len(args.command_args) > 0:
            command.extend(self.split_command_line_args(args.command_args))
        command.append('.')
        checkouts.perform(command, dry_run=args.dry_run, required_files=[])

        return
