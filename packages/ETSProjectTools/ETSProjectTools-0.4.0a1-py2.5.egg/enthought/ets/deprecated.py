"""
Report that a command has been deprecated.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""


# Standard library imports
import os
import sys


def deprecated():
    """
    Entry point for the setuptools installed script.

    """

    full = os.path.basename(sys.argv[0])
    cmd = full[3:]
    sep = '*' * 80
    print '\n%s\nDEPRECATED!  Please use "ets %s" instead!\n%s\n' % (
        sep, cmd, sep)

    os.system('ets %s %s' % (cmd, ' '.join(sys.argv[1:])))

    return
