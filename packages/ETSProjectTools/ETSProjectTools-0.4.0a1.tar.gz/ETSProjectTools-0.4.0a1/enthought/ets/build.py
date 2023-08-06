"""
Perform a build on the projects within a checkout.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import os

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand
from enthought.ets.tools.checkouts import Checkouts


class Build(BaseSubcommand):
    """
    Perform a build on the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = (
            'Perform a build on the projects within a checkout.'
            ' If no path is explicitly specified, then the current directory '
            'is treated as the root of the checkout.')
        parser = subparsers.add_parser('build',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'A checkout to build',
            nargs = '*',
            )

        # Add common options
        parser.add_argument('-c', '--clean',
            action = 'store_true',
            dest = 'clean',
            help = 'perform a clean operation (prior to doing anything else)',
            )
        self.dry_run(parser)
        parser.add_argument('-E', '--no-eggs',
            action = 'store_false',
            default = True,
            dest = 'eggs',
            help = 'suppress the building of eggs',
            )
        parser.add_argument('-o', '--output-dir',
            default = 'dist',
            dest = 'dest',
            help = 'specify the destination directory for build output ' \
                '(defaults to %(default)s)',
            )
        parser.add_argument('-p', '--rpm',
            action = 'store_true',
            dest = 'rpm',
            help = 'build binaries in RPM format',
            )
        parser.add_argument('-r', '--release',
            action = 'store_true',
            dest = 'release',
            help = 'build release versions',
            )
        parser.add_argument('-s', '--sdist',
            action = 'store_true',
            dest = 'source',
            help = 'build source tarballs',
            )
        parser.add_argument('-t', '--test',
            action = 'store_true',
            dest = 'test',
            help = 'run tests as well as building',
            )
        parser.add_argument('-T', '--test-file',
            dest = 'test_file',
            default = 'tests.out',
            help = 'specify the file to write test output too. '
                '(defaults to %(default)s)',
            )

        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Build each project within a checkout.

        """

        print '*'*80 + '\n*** NOT YET IMPLEMENTED ***\n' + '*'*80 + '\n'

        return

