"""
Iterate through directories to perform an svn update on each child source tree.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import optparse
import os
import sys

# Project imports.
from checkouts import Checkouts


def main():
    """
    Entry point for the setuptools installed script.

    """

    # Parse the user's command line.
    parser = optparse.OptionParser(
        version = '0.1',
        description = ('Perform an svn update against all svn checkouts '
            'within a directory.  If no path is explicitly specified, '
            'then the current directory is treated as the root of the '
            'checkouts to be updated.'),
        usage = '%prog [options] [path] [...]'
        )
    parser.add_option('-d', '--dry_run', action='store_true', default=False,
        dest='dry_run', help='do not actually run any commands -- '
        'typically used with the verbose option.')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
        help='show more output about progress of this tool\'s execution')
    options, args = parser.parse_args()

    # If no path was specified, use the current working directory.
    if len(args) < 1:
        args = [os.getcwd()]

    # Create a record of the svn checkout directories under the user-specified
    # paths.
    checkouts = Checkouts(args, verbose=options.verbose)

    # Perform an svn status command against all checkouts.
    command = 'svn up "%s"'
    checkouts.perform(command, dry_run=options.dry_run)

    return


if __name__ == '__main__':
    main()

