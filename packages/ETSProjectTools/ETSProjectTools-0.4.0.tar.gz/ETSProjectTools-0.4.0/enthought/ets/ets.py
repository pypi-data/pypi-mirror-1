"""
Checkout the sources corresponding to the projects a specified egg or enthought
project depends on.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import ConfigParser
import os
import stat
import sys

# Project library imports
from enthought.ets import argparse
from enthought.ets.bdist import BDist
from enthought.ets.checkout import Checkout
from enthought.ets.clean import Clean
from enthought.ets.depends import Depends
from enthought.ets.develop import Develop
from enthought.ets.graph import Graph
from enthought.ets.map import Map
from enthought.ets.pkg_url import PkgURL
from enthought.ets.revert import Revert
from enthought.ets.status import Status
from enthought.ets.test import Test
from enthought.ets.update import Update


# Constants
CONFIG_FILE_DEFAULT = os.path.join(os.path.expanduser("~"), '.ets.cfg')
ENTHOUGHT_SVN_REPO = 'https://svn.enthought.com/svn/enthought'


def default_config():
    """
    Initialize the default config object. Useful for testing.
    """

    cp = ConfigParser.SafeConfigParser()

    # Add in an entry for the enthought repo.
    section = 'svn repo'
    cp.add_section(section)
    cp.set(section, '1', ENTHOUGHT_SVN_REPO)
    return cp


def init_config(filepath):
    """
    Initialize the config file at the specified path.

    """

    cp = default_config()

    # Save the configuration file for next time.
    try:
        fp = open(filepath, 'w')
        cp.write(fp)
        fp.close()
        os.chmod(filepath, stat.S_IRUSR|stat.S_IWUSR)
        print 'Created config file: %s' % filepath
    except IOError:
        pass

    return


def main(argv=None):
    """
    The main entry point for all "ets" commands

    """

    # Allow explicit calls to specify arguments to use
    if argv is None:
        argv = sys.argv[1:]

    # Setup our argument parser with any arguments all commands take
    parser = argparse.ArgumentParser(
        description = 'Tools to work with project(s), and their dependencies, '
            'as a single unit.'
        )
    parser.add_argument('-c', '--config',
        default = CONFIG_FILE_DEFAULT,
        help = 'A local configuration file.  Defaults to "%(default)s".  Use '
            'this to store authentication info, and the urls of the '
            'repositories you interact with.'
        )
    parser.add_argument('-v', '--verbose',
        action = 'store_true',
        dest = 'verbose',
        help = 'Show all output from the build commands',
        )

    # Create the parsers for the sub-commands.
    subparsers = parser.add_subparsers(
        dest = 'etscmd',
        help = 'Various sub-commands for interacting with project source.'
        )
    BDist(subparsers)
    Checkout(subparsers)
    Clean(subparsers)
    Depends(subparsers)
    Develop(subparsers)
    Graph(subparsers)
    PkgURL(subparsers)
    Map(subparsers)
    Revert(subparsers)
    Status(subparsers)
    Test(subparsers)
    Update(subparsers)

    # Process the user's request
    args = parser.parse_args(argv)
    cfg = read_config(args.config)
    args.func(args, cfg)

    return


def read_config(filepath):
    """
    Return the user's configuration.

    """

    cp = ConfigParser.SafeConfigParser()

    # If we don't have a valid file path, then do nothing else.
    if len(filepath) > 1:

        # If the specified config file doesn't exist, initialize it now.
        filepath = os.path.abspath(filepath)
        if not os.path.exists(filepath):
            init_config(filepath)

        # Read the config file.
        cp.read(filepath)

    return cp


if __name__ == '__main__':
    main()

