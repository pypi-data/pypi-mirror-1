"""
Perform a development install on the projects within a checkout.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import os
import sys

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class Develop(BaseSubcommand):
    """
    Perform a development install on the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = ('Perform a development install on the projects within a '
            'checkout.')
        parser = subparsers.add_parser('develop',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'The checkouts to install in development mode.  If no path '
                'is explicitly specified, then the current directory is '
                'treated as the root of the checkout.',
            nargs = '*',
            )

        # Add options
        self.command_args(parser, 'develop')
        self.dry_run(parser)
        self.setup_args(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Develop each project within a checkout.

        """

        # If no path was specified, use the current working directory.
        if args.path is None or len(args.path) < 1:
            args.path = [os.getcwd()]

        # Create a record of the svn checkout directories under the
        # user-specified paths.
        checkouts = Checkouts(args.path, verbose=args.verbose)

        # Perform the develop command against the checkouts.  Note that we need
        # to ensure we ignore dependencies since we can't process the projects
        # in the order of the dependencies, but at least in theory we HAVE all
        # the dependencies as checkouts.
        command = [sys.executable, 'setup.py']
        if len(args.setup_args) > 0:
            command.extend(self.split_command_line_args(args.setup_args))
        command.extend(['develop', '--no-deps'])
        if len(args.command_args) > 0:
            command.extend(self.split_command_line_args(args.command_args))
        checkouts.perform(command, dry_run=args.dry_run)

        # Generate a warning if any of the checkouts are from a tag so the user
        # knows before they start making modifications that they shouldn't check
        # changes in.
        checkouts.warn_if_tag('WARNING: Some of your checkouts are from '
            'svn tags, please note that you should not check in any changes '
            'to a tag.')

        return

