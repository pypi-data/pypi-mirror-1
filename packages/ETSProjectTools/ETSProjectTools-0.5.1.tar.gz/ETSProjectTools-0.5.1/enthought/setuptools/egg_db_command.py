#------------------------------------------------------------------------------
# Copyright (c) 2007 by Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from egg_db import EGG_DB_FILE
from setuptools import Command
import os


class EggDBCommand(Command):

    ##########################################################################
    # Attributes
    ##########################################################################

    #### public 'Command' interface ##########################################

    boolean_options = []

    user_options = [
        ('egg-db=', 'd', 'path to the egg database file to create or update'),
        ]


    ##########################################################################
    # 'Command' Interface
    ##########################################################################

    #### public methods ######################################################

    def finalize_options(self):
        # Set up the location of the egg database file.
        if self.egg_db is None:
            self.egg_db = EGG_DB_FILE
        self.egg_db = os.path.expanduser(self.egg_db)
        self._status('Using egg database: %s' % self.egg_db)

        return


    def initialize_options (self):
        self.egg_db = None

        return


    ##########################################################################
    # 'BaseCommand' Interface
    ##########################################################################

    #### protected methods ###################################################

    def _error(self, msg, *args, **kws):
        """
        Print an error message.

        """

        # Convert our indent spacing to an actual string
        indent = kws.get('indent', 0)
        prefix = ' '*indent

        # Fill in any placeholders in the msg
        if len(args) > 0:
            msg = msg % args

        if self.verbose:
            print prefix + '*'*(78-indent)
        lines = msg.split('\n')
        print prefix + 'ERROR: %s' % lines[0]
        for line in lines[1:]:
            print prefix + ' '*4 + line
        if self.verbose:
            print prefix + '*'*(78-indent)

        return


    def _printdict(self, msg, dict, recurse=True):
        """
        Print the contents of a dictionary.

        """

        list = ['%s = %s' % (k,v) for k,v in dict.items()]
        list.sort()
        print '\n%s' % (' %s ' % msg).center(79, '=')
        print '%s' % '\n'.join(list)

        if recurse:
            children = [(k,v.__dict__) for k,v in dict.items() \
                if getattr(v, '__dict__', None) is not None]
            for k,v in children:
                printdict(k, v)

        return


    def _status(self, msg, *args, **kws):
        """
        Print a status message if we're in verbose mode.

        """

        if not self.verbose:
            return


        # Convert our indent spacing to an actual string
        indent = kws.get('indent', 0)
        prefix = ' '*indent

        # Fill in any placeholders in the msg
        if len(args) > 0:
            msg = msg % args

        # Print each line with an indent.
        lines = msg.split('\n')
        print prefix + lines[0]
        for line in lines[1:]:
            print prefix + ' '*4 + line

        return


    def _warning(self, msg, *args, **kws):
        """
        Print a warning message.

        """

        # Convert our indent spacing to an actual string
        indent = kws.get('indent', 0)
        prefix = ' '*indent

        # Fill in any placeholders in the msg
        if len(args) > 0:
            msg = msg % args

        if self.verbose:
            print prefix + '-'*(78-indent)
        lines = msg.split('\n')
        print prefix + 'WARNING: %s' % lines[0]
        for line in lines[1:]:
            print prefix + ' '*4 + line
        if self.verbose:
            print prefix + '-'*(78-indent)

        return


#### EOF #####################################################################

