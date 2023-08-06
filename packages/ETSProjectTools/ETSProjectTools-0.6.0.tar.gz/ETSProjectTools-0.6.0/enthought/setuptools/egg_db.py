#------------------------------------------------------------------------------
# Copyright (c) 2007 by Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from ConfigParser import SafeConfigParser
import os


# The default name of the egg database file.
EGG_DB_FILE = os.path.expanduser(
    os.path.join('~', '.enthought', 'egg_db.ini')
    )

# The name of the maps section in the egg database file.
MAP_SECTION = 'maps'

# The name of the roots section in the egg database file.
ROOT_SECTION = 'roots'

# The name of the symbols section in the egg database file.
SYMBOL_SECTION = 'symbols'


def get_egg_db(path, verbose=False):
    """
    Return a parser of the egg database file.

    """

    # Initialize the parser
    parser = SafeConfigParser()
    if verbose:
        print 'Reading egg database: %s' % path
    parser.read([path])

    # Ensure the parser has the expected sections.
    for section in [MAP_SECTION, ROOT_SECTION, SYMBOL_SECTION]:
        if not parser.has_section(section):
            parser.add_section(section)
            if verbose:
                print ' '*4 + 'Created section: %s' % section

    return parser


def save_egg_db(parser, path, verbose=False):
    """
    Save the data in the specified parser to the specified egg database file.

    """

    # Write the updated config file.
    f = file(path, 'w')
    try:
        parser.write(f)
        if verbose:
            print 'Egg database updated: %s' % path
    finally:
        f.close()

    return


#### EOF ####################################################################

