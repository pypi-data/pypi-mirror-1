#------------------------------------------------------------------------------
# Copyright (c) 2007 by Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from egg_db_command import EggDBCommand
from egg_db import (get_egg_db, MAP_SECTION, ROOT_SECTION, save_egg_db,
    SYMBOL_SECTION)
import os


# The default name for each egg's extras mapping file.
EXTRAS_MAP = 'extras.map'

# The separator used between values when a package is in more than one egg.
SYMBOL_SEP = ', '


class Collector(EggDBCommand):

    ##########################################################################
    # Attributes
    ##########################################################################

    #### public 'Command' interface ##########################################

    description = ('Collect information about egg contents in a database for '
        'use by other setuptools commands provided by Enthought.')

    user_options = [
        ('egg-db=', 'd', 'path to the egg database file to create or update'),
        ('extras-map=', 'e', 'path to the extas-mapping file for this egg'),
        ]


    ##########################################################################
    # 'Command' Interface
    ##########################################################################

    #### public methods ######################################################

    def finalize_options(self):
        # FIXME: Can't use 'super' since distutils.Command is not a 'new' style
        # class
        EggDBCommand.finalize_options(self)

        # Set up the location of the extras mapping file.
        if self.extras_map is None:
            self.extras_map = EXTRAS_MAP
        self._status('Looking for extras map file: %s' % self.extras_map)

        return


    def initialize_options(self):
        # FIXME: Can't use 'super' since distutils.Command is not a 'new' style
        # class
        EggDBCommand.initialize_options(self)

        self.extras_map = None

        return


    def run(self):
        # Generate metadata first to ensure our information about this egg is
        # up to date.
        self.run_command("egg_info")

        # Open our egg database and update the root location, mapping file, and
        # packages for this egg. Then save the updated data.
        parser = get_egg_db(self.egg_db, verbose=self.verbose)
        self.save_mapping_file(parser)
        self.save_root(parser)
        self.save_symbols(parser)
        save_egg_db(parser, self.egg_db, verbose=self.verbose)

        return


    ##########################################################################
    # 'MapCollector' Interface
    ##########################################################################

    #### public methods ######################################################

    def save_mapping_file(self, parser):
        """
        Save the location of this egg's extras mapping file into the egg db.

        """

        # Determine the name of this component.
        egg_name = self.distribution.metadata.name

        # Find the mapping file for this component.
        if not os.path.exists(self.extras_map):
            self._error('ERROR: Extras map file not found!')
            return
        mappath = os.path.abspath(self.extras_map)

        # Save it to the egg db.
        parser.set(MAP_SECTION, egg_name, mappath)

        return


    def save_root(self, parser):
        """
        Save this egg's root location into an egg database.

        """
        # Determine the name of this component.
        egg_name = self.distribution.metadata.name

        # Determine the root path of this egg's source.
        # FIXME: For now we assume this is the current working dir.
        root = os.path.abspath(os.getcwd())

        # Save it in the db.
        parser.set(ROOT_SECTION, egg_name, root)

        return


    def save_symbols(self, parser):
        """
        Save info about this egg's symbols to the egg database.

        The symbols we're interested in are the packages and the modules.

        """

        # Iterate over all the packages in this egg.
        for p in self.distribution.packages:
            self._save_symbol(parser, p)

            # For each package, we also want to save a symbol record for the
            # modules in that package.
            base = p.replace('.', os.path.sep)
            for f in os.listdir(base):
                name, ext = os.path.splitext(f)
                if ext == '.py':
                    modname = '%s.%s' % (p, name)
                    self._save_symbol(parser, modname)

        return


    #### protected methods ###################################################

    def _save_symbol(self, parser, symbol):
        """
        Save a record of the specified symbol.

        """

        # Determine the name of this component.
        egg_name = self.distribution.metadata.name

        # Create the option for this module if it doesn't already
        # exist.
        if not parser.has_option(SYMBOL_SECTION, symbol):
            parser.set(SYMBOL_SECTION, symbol, egg_name)

        # Otherwise, insert the egg only if it's not already set
        # in the option.
        else:
            optionstr = parser.get(SYMBOL_SECTION, symbol)
            options = optionstr.split(SYMBOL_SEP)
            if egg_name not in options:
                options.append(egg_name)
                optionstr = SYMBOL_SEP.join(options)
                parser.set(SYMBOL_SECTION, symbol, optionstr)

        self._status('Added symbol: %s' % symbol)

        return


#### EOF #####################################################################

