"""
Perform a build on the projects within a checkout.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import os
import sys

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class BDist(BaseSubcommand):
    """
    Perform a bdist on the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = ('Perform a bdist command on the projects within a checkout. '
            'This always builds eggs by appending "--formats egg" but you '
            'can add your own formats as well.')
        parser = subparsers.add_parser('bdist',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'The checkouts to build binary distributions for.  If no '
                'path is explicitly specified, then the current directory is '
                'treated as the root of the checkout.',
            nargs = '*',
            )

        # Add options
        self.command_args(parser, 'bdist')
        self.dry_run(parser)
        parser.add_argument('-o', '--output-dir',
            default = 'dist',
            dest = 'dest',
            help = ('specify the destination directory for the built '
                'distributions (defaults to %(default)s). If this is not an '
                'absolute path, it is treated as relative to the checkout '
                'directory'),
            )
        parser.add_argument('-r', '--release',
            action = 'store_true',
            dest = 'release',
            help = 'build release versions',
            )
        self.setup_args(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Build a binary distribution of each project within a checkout.

        """

        # If no path was specified, use the current working directory.
        if args.path is None or len(args.path) < 1:
            args.path = [os.getcwd()]

        # Create a record of the svn checkout directories under the
        # user-specified paths.
        checkouts = Checkouts(args.path, verbose=args.verbose)

        # Create the target output directory unless we're doing a dry run.
        # Note that we rely on os.path.join discarding everything before an
        # explicit absolute path.
        args.dest = os.path.abspath(os.path.join(args.path[0], args.dest))
        if not args.dry_run and not os.path.exists(args.dest):
            os.makedirs(args.dest)

        # Perform the bdist command against the checkouts.
        command = [sys.executable, 'setup.py']
        if len(args.setup_args) > 0:
            command.extend(self.split_command_line_args(args.setup_args))
        if args.release:
            command.append('release')
        command.extend(['bdist', '-d', args.dest, '--formats', 'egg'])
        if len(args.command_args) > 0:
            command.extend(self.split_command_line_args(args.command_args))
        checkouts.perform(command, dry_run=args.dry_run)

        return

