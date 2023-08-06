"""
Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""


# Standard library imports
import logging
import os
import subprocess


# Create a logger for this module.
logger = logging.getLogger(__name__)


# Our custom exceptions
class CheckoutException(Exception):
    pass


class Checkouts(object):

    #=========================================================================
    # 'object' interface
    #=========================================================================

    def __init__(self, dirs, verbose=False):
        """
        Constructor.

        Extended to initialize our custom attributes:
            * dirs is a list of directory paths, either absolute or relative to
              the current working directory, that contains a checkout for us to
              work on.
            * verbose is a boolean indicating whether to display progress
              information to stdout.

        """

        # Save the passed arguments
        self.parent_dirs = [os.path.abspath(d) for d in dirs]
        self.verbose = verbose

        # Initialize our internal variables
        #  _status_index tracks the indent level for our output messages.
        self._status_indent = 0

        # Initialize our list of projects by scanning the specified dirs.
        self._initialize_projects_list()

        # Generate a warning if the user's parent dirs are not checkout dirs!
        self._validate_parent_dirs()

        return


    #=========================================================================
    # 'ProjectSet' interface
    #=========================================================================

    #==== public methods =====================================================

    def perform(self, command, dry_run=True, required_files=['setup.py']):
        """
        Execute the specified commands for all known projects.

        The required_files list may be used to filter which projects the
        command is actually run on.
        """

        # Print some info and return immediately if no projects were found.
        if len(self.projects) < 1:
            self._status('No projects found in checkouts: %s' % \
                self.parent_dirs, ignore_verbose=True)

            return

        # Iterate through all projects.
        for project in self.projects:
            retcode = 0

            # Skip this project if the required files don't exist.
            skip = False
            for fpath in required_files:
                tgt = os.path.join(project, fpath)
                if not os.path.exists(tgt):
                    self._status('Ignoring project %s because %s missing' % (
                        project, fpath), ignore_verbose=True)
                    skip = True
                    break
            if skip:
                continue

            # Handle the case where the command was a string.
            if isinstance(command, str):
                cmd = command % project
                self._status(cmd, ignore_verbose=True)
                if not dry_run:
                    retcode = os.system(cmd)

            # Handle where the command was a sequence.  In this case, it
            # is assumed we're executing the command in the project dir.
            else:
                cmd = []
                for c in command:
                    if '%' in c:
                        cmd.append(c % project)
                    else:
                        cmd.append(c)
                self._status('Running "%s" within dir "%s"' % (' '.join(cmd),
                    project), ignore_verbose=True)
                if not dry_run:
                    retcode = subprocess.call(cmd, cwd=project)

            # Die if the command didn't finish succesfully.
            if 0 != retcode:
                raise RuntimeError('Unable to complete command for project: '
                    '%s' % project)

        return


    def warn_if_tag(self, warning):
        """
        Display a warning if any of the projects are from svn tags.

        """

        # Determine if any projects are tags
        tags = []
        for checkout in self.projects:
            if r'/tags/' in checkout:
                tags.append(checkout)

        # Display the message if we have projects from tags.
        if len(tags) > 0:
            self._status(warning, ignore_verbose=True)
            self._status_indent += 1
            try:
                for t in tags:
                    self._status(t, ignore_verbose=True)
            finally:
                self._status_indent -= 1




    #==== protected methods ==================================================

    def _initialize_projects_list(self):
        """
        Initialize the list of projects by scanning our set of directories.

        """

        self.projects = []

        for dir in self.parent_dirs:
            self._status('Finding projects in checkout at %s' % dir)
            self._status_indent += 1
            try:

                # Skip, with a warning, any non-existing directories.
                if not os.path.isdir(dir):
                    self._status('WARN: "%s" does not exist ' % dir + \
                        'or is not a directory.', ignore_verbose=True)
                    continue

                # Scan the sub-directories to look for those that are project
                # sources.
                for child in os.listdir(dir):
                    child = os.path.join(dir, child)

                    # The child must be a directory
                    if os.path.isdir(child):

                        # The child must contain an svn sub-dir.
                        svn = os.path.join(child, '.svn')
                        if os.path.isdir(svn):
                            
                            self.projects.append(child)
                            self._status('Identified checkout dir "%s"' % child)

            finally:
                self._status_indent -= 1

        return


    def _status(self, msg, ignore_verbose=False):
        """
        Report the specified status message using the current indent level.

        If ``ignore_verbose`` is True, then the message is printed even if
        we're not in verbose mode.

        """

        msg = '%s%s' % ('    '*self._status_indent, msg)

        if self.verbose or ignore_verbose:
            print msg

        logger.debug(msg)

        return


    def _validate_parent_dirs(self):
        """
        Warn the user if the parent dirs are not checkout dirs!

        A checkout dir is the parent of project source tree directories but
        is not itself a directory stored in a source control repository.

        """

        for dir in self.parent_dirs:

            # FIXME: This should be done in a way that makes source control
            # systems pluggable.  We shouldn't hard code the assumption we
            # only need to worry about svn.
            if os.path.exists(os.path.join(dir, '.svn')):
                msg = ('The directory "%s" is an svn checkout, not an ets '
                    'checkout!') % dir
                raise RuntimeError(msg)

        return
