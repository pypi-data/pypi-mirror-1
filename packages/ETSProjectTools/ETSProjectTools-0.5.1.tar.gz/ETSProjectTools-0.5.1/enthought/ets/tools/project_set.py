"""
Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""


# Standard library imports
import ConfigParser
import logging
import os
from pkg_resources import Distribution, Requirement, working_set
import re
import shutil
import socket
import StringIO
import subprocess
import sys
import urllib2


# Create a logger for this module.
logger = logging.getLogger(__name__)


# Our custom exceptions
class ProjectMapNotFound(Exception):
    pass
class ProjectSetException(Exception):
    pass
class ProjectNotFound(ProjectSetException):
    pass
class ProjectParseError(ProjectSetException):
    pass
class VersionConflict(ProjectSetException):
    pass


class ProjectSet(object):

    #=========================================================================
    # 'object' interface
    #=========================================================================

    def __init__(self, verbose=False):
        """
        Constructor.

        Extended to initialize our custom attributes:
            - verbose is a boolean indicating whether to print lots of
                information about the state progress of this instance.
        """

        # Save the passed arguments
        self.verbose = verbose

        # Initialize our publicly-accessible attributes.
        #  missing is a dict whose keys are project names and whose values are
        #        error messages explaining why the project source is missing.
        self.missing = {}


        # Initialize our internal variables
        #  _root_project is the *name* of the root project
        #  _projects is a dict whose keys are project names and whose values are
        #        project info instances.
        #  _project_map is a dict whose keys are ids for projects (built from
        #        the project name and version) and the values are tuples
        #        consisting of (1) a setuptools' Distribution for the project,
        #        and (2) a dictionary of the information known about the
        #        project.
        #  _status_index tracks the indent level for our output messages.
        self._root_project = None
        self._projects = {}
        self._project_map = {}
        self._status_indent = 0

        return


    #=========================================================================
    # 'ProjectSet' interface
    #=========================================================================

    #==== public methods =====================================================

    def add(self, project, parent=None, raise_missing=True):
        """
        Add the specified project to our set of projects.

        The project specification may be either:
          - a fully specified url to a project directory in ANY svn repository.
            A project directory is one that contains a setup.py file.
          - a string that can be parsed by setuptools into a project
            specification, meaning a project name and/or version requirement.

        """

        # FIXME: Re-implement 'trunk' as getting the trunk of every known
        # project.  Not as the trunk of ETS itself.
#        if 'trunk' == project:
#            project = 'ets'
#            self._status('Interpreting "trunk" as "ets" project '
#                'specification.', ignore_verbose=True)

        # Special handling for explicit urls.
        if 'http' in project[:4]:
            self._add_project_url(project)

        # Otherwise, treat it as a setuptools requirement.
        else:
            try:
                self._add_project_requirement(project)
            except Exception, e:
                # If that did not work, raise an error to the user.
                if raise_missing:
                    raise ProjectNotFound('Unable to locate source for '
                        'project "%s" due to error: %s' % (project, str(e)))

                # Or, record the missing project and inform the user latter.
                else:
                    if parent is not None:
                        msg = '%s -- Required by parent project %s' % (e,
                            parent)
                    else:
                        msg = str(e)
                    self.missing[project] = msg

        return


    def add_dependencies(self):
        """
        Add any dependencies of the current project set.

        This method exists specifically so we can prefer the versions
        specified by the user's additions to this project set over finding the
        optimum match to some dependency in the first project.  For example, if
        the first project, let's call it 'foo', has a dependency for
        'bar >2.0, <3.0a' and the user explicitly added 'bar-2.5', then that
        dependency is met by the user addition.  If we had parsed 'foo's
        dependencies before adding 'bar' though, we might have found 'bar-2.9'
        in the repository and used that instead, and then gotten a version
        conflict when we added the user's 'bar-2.5'.

        """

        self._status('Adding dependent projects')
        self._status_indent += 1
        try:

            # Ensure we find the full set of dependencies.  We do this by
            # iterating until the process of looking up dependencies results in
            # no new projects being added to our project set.
            iteration_pass = 0
            while True:
                iteration_pass += 1
                self._status('Pass: %d' % iteration_pass)
                self._status_indent += 1
                try:

                    # Insepct every project required so far while keeping track
                    # of which ones we visit.
                    checked = {}
                    for name, info in self._projects.items():
                        checked[name] = True
                        self._status('Checking dependencies of %s' % name)
                        self._status_indent += 1
                        try:

                            # Add all the install requirements for the project.
                            for dep in info.get('install_requires', []):
                                self.add(dep, parent=name, raise_missing=False)

                            # Add all dependencies from the requested extras.
                            for extra in info.get('extras', []):
                                self._status('Processing "%s" ' % extra + \
                                    'extra for project %s' % name)
                                self._status_indent += 1
                                try:

                                    for dep in info['extras_require'][extra]:
                                        self.add(dep, parent=name,
                                            raise_missing=False)

                                finally:
                                    self._status_indent -= 1

                        finally:
                            self._status_indent -= 1

                finally:
                    self._status_indent -= 1

                if len(checked) >= len(self._projects):
                    break

        finally:
            self._status_indent -= 1

        return


    def checkout(self, dir, dry_run=True):
        """
        Checkout the source for the known projects to the specified directory.

        If the ``dry_run`` parameter is True, then no checkouts are actually
        made and instead we just output the status messages about what should
        be checked-out.

        """

        dir = os.path.abspath(dir)
        self._status('Checking out project source to directory %s' % dir)

        # Do all the necessary checkouts while tracking if we need to display
        # a warning about checkouts of svn tags.  If any checkout returns an
        # error (i.e. a non-zero error code,) stop all further checkouts.
        need_warning = False
        try:
            self._status_indent += 1

            for name, info in self._projects.items():
                if len(info.get('extras', [])) < 1:
                    prj = '%s==%s' % (name, info['version'])
                else:
                    prj = '%s%s==%s' % (name, list(info['extras']), info['version'])
                url = info['url']
                self._status('Checking out "%s" source from "%s"' % (prj, url),
                    ignore_verbose=True)

                if not dry_run:
                    version = info['version']
                    target_dir = os.path.join(dir, "%s_%s" % (name, version))
                    errcode = subprocess.call(['svn', 'co', url, target_dir])
                    if errcode != 0:
                        break

                if need_warning == False and r'/tags/' in url:
                    need_warning = True

        finally:
            self._status_indent -= 1

        # Confirm
        if not dry_run:
            self._status('\nAll project source has been checked out to '
                '"%s"' % dir, ignore_verbose=True)

        # Display the tags warning if necessary.
        if need_warning:
            self._status('\nWARNING: YOUR CHECKOUT INCLUDES PROJECTS FROM SVN '
                'TAGS -- PLEASE BE CAREFUL WHEN CHECKING IN CHANGES AS '
                'TAGS SHOULD NOT BE CHANGED!  You can svn copy a tag to a  '
                'branch, then svn switch to that, and then check in your '
                'changes for a future release.', ignore_verbose=True)

        return


    def get_projects(self):
        """
        Return a list of the projects in this project set.

        The list is actually a list of tuples where each tuple is the project
        name and version.

        """

        projects = [(p['name'], p['version']) for p in self._projects.values()]
        projects.sort()

        return projects


    def get_root_project_info(self):
        """
        Return the name and version of the root project of this project set.

        The root project is the first project added by the user.

        """

        info = self._projects[self._root_project]
        name = info['name']
        version = info['version']

        return (name, version)


    def inspect_repositories(self, repositories, ignore_repo_map=False):
        """
        Add to our project map by inspecting the specified SVN repositories.

        The repositories argument is a list of URLs as strings. Each repository
        in the list will be inspected to discover the project sources stored in
        that repository.  Unless the ignore_repo_map parameter is True,
        inspection starts by looking for a project map file stored at the root
        of the repository.  If a project map is found, then its contents are
        read and we are done inspecting that repository.  If no project map is
        found, then we will crawl the repository looking for the setup.py's
        that define project source trees.

        """

        # Iterate through the specified repositories.
        for repo in repositories:
            msg = 'Inspecting repository: %s' % repo
            if ignore_repo_map:
                msg += '  Please be patient, this may take awhile.'
            self._status(msg, ignore_verbose=True)
            self._status_indent += 1
            try:

                # Unless told not to, look for a project map file.  If
                # one is found, we use it rather than crawling the
                # repository to discover projects.
                if not ignore_repo_map:
                    map_data = self._get_repository_map_as_file(repo)
                    if map_data is not None:
                        self.load_project_map(map_data)
                        continue

                # Find and add the projects in the current repo to our project
                # map.
                try:
                    infos = self._parse_svn_dir(repo)
                except socket.gaierror:
                    raise ProjectSetException("Unable to access repository.  "
                        "Is the network down?")
                for info in infos:
                    id = '%s_%s' % (info['name'], info['version'])
                    d = Distribution(
                        location = info['url'],
                        project_name = info['name'],
                        version = info['version'],
                        )
                    self._project_map[id] = (d, info)

            finally:
                self._status_indent -= 1
                self._status('Finished repository: %s' % repo)

        return


    def load_project_map(self, map):
        """
        Merge projects from the specified project map into our own project map.

        The map parameter may be either the content of a project map or a
        filepath as a string.  Either way, the contents of the map are
        iterated over to add each project to our own project map.

        If a filepath is provided and the specified file can not be read, a
        ProjectMapNotFound exception is raised.

        """

        # If the passed value contains newlines, then assume it is the content
        # of a project map.
        if '\n' in map:
            f = StringIO.StringIO(map)
            self._load_project_map(f)

        # Otherwise, try treating the passed parameter as a path to a file.
        elif os.path.isfile(map):
            self._status('Reading local map file: %s' % map)
            self._status_indent += 1
            try:
                map = open(map)
                self._load_project_map(map)
                map.close()
            finally:
                self._status_indent -= 1

        # If none of the above worked, raise an error to report a problem.
        else:
            raise ProjectMapNotFound('The specified map file does not exist: '
                '%s' % map)

        return


    def print_project_map(self):
        """
        Prints the set of known projects to stdout.

        """

        print "\nProjects in the known repositories:"

        names = self._project_map.keys()
        names.sort()
        for name in names:
            (distrib, info) = self._project_map[name]
            id = '%s_%s' % (info['name'], info['version'])
            url = info['url']
            print '    %s\t%s' % (id.ljust(30), url)

        print "\n"

        return


    def save_map_file(self, filepath):
        """
        Write out the contents of our project map to the specified file.

        The file is created if it does not already exist, though the necessary
        directories are not created if they do not exist.

        """

        # Ensure we can write to the requested filepath.
        filepath = os.path.abspath(filepath)
        f = open(filepath, 'w')
        self._status('Saving project map to: %s' % filepath)
        self._status_indent += 1
        try:

            # Convert our project map to an ini-style database, one section per
            # project.
            cp = ConfigParser.ConfigParser()
            for id, (d, info) in self._project_map.items():
                self._status('Saving data for project: %s' % id)
                cp.add_section(id)
                for k,v in info.items():
                    if k in ['extras_require', 'install_requires', 'name',
                            'url', 'version']:
                        cp.set(id, k, str(v))

            # Write the ini-style database to our target file.
            cp.write(f)

        finally:
            self._status_indent -= 1
            f.close()

        return


    #==== protected methods ==================================================

    def _add_project_requirement(self, spec):
        """
        Add a project corresponding to the given setuptools requirement spec.

        """

        # Find all of the projects in our project map that meet the requirement
        # and sort them by version.
        r = Requirement.parse(spec)
        matches = []
        for dist, info in self._project_map.values():
            if dist in r:
                matches.append( (dist, info) )
        matches.sort()

        # Find the best match that fits our existing projects.  Note than an
        # attempt to add version different from one we've already added will
        # generate an exception.  Thus the try...except here.
        while len(matches) > 0:
            dist, info = matches[-1]
            try:
                # Create a customized verison of the project info that includes
                # the extras that were requested for this usage.
                info = info.copy()
                info['extras'] = list(r.extras)

                self._record_project(info)
                break

            except VersionConflict:
                matches.pop()
                pass

        # If we ran out of matches, raise an exception.
        if len(matches) < 1:
            raise ProjectNotFound('No match found for project specification '
                '"%s"' % spec)

        return


    def _add_project_url(self, url):
        """
        Adds the URL specified project to the current set.

        We assume the URL references the root directory of the project.  We get
        the rest of the information by retrieving the setup.py within that
        directory.

        """

        info = self._get_project_info_from_svn(url)
        self._record_project(info)

        return


    def _get_project_info_from_svn(self, url):
        """
        Return project info from the specified URL to an svn project directory.

        Returns a dictionary of the keywords passed to the setup() method when
        executing the setup.py file.  To be most efficient, we try to execute
        the setup.py without downloading the whole project.  If that attempt
        results in an exception, we try to parse the directory name to get
        the project name and version.

        Will raise an exception if the project name and version couldn't be
        determined at all.

        """

        # First, look for a simple, custom file that contains the necessary
        # data to identify the project and its dependencies.  If one is found
        # we won't have to parse the possibly more complex setup.py.
        setup_data_url = '%s/setup_data.py' % url
        try:
            setup_data = self._get_url(setup_data_url)

            try:
                scope = {'__file__':'setup_data.py', '__name__':'__main__'}
                exec setup_data in scope
                info = scope['INFO']
                self._status('Parsed setup_data.py from "%s"' % setup_data_url)
            except Exception, e:
                self._status('WARN: Unable to parse setup_data.py: %s' % str(e))
                info = None

        except Exception, e:
            info = None

        # If we haven't found project info yet, retrieve the content of the
        # setup.py
        if info is None:
            setup_url = '%s/setup.py' % url
            try:
                setup = self._get_url(setup_url)
            except Exception, e:
                raise ProjectParseError('Unable to find a setup.py for '
                    'project URL "%s".  Exception was: %s' % (setup_url,
                    str(e)))

            # Try to execute the setup.py without downloading the whole project
            # tree.
            try:
                info = self._safe_setup_execution(setup)
                self._status('Parsed setup.py from "%s"' % setup_url)
            except Exception, e:
                self._status('WARN: Unable to parse setup.py: %s' % str(e))
                info = None

        # If that didn't work, try to get as much info as possible by parsing
        # the directory name part of the URL.  This allows us to retrieve some
        # project info even for older Enthought tags where the setup.py wouldn't
        # run unless the whole source tree was available -- and we don't want
        # to download the whole thing!
        if info is None:
            try:
                root, project_spec = url.rsplit('/', 1)
                name, version = project_spec.rsplit('_', 1)
                info = {
                    'name':name,
                    'version':version,
                    'install_requires':[],
                    'extras_require':{},
                    }
                self._status('WARN: Parsed URL "%s" for project ' % url + \
                    'info. No dependencies will be included.')
            except Exception, e:
                raise ProjectParseError('Unable to parse URL "%s" ' % url + \
                    'for project info due to error: %s' % str(e))

# FIXME: Should the below be a fallback choice?  i.e. a 3rd option?
#        # That didn't work, so let's it again once we have a copy of the whole
#        # source tree.
#        except Exception, e:
#            self._status_indent += 1
#            self._status('Unable to parse setup.py without whole source tree.')
#            try:
#
#                # Make a local copy of the source tree
#                local_dir = self._tmp_copy_of_svn_dir(url)
#                try:
#
#                    # Temporarily change to our temp directory
#                    cwd = os.getcwd()
#                    os.chdir(local_dir)
#                    try:
#                        info = self._safe_setup_execution(setup)
#                    finally:
#                        os.chdir(cwd)
#
#                # Ensure we clean up our temp directory.
#                # FIXME: We should probably keep these temp directories around
#                # until we know we won't be using them in the final checkout --
#                # actually, in that case, we'd have to change to doing an svn
#                # checkout instead of our web copy.  svn would be faster
#                # anyway.
#                finally:
#                    pass
##                    self._status('Removing temp directory "%s"' % local_dir)
##                    shutil.rmtree(local_dir)

        # Create the project info dictionary
        info['url'] = url

        # Safety check.  If we don't have at least a url, name, and version
        # then this info is not valid and should be discarded.
        for key in ['url', 'name', 'version']:
            if key not in info:
                raise ProjectParseError('Discarding incomplete project '
                    'specification due to missing data: %s' % key)

        return info


    def _get_repository_map_as_file(self, url):
        """
        Return the contents of the project map in the specified repository.

        We look for the project map only in the root directory of the
        repository, and only by a specific name.  If the repository contains
        no project map, then None is returned.

        """

        # The name of the project map file to look for.
        MAP_FILENAME = 'project_map.ini'

        # Try reading the contents of the map file.
        map_url = '%s/%s' % (url, MAP_FILENAME)
        try:
            map_data = self._get_url(map_url)
            self._status('Found project map at: %s' % map_url)
        except Exception, e:
            map_data = None
            self._status('No project_map.ini found. %s' % str(e))

        return map_data


    def _get_url(self, url):
        """
        Return the content retrieved from the specified url.

        Raises an ProjectSetException if there is any problem accessing the
        url due to authentication.  Other errors cause exceptions from urllib2
        to propagate.

        """

        try:
            f = urllib2.urlopen(url)
            result = f.read()
            f.close()
        except Exception, e:
            if isinstance(Exception, IOError) and  hasattr(e, 'code'):
                if e.code == 401:
                    msg = ('Authorization error while accessing "%s" which '
                        'has header: "%s"')
                    msg = msg % (url, e.headers['www-authenticate'])
                    raise ProjectSetException(msg)
                else:
                    raise
            else:
                raise
        return result


    def _load_project_map(self, file):
        """
        Merge projects from the specified map file into our own project map.

        The content of the file is expected to be in ini-style format, where
        each section identifies a project, and the sections options contain the
        information about the project.

        """

        # Iterate through all the projects in the file.
        cp = ConfigParser.ConfigParser()
        cp.readfp(file)
        for id in cp.sections():
            self._status('Processing map project; %s' % id)
            self._status_indent += 1
            try:

                # Read all the options and store them in a project info
                # dictionary.
                info = {}
                for key in cp.options(id):
                    value = cp.get(id, key)
                    self._status('Processing "%s" = "%s"' % (key,
                        value))
                    try:
                        value = eval(value)
                    except:
                        pass
                    info[key] = value

                # Rebuild the setuptools' Distribution object.
                d = Distribution(
                    location = info['url'],
                    project_name = info['name'],
                    version = str(info['version']),
                    )

                # Store the project info in our map.
                self._project_map[id] = (d, info)

            finally:
                self._status_indent -= 1

        return


    def _parse_svn_dir(self, url):
        """
        Return info for project directories at the specified svn url.

        This may raise exceptions (ProjectSetException or anything coming out
        of urllib2) is there are problems accessing the url.

        """

        project_infos = []

        # Retrieve the svn content for the url.
        svn_content = self._get_url(url)
        self._status('Parsing svn dir: %s' % url)

        # If there is a setup.py link in the content, treat the URL as the root
        # directory of a project and ignore the rest of the directory structure.
        pattern = r'<li><a href="setup.py">setup.py</a></li>'
        if pattern in svn_content:
            self._status_indent += 1
            try:
                info = self._get_project_info_from_svn(url)
                project_infos.append(info)
                self._status('Identified project "%s" ' % info['name'] + \
                    'version "%s"' % info['version'])
            except Exception, e:
                if '404' not in str(e):
                    self._status('ERROR: Unable to get project info due '
                        'to error: %s' % str(e))
            self._status_indent -= 1
            return project_infos

        # Otherwise, exameine all of the child directories to see if any of
        # them are project roots.
        pattern = r'<li><a href="(.*)/">'
        for link in re.findall(pattern, svn_content):
            link_url = '%s/%s' % (url, link)

            # Skip any '.' or '..' directories
            if link == '.' or link == '..':
                continue

            # Recurse in the event of special case directories.
            if link in ['trunk', 'branches', 'tags']:
                try:
                    self._status_indent += 1
                    project_infos.extend(self._parse_svn_dir(link_url))
                    continue
                finally:
                    self._status_indent -= 1

            # Recurse if there exists a child directory of the current link
            # called 'trunk' which contains a setup.py file -- these links ARE
            # project root directories.
            try:
                self._status_indent += 1
                try:
                    test_url = '%s/trunk/setup.py' % (link_url)
                    dummy = self._get_url(test_url)
                    project_infos.extend(self._parse_svn_dir(link_url))
                    continue
                except Exception, e:
                    pass
            finally:
                self._status_indent -= 1

            # For any other link, assume it might be a directory that contains
            # a setup.py, but expect that assumption not to hold.
            try:
                self._status_indent += 1
                try:
                    info = self._get_project_info_from_svn(link_url)
                    project_infos.append(info)
                    self._status('Identified project "%s" ' % info['name'] + \
                        'version "%s"' % info['version'])
                except Exception, e:
                    if '404' not in str(e):
                        self._status('ERROR: Unable to get project info due '
                            'to error: %s' % str(e))
            finally:
                self._status_indent -= 1

        return project_infos


    def _record_project(self, info):
        """
        Add the specified project to this set.

        Does nothing if the project is already in this set.

        """

        # Merge requests if we've already added this project.
        name = info['name']
        version = info['version']
        if name in self._projects:

            # Report any version mis-matches.
            existing = self._projects[name]
            if version != existing['version']:
                raise VersionConflict('Unexpected version mismatch! Wanted '
                    '%s but already had %s of %s' % (
                    version, existing['version'], name))

            # Merge any extras lists.
            orig = set(existing['extras'])
            extras = orig.union(info['extras'])
            if len(extras) > len(orig):
                existing['extras'] = extras

                # Only report the new extras.
                new = list(extras.difference(orig))
                self._status('Adding extra %s to %s_%s' % (new, name,
                    version))

            return

        # Report status
        if len(info.get('extras', [])) < 1:
            prj = '%s==%s' % (name, version)
        else:
            prj = '%s%s==%s' % (name, list(info['extras']), version)
        self._status('Adding project: %s' % prj)
        self._status_indent += 1
        try:

            # Store the project info
            self._status('Found source at url: %s' % info['url'])
            self._projects[name] = info

            # If there is no root project yet, make this it.
            if self._root_project is None:
                self._root_project = name

        finally:
            self._status_indent -= 1

        return


    def _safe_setup_execution(self, setup):
        """
        Safely execute a setup.py to return project info.

        Will raise an ``Exception`` if execution fails.

        """

        # Temporarily replace setuptools' and distutils' setup method with
        # a version that just records the keyword arguments.
        class Keywords(object):
            keywords = {}
        k = Keywords()
        def my_setup(**kws):
            k.keywords = kws
        import setuptools
        old_setuptools_setup = setuptools.setup
        setuptools.setup = my_setup
        try:
            import numpy.distutils.core
            old_numpy_distutils_setup = numpy.distutils.core.setup
            numpy.distutils.core.setup = my_setup
        except Exception:
            old_numpy_distutils_setup = None

        # Redirect stdout and stderr to prevent output from showing up at the
        # console
        buffer = StringIO.StringIO()
        sys.stdout = sys.stderr = buffer

        # Parse the downloaded setup.py.  If we get an exception while running
        # the full version, try running it when it is not the main file.
        try:
            try:
                scope = {'__file__':'setup.py', '__name__':'__main__'}
                exec setup in scope
                self._status('Fully executed setup.py')
            except:
                scope = {'__file__':'setup.py'}
                exec setup in scope
                self._status('Executed setup.py but not as __main__')
        finally:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            setuptools.setup = old_setuptools_setup
            if old_numpy_distutils_setup is not None:
                numpy.distutils.core.setup = old_numpy_distutils_setup

        # Retrieve whatever project information we can get from the setup.py
        if len(k.keywords) > 0:
            info = k.keywords.copy()
        else:
            info = self._update_dict(None, 'name', scope, 'NAME')
            info = self._update_dict(info, 'version', scope, 'VERSION')
            info = self._update_dict(info, 'install_requires', scope,
                'INSTALL_REQUIRES', [])

        return info


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


    def _tmp_copy_of_svn_dir(self, url, path=None):
        """
        Create a local, temp-dir copy of the specified svn directory tree.

        """

        # Create a temporary directory if one wasn't specified
        if path is None:
            cur_dir = os.getcwd()
            count = 0
            while True:
                count += 1
                name = 'etsco.%s' % count
                path = os.path.join(cur_dir, name)
                if not os.path.exists(path):
                    break
            os.makedirs(path)

        # Report status
        self._status('Making local copy of "%s" ' % url)
        self._status_indent += 1
        try:


            # Retrieve the svn directory listing
            index = self._get_url(url)

            # Iterate through all files or directories.
            pattern = r'<li><a href="(.*)">'
            for link in re.findall(pattern, index):

                # If the link is a file, download it now.
                if '/' not in link[-1:]:
                    self._status('Copying file %s' % link)
                    child_path = os.path.join(path, link)
                    local_file = open(child_path, "wb")
                    child_url = '%s/%s' % (url, link)
                    remote_file = self._get_url(child_url)
                    shutil.copyfileobj(remote_file, local_file, 8192)
                    remote_file.close()
                    local_file.close()

                # Otherwise, treat it as a directory
                else:
                    link = link[:-1]
                    child_url = '%s/%s' % (url, link)

                    # Ignore '.' or '..' directories
                    if link == '.' or link == '..':
                        continue

                    # Recurse into directories
                    else:
                        child_path = os.path.join(path, link)
                        os.makedirs(child_path)
                        self._tmp_copy_of_svn_dir(child_url, child_path)

        finally:
            self._status_indent -= 1

        return path


    def _update_dict(self, dst, dst_var, src, src_var, default=None):
        """
        Copy the value of the specified src_var to the dst_var.

        The dst value passed in maybe None, and a new dictionary will be
        created -- but only if the src_var actually exists in the src
        dictionary.

        The specified default value is only applied to the dst dictionary if
        the passed dst is not None and the src_var doesn't exist in the src
        dictionary.

        """

        if src.has_key(src_var):
            if dst is None:
                dst = {dst_var:src[src_var]}
            else:
                dst[dst_var] = src[src_var]

        else:
            if dst is not None and default is not None:
                dst[dst_var] = default

        return dst





