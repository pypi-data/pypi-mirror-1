#------------------------------------------------------------------------------
# Copyright (c) 2007 by Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from egg_db_command import EggDBCommand
from collector import SYMBOL_SEP
from ConfigParser import SafeConfigParser
from distutils.sysconfig import get_python_lib
from egg_db import (EGG_DB_FILE, get_egg_db, MAP_SECTION, ROOT_SECTION,
    SYMBOL_SECTION)
from pkg_resources import parse_requirements
from setuptools.command.bdist_egg import walk_egg
import compiler
import imp
import os
import sys
import traceback


SYSMODDIR = os.path.dirname(get_python_lib())
if sys.version.split()[0] == '2.5':
    from python_packages import python25
    IGNORE = sys.builtin_module_names + python25
else:
    IGNORE = sys.builtin_module_names + (
        'compiler', 'os', 'os.path', 'pickle', 'pkg_resources', 're',
        'setuptools',
        )


class ValidateDeps(EggDBCommand):

    ##########################################################################
    # Attributes
    ##########################################################################

    #### public 'Command' interface ##########################################

    description = ('Validate the dependencies listed as being required '
        'by an egg match those actually imported in the source.')


    ##########################################################################
    # 'Command' Interface
    ##########################################################################

    #### public methods ######################################################

    def finalize_options(self):
        # FIXME: Can't use 'super' since distutils.Command is not a 'new' style
        # class
        EggDBCommand.finalize_options(self)

        return


    def initialize_options(self):
        # FIXME: Can't use 'super' since distutils.Command is not a 'new' style
        # class
        EggDBCommand.initialize_options(self)

        return


    def run(self):
        # Get the current egg database
        if not os.path.exists(self.egg_db):
            self._error('Egg database file "%s" not found!\t' % self.egg_db + \
                '(Run the "etscollect" command to generate one.)')
            return
        self.parser = get_egg_db(self.egg_db, verbose=self.verbose)

        # Generate metadata first
        self.run_command("egg_info")

        # Retrieve the list of dependencies already specified in our setup.py.
        deps = self.get_declared_dependencies()

        # Build a dictionary of all known eggs and extras required by the
        # imports in the source files that make up this egg.  The keys are the
        # egg and extras names, in a format of "<egg_name>[<extra1>,...]".
        # The values are dictionaries where the keys are the imported symbols
        # that caused us to require this egg & extra, and the values are lists
        # of all the source modules that imported that symbol.
        requirements = self.get_requirements()

        # Calculate the gaps in our dependencies.  There are two cases.  First,
        # is the dependencies from which we do not import anything in our
        # source.  Second, is the dependencies which are not declared but from
        # which we import.
        not_imported, not_declared = self.calculate_differences(deps,
            requirements.keys())

        # Display the results
        print '*'*79
        print ('The following egg dependencies had no imports:\n\t'
            '%s' % '\n\t'.join(not_imported))
        print ('Imports from the following eggs were not declared as '
            'dependencies:\n\t'
            '%s' % '\n\t'.join(not_declared))
        print '*'*79

        return


    ##########################################################################
    # 'ValidateDeps' Interface
    ##########################################################################

    #### public methods ######################################################

    def calculate_differences(self, deps, imported):
        """
        Return a tuple of sets representing the not imported, and not declared
        packages / modules.

        """

        # Remove everything obvious
        deps = set(deps)
        imported = set(imported)
        not_declared = imported.difference(deps)
        not_imported = deps.difference(imported)

        # Filter out any imports that are children of a declared dependency.
        was_imported = set()
        for module in set(not_declared):
            root = ''
            path = module
            join = ''
            while path.find('.') >= 0:
                nextroot, path = path.split('.', 1)
                root += join + nextroot
                join = '.'
                if root in not_imported:
                    not_declared.remove(module)
                    was_imported.add(root)
                    break
        not_imported = not_imported.difference(was_imported)

        # Convert to sorted lists
        not_declared = list(not_declared) ; not_declared.sort()
        not_imported = list(not_imported) ; not_imported.sort()

        return (not_imported, not_declared)


    def get_declared_dependencies(self):
        """
        Return a list of the eggs required by setup.py.

        The returned list is built by parsing the list of eggs in the
        'install_requires' section, and the extras section of the setup.py.

        """

        required_eggs = []

        # Parse the install requirements
        reqs = parse_requirements(self.distribution.install_requires or (()))
        for r in reqs:
            name = r.unsafe_name
            if name not in required_eggs:
                required_eggs.append(name)
            if len(r.extras) > 0:
                for e in r.extras:
                    extra_name = '%s[%s]' % (name, e)
                    if extra_name not in required_eggs:
                        required_eggs.append(extra_name)

        # Parse the extras requirements.
        extras_require = self.distribution.extras_require or {}
        for k,v in extras_require.items():
            reqs = parse_requirements(v or (()))
            for r in reqs:
                name = r.unsafe_name
                if name not in required_eggs:
                    required_eggs.append(name)
                if len(r.extras) > 0:
                    for e in r.extras:
                        extra_name = '%s[%s]' % (name, e)
                        if extra_name not in required_eggs:
                            required_eggs.append(extra_name)

        # Print the data if we're in verbose mode.
        if self.verbose:
            print
            self._status('Declared dependencies:\n%s', '\n'.join(required_eggs))

        return required_eggs


    def get_imports(self):
        """
        Return a dictionary of the imports within the sources in this egg.

        The key is the full specification of the symbol being imported and the
        value is a list of all the source modules that imported that symbol.

        This list is built by scanning the python source inside the packages
        listed as being part of the egg.  We do not actually import any source!

        """

        results = {}

        # Iterate through all modules in the packages in this egg.
        self._status('')
        for p in self.distribution.packages:
            self._status('Scanning package: %s' % p)
            base = p.replace('.', os.path.sep)
            for f in os.listdir(base):
                name = f
                if name.endswith('.py'):
                    path = os.path.join(base, name)

                    # Record each symbol imported as having been imported in
                    # that module.
                    imports = self.get_imports_from_module(path)
                    for symbol in imports:
                        sources = results.setdefault(symbol, [path])
                        if path not in sources:
                            sources.append(path)

        return results


    def get_imports_from_module(self, path):
        """
        Return a list of the symbols imported in the specified module.

        """

        name = os.path.join('.', path)
        self._status('Scanning file: %s' % name, indent=2)

        try:
            mod = compiler.parseFile(name)
        except Exception, e:
            self._error('Unable to process file "%s"\n\t%s' % (name,
                traceback.format_exc(sys.stderr)), indent=2)
            return {}

        visitor = ImportVisitor(name, verbose=self.verbose)
        compiler.walk(mod, visitor)

        return visitor.symbols


    def get_requirements(self):
        """
        Return a dictionary of required eggs derived from actual imports.

        The returned dictionary documents all known eggs and extras required by
        the imports in the source files that make up this egg.  The keys are
        the egg and extras names, in a format of "<egg_name>[<extra1>,...]".
        The values are dictionaries where the keys are the imported symbols
        that caused us to require this egg & extra, and the values are lists
        of all the source modules that imported that symbol.

        """

        requirements = {}

        # Start by building a dictionary of all imported symbols in the source
        # files that make up this egg.  The key is the full specification of the
        # symbol being imported and the value is a list of all the sources that
        # import that symbol.
        imports = self.get_imports()

        # Update the user on what we're doing next.
        print
        self._status('Mapping imports to eggs by packages:')

        # Iterate through all the imports trying to match each up to a package
        # we know to be associated with an egg.
        for imported, sources in imports.items():

            # Find the egg that contains the symbol being imported.
            egg = self._get_matching_egg(imported, sources)
            if egg is None:
                continue

            # Determine any extras required by this import
            extra = self._get_required_extra(egg, imported)
            if extra is not None:
                egg = '%s[%s]' % (egg, extra)

            # Store the requirement in our dictionary of requirements.  If
            # there is already an entry for this egg, add to that entry.
            if egg not in requirements:
                requirements[egg] = {imported: sources}
            else:
                current = requirements[egg]
                if imported not in current:
                    current[imported] = sources
                else:
                    current[imported] = current[imported].extend(sources)

            self._status('Matched egg "%s" to imported symbol "%s"',
                egg, imported, indent=2)

        self._print_requirements_map(requirements)

        return requirements


    #### protected methods ###################################################

    def _get_matching_egg(self, symbol, sources):
        """
        Return the egg depenency that includes the specified symbol.

        A return value of None indicates no match could be made.

        """

        # Match the symbol to a known egg package.  We do this by testing
        # successively shorter symbols so that we get the most fully specified
        # match that we can.
        s = symbol
        while len(s) > 0:
            if self.parser.has_option(SYMBOL_SECTION, s):
                break
            split = s.rsplit('.', 1)
            if len(split) > 1:
                s = split[0]
            else:
                s = ''

        # Issue a warning if we couldn't find an egg containing the symbol.
        if len(s) < 1:
            self._warning('Could not match import of "%s" to a known '
                'egg package. It was imported in:\n%s', symbol,
                '\n'.join(sources), indent=2)
            return None

        # Issue a warning if the symbol matches more than one egg, and then
        # continue by using the egg with the shortest name.  (We're assuming
        # the egg with the shortest name is the most general one and that is
        # the one most likely to be imported from.)
        option = self.parser.get(SYMBOL_SECTION, s)
        eggs = option.split(SYMBOL_SEP)
        if len(eggs) > 1:
            egg = None
            for e in eggs:
                if egg is None:
                    egg = e
                    continue
                if len(e) < len(egg):
                    egg = e
            self._warning('Multiple eggs match import of "%s".  '
                'Using egg "%s".  Matches:\n%s', symbol, egg,
                '\n'.join(eggs), indent=2)
        else:
            egg = eggs[0]

        # Skip our own egg
        if egg == self.distribution.metadata.name:
            egg = None

        return egg


    def _get_required_extra(self, egg, symbol):
        """
        Return the extra required by the import of a symbol from an egg.

        A return value of None indicates no extra is necessary.

        """

        result = None

        # Only do something if there is an extra mapping file.
        if self.parser.has_option(MAP_SECTION, egg):
            map_file = self.parser.get(MAP_SECTION, egg)

            # Read the mapping data.
            map_parser = SafeConfigParser()
            map_parser.read([map_file])

            # Iterate through all the sections, looking for one that has a
            # symbol declaration matching the symbol being imported.  There
            # is no guarantee that there is such a match!
            for section in map_parser.sections():

                # Look for matches at any level of our symbol.
                s = symbol
                while len(s) > 0:
                    if map_parser.has_option(section, s):
                        break
                    split = s.rsplit('.', 1)
                    if len(split) > 1:
                        s = split[0]
                    else:
                        s = ''

                # If we found a match, the name of the section is our extra.
                if len(s) > 0:
                    result = section
                    break

        return result


    def _print_requirements_map(self, requirements):

        # Print nothing if we're not in verbose mode!
        if not self.verbose:
            return

        self._status('')
        self._status('Egg Dependency Map:')
        rkeys = requirements.keys()
        rkeys.sort()
        for rk in rkeys:
            self._status('Egg: %s' % rk, indent=2)

            imports = requirements[rk]
            ikeys = imports.keys()
            ikeys.sort()
            for ik in ikeys:
                self._status('Import: %s' % ik, indent=4)
                for source in imports[ik]:
                    self._status('From: %s' % source, indent=6)
        return


class ImportVisitor(compiler.visitor.ASTVisitor):
    """
    Records symbols imported when walking an AST.

    """

    def __init__(self, filename, verbose=False):
        self.filename = filename
        self.symbols = []
        self.verbose = verbose

        # Setup to attempt to detect local imports
        self.dir = os.path.dirname(filename)
        self.localfiles = []
        for f in os.listdir(self.dir):
            name, ext = os.path.splitext(f)
            self.localfiles.extend([name, f])

        return


    def accept_module(self, name):
        # Filter out imports of local modules
        if name in self.localfiles:
            return

        # Filter out imports of local packages
        if name.find('.') >= 0:
            pack, dummy = name.split('.', 1)
            if pack in self.localfiles:
                return

        # Ignore any builtin modules.
        if name in IGNORE:
            return

        # Ignore any standard library modules.
        if name.find('.') < 0:
            try:
                (mod_file_obj, mod_path, mod_desc) = imp.find_module(name)
                if mod_file_obj is not None:
                    mod_file_obj.close()
                if (not mod_path.endswith("site-packages") and \
                    mod_path.startswith(SYSMODDIR)):
                    return
            except ImportError:
                pass

        # Record this module as being imported.
        if name not in self.symbols:
            self.symbols.append(name)
            if self.verbose:
                print ' '*4 + 'Imports symbol: %s' % name

        return


    def visitImport(self, node):
        self.accept_module(node.names[0][0])

        return


    def visitFrom(self, node):
        self.accept_module(node.modname)

        return


#### EOF #####################################################################

