"""
Iterate through directories to make each child source tree an actively deployed
project.

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
        description = ('Perform an setup.py develop against all svn checkouts '
            'within a directory.'),
        usage = '%prog [options] path [...]'
        )
    parser.add_option('-d', '--dry_run', action='store_true', default=False,
        dest='dry_run', help='do not actually run any commands -- '
        'typically used with the verbose option.')
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

    # Perform the command against all checkouts.
    command = 'cd %%s && %s setup.py develop -N' % sys.executable
    checkouts.perform(command, dry_run=options.dry_run)

    # Generate a warning if any of the checkouts are from a tag so the user
    # knows before they start making modifications that they shouldn't check
    # changes in.
    checkouts.warn_if_tag('WARNING: Some of your checkouts are from svn tags, '
        'please note that you should not check in any changes to a tag.')

    return


if __name__ == '__main__':
    main()

