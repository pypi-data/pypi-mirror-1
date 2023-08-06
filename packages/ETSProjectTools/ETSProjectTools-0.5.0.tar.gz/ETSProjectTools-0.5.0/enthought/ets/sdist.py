"""
Package a source distribution for the projects within a checkout.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import os
import sys

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class SDist(BaseSubcommand):
    """
    Package a source distribution for the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = ('Package a source distribution for the projects within a '
            'checkout.')
        parser = subparsers.add_parser('sdist',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'The checkouts to build source distributions for.  If no '
                'path is explicitly specified, then the current directory is '
                'treated as the root of the checkout.',
            nargs = '*',
            )

        # Add options
        self.command_args(parser, 'sdist')
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
        Package a source distribution of each project within a checkout.

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
        args.dest = os.path.join(args.path[0], args.dest)
        if not args.dry_run and not os.path.exists(args.dest):
            os.makedirs(args.dest)

        # Perform the sdist command against the checkouts.
        command = [sys.executable, 'setup.py']
        if len(args.setup_args) > 0:
            command.extend(self.split_command_line_args(args.setup_args))
        if args.release:
            command.append('release')
        command.extend(['sdist', '-d', args.dest])
        if len(args.command_args) > 0:
            command.extend(self.split_command_line_args(args.command_args))
        checkouts.perform(command, dry_run=args.dry_run)


        return

