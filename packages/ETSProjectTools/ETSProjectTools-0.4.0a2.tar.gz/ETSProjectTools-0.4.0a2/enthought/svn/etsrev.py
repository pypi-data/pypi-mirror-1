"""
Iterate through directories to perform an svn revert on each child source tree.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import optparse
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
        description = ('Perform an svn revert against all svn checkouts '
            'within a directory.'),
        usage = '%prog [options] path [...]'
        )
    parser.add_option('-d', '--dry_run', action='store_true', default=False,
        dest='dry_run', help='do not actually run any commands -- '
        'typically used with the verbose option.')
    parser.add_option('-n', '--non-recursive', action='store_false',
        default=True, dest='recursive', help='only revert the top '
        'directory of each source tree')
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
        help='show more output about progress of this tool\'s execution')
    options, args = parser.parse_args()

    # Don't do anything if at least one path wasn't specified.
    if len(args) < 1:
        parser.print_usage()
        return

    # Create a record of the svn checkout directories under the user-specified
    # paths.
    checkouts = Checkouts(args, verbose=options.verbose)

    # Setup our command according to the user's flags.
    command = 'svn revert'
    if options.recursive:
        command += " -R"

    # Perform an svn status command against all checkouts.
    command += " %s"
    checkouts.perform(command, dry_run=options.dry_run)

    return


if __name__ == '__main__':
    main()

