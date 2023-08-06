===================================================
ETSProjectTools: Part of the Enthought Tool Suite
===================================================

Description
-----------

This project provides tools that improve a developer's ability to work
with sources, build and deliver binaries, and provide help and examples for
any project.



Installation
------------

Installation of the latest release is as simple as doing::

    easy_install ETSProjectTools

If you don't have setuptools installed, or you prefer to get the latest version
from svn, you can simply check-out the project source from svn::

    svn co https://svn.enthought.com/svn/enthought/ETSProjectTools/trunk ETSProjectTools

then, assuming you have setuptools 0.6c7 or later installed, install it via
commands like::

    cd ETSProjectTools
    python setup.py install

After that completes, you can check for proper installation by running the
following and confirming you get the usage output::

    ets co -h

See `Troubleshooting`_ if this command produces error messages.



Source Interaction Tools
------------------------

ets co
~~~~~~

The ``ets co`` command checks out the source for one or more projects
and, by default, all of their dependencies, into a common top-level directory.
The project sources are checked-out from one or more svn repositories.  A
typical command line looks like::

    ets co ETS

Which will find the latest version of the ETS meta-egg in the known
repositories, find the source locations for all dependent projects of ETS, and
all the dependent projects of those projects, etc., and finally check-out the
sources for that complete set of projects into a directory structure like::

    ETS_3.0.0b1/
        AppTools_3.0.0b1/
            <source for AppTools project>
        BlockCanvas_3.0.0b1/
            <source for BlockCanvas project>
        ...
        ETS_3.0.0b1/
            <source for ETS project>
        ...
        TraitsGUI_3.0.0b1/
            <source for TraitsGUI project>

That is, the top-level directory is named for the first explicitly requested
project that you requested, and there is a sub-directory under that for each
project that was a dependency or that you explicitly requested.  Those
sub-directories contain the source for the right version of those projects as
per the dependency specifications.



Specifying An Explicit Top-Level Directory
__________________________________________

The ``ets co`` command supports an option, ``-o`` or ``--output-dir``, to allow
you to explicitly specify the top-level, or output, directory.   By default,
the output directory will take on the name of the first project and version
specified as an argument when you run the script.   For example, the following
command::

    ets co "enthought.traits == 2.0.1b1"

will normally create a checkout  called ``enthought.traits_2.0.1b1``
and then checkout the project sources into directories underneath that.  But
you could force it to use a specific directory, say ``~/src/trunk``, like so::

    ets co -o ~/src/trunk "enthought.traits == 2.0.1b1"



Specifying Explicit Projects and Versions
_________________________________________

The ``ets co`` command takes any number of arguments as a set of explicit
projects to be checked out.  (All dependencies of these projects will also be
checked out.)  The arguments can be any of:

 - a setuptools Requirement specification.  A Requirement is composed of a
   project name and a version specification.  For example,
   ``Traits == 3.0.0b1`` and ``Mayavi < 3.0a``.  These
   Requirements will be matched against the set of projects and versions
   actually found in the known repositories such that the best match,
   according to standard setuptools' rules, is the project that will be
   checked out.

 - a URL to the SVN source tree of a project: the specified directory must
   contain a ``setup.py`` file so that the tool can identify the project name,
   version, and dependencies.

It is important to note that ``ets co`` always prefers any explicit project
and version that you specify over any version that may match a dependency
declaration of any project being checked out.   For example, if you do::

    ets co "projectA == 2.0" "projectB < 3.0a"

and the dependency specification of ``projectA`` is ``projectB > 2.0``, your
checkout will include a version of ``projectB`` that is less than ``3.0a`` even
if versions later than that exist in the repository and would otherwise have
been chosen by ``projectA``'s dependency specification.



Working Through A Proxy
_______________________

The ``ets co`` command provides the ``--proxy`` option to allow it to interact
with an SVN repository via a proxy server -- including one that requires
authentication via the 'Basic Authentication' protocol.   Simply do something
like::

    ets co --proxy user:[password]@proxyserver:port trunk

Note that we recommend leaving the password specification out of your command
line.  If you do so, the script will prompt you for the password and allow you
to type it without it echoing to the screen.   If your proxy doesn't require
authentication at all, simply leave the user ID and '@' off the command line
like::

    ets co --proxy proxyserver:port trunk


Note also that, since ``ets co`` spawns the standard svn checkout command to
actually perform the checkouts, you must also configure SVN itself to work
through your proxy.  ``ets co`` does not do that for you.


Tags Warning
____________

In many cases, project source that you check out as a result of running
``ets co`` comes from a tag representing an actual released version of a
project.  These sources should NEVER be changed, or else no one will be able
to easily rebuild those releases.  Therefore, it is important that you NOT
check-in changes to the source checked-out from a tag.  As a result, ``ets co``
outputs a strong warning message if it detects that any of the project
source it checked out came from a tag.

We currently do not do anything to enforce that you not check-in to a tag.
We are trusting you to be careful. :-)


ets up
~~~~~~

The command ``ets up`` takes a single argument, meant to be a checkout directory
created by running the ``ets co`` command, and runs an SVN update command for each
checked-out project source tree.


ets st
~~~~~~

The command ``ets st`` takes a single argument, meant to be a checkout directory
created by running the ``ets co`` command, and runs an SVN status command for each
checked-out project source tree.


ets rev
~~~~~~~

The command ``ets rev`` takes a single argument, meant to be a checkout directory
created by running the ``ets co`` command, and runs an SVN revert command for each
checked-out project source tree.  This is particularly useful if you've setup
these project checkouts to be accessible in your Python environment via a
``setup.py develop`` type command, have modified them to aid in or do
debugging, and now want to restore back to the original version.


ets develop
~~~~~~~~~~~

The command ``ets develop`` takes a single argument, meant to be a checkout 
directory created by running the ``ets co`` command, and runs a
``python setup.py develop -N`` command for each checked-out project source
tree, thus making that project active in the current Python environment.

This command also allows you to specify additional arguments for the ''develop''
command by using the '-e' option.   For example, if you want to setup your
egg links for the developed projects into a non-standard dir, you might do::

    ets develop -e"-d /home/dpeterson/usr/lib/python2.5/site-packages"



Troubleshooting
---------------

'ets' is not a command
~~~~~~~~~~~~~~~~~~~~~~
**Symptom**: System message about 'ets' not being a recognized or found as a 
command.

**Reason**: The standard Python scripts directory is not in your PATH. 

**Solution**: Ensure that the standard Python scripts directory is in your PATH.
On Windows, this is something like ``C:\Python25\Scripts`` or ``C:\Python25\Tools``.


ImportError: cannot import name setup_authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Symptom**: Python ImportError for setup_authentication

**Reason**: Your system has a version of enthought.proxy installed that is
different from the one in ETSProjectTools; most likely this is because you
have installed Enstaller.  Or, you have an older version of ETSProjectTools
installed -- it used to be called PackageTools, then ETSPackageTools, before
its current name of ETSProjectTools.

**Solution**: "Uninstall" the Enstaller project, or PackageTools, or
ETSPackageTools,  by editing easy-install.pth and removing the line(s) that 
reference any of these projects.  Alternatively, you can rename the egg files
or directories, or even delete, or move them.


WARNING: The SOURCES for the following projects could not be located
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Symptom**: 'ets co' reports this warning when doing a checkout.

**Reason**: You checked out source for projects that have a dependency on
one or more projects that are not in the known repositories. 

**Solution**: If you don't need the source for the referenced projects, you 
don't need to do anything in response to this message. If you do need the
source, run the script again, and use the -r option to specify additional
repositories to search.

