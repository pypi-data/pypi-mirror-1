"""
Checkout the sources corresponding to the projects a specified egg or enthought
project depends on.

Copyright (c) 2007-2009 by Enthought, Inc.
License: BSD Style.

"""

import ConfigParser
import os
import stat
import sys

from enthought.ets import argparse, version
from enthought.ets.bdist import BDist
from enthought.ets.checkout import Checkout
from enthought.ets.clean import Clean
from enthought.ets.depends import Depends
from enthought.ets.develop import Develop
from enthought.ets.graph import Graph
from enthought.ets.info import Info
from enthought.ets.install import Install
from enthought.ets.map import Map
from enthought.ets.pkg_url import PkgURL
from enthought.ets.revert import Revert
from enthought.ets.sdist import SDist
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
        add_help = False,
        description = '''
Tools to work with projects, and their dependencies, as a single unit.

Please note that each of the subcommands listed below (as a positional
argument) takes its own set of separate arguments, which must go AFTER
the command.  For example, to pass a custom installation prefix to the
"install" command, you should run:
    ets install -c"--prefix=/usr/local"

In order to see the valid subcommand-specific arguments, use:
    ets <command> -h

The "optional arguments" listed below are global, are specified prior
to any sub-commands as shown in the usage above, and apply to each of
the subcommands you specify.
''',
        formatter_class = argparse.RawDescriptionHelpFormatter,
        )
    parser.version = version.version
    parser.add_argument('-c', '--config',
        default = CONFIG_FILE_DEFAULT,
        help = 'A local configuration file.  Defaults to "%(default)s".  Use '
            'this to store authentication info, and the urls of the '
            'repositories you interact with.'
        )
    parser.add_argument('-h', '--help',
        action = 'help',
        default = argparse.SUPPRESS,
        help = 'show this help message and exit.  NOTE: You can also get '
            'help on subcommands by doing "%(prog)s <subcommand> -h"',
        )
    parser.add_argument('-v', '--verbose',
        action = 'store_true',
        dest = 'verbose',
        help = 'Show all output from the build commands',
        )
    parser.add_argument('--version',
        action = 'version',
        default = argparse.SUPPRESS,
        help = 'Show program\'s version number and exit',
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
    Info(subparsers)
    Install(subparsers)
    Map(subparsers)
    PkgURL(subparsers)
    Revert(subparsers)
    SDist(subparsers)
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

