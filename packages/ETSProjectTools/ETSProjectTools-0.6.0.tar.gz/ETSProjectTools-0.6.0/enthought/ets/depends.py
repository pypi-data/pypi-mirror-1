"""
Displays a dependency list for a given project..

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""


# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand


class Depends(BaseSubcommand):
    """
    The ets depends command.

    """

    def __init__(self, subparsers):
        """
        Constructor.

        Overloaded to customize our parser configuration.

        """

        # Create our parser.
        desc = 'Displays the list of dependencies for one or more projects.'
        parser = subparsers.add_parser('depends',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('project',
            help = 'Specifications of project(s) to retrieve.  These are of '
                'the same form as setuptools\' version specifications.  For '
                'example "ets==2.7.0" or "ets >=2.7, <3.0a"',
            nargs = "+",
            )

        # Add the options
        self.use_project_map(parser)
        self.proxy(parser)

        # Save the entry point for running this command.
        parser.set_defaults(func = self.main)

        return


    def main(self, args, cfg):
        """
        Execute the ets depends command.

        """

        # Build a project set to reflect the user's interests and add all the
        # dependent projects.
        project_set = self.build_project_set(args, cfg)
        project_set.add_dependencies()

        # Only continue if the user specified at least one project.
        if len(args.project) == 0:
            return

        # Display the dependency list to the user.
        dependencies = project_set.get_projects()
        root_name, root_version = project_set.get_root_project_info()
        print "\nDependencies for %s == %s:" % (root_name, root_version)
        print "\n".join("\t%s == %s" % (name, version) for name, version in
            dependencies)

        return


