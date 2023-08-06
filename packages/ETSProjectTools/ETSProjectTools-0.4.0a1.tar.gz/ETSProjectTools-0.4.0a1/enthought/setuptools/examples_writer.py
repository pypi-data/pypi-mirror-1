""" Metadata writer for adding examples to a distribution's
EGG-INFO and its data_files.
"""

#------------------------------------------------------------------------------
# Copyright (c) 2007 by Enthought, Inc.
# All rights reserved.
#------------------------------------------------------------------------------

from distutils.errors import DistutilsError
import glob
import os
from os.path import basename, dirname, isfile, isdir, islink


# We settle on using the forward slash for all paths inside the examples_map
# file.  (We can't use os.sep because we want the map file to work across
# platforms.)
SEPARATOR = "/"
def join(*args):
    return SEPARATOR.join([x for x in args if len(x) > 0])

def split(fn):
    """ Emulates os.path.split but uses SEPARATOR instead of os.sep """
    count = fn.count(SEPARATOR)
    if count == 0:
        return ("", fn)
    elif count == 1:
        return fn.split(SEPARATOR)
    else:
        parts = fn.split(SEPARATOR)
        return (SEPARATOR.join(parts[:-1]), parts[-1])

#------------------------------------------------------------------------------
# Validation functions
#------------------------------------------------------------------------------

def validate_examples(dist, attr, value):
    pass

def validate_examples_map(dist, attr, value):
    pass


#------------------------------------------------------------------------------
# Metadata writer
#------------------------------------------------------------------------------


class ConfigWalker(object):
    """ This is used to walk the sections of the config object and compile
    the list of files referenced in all the sections.  Each file name has
    the entire relative source path prepended to it.
    """

    def __init__(self, basedir=""):
        self.basedir = basedir
        self.files = []
        self.prev_sourcedir = None

    def collect_filenames(self, examples):
        """ Gathers up all the paths in **examples** and returns them in
        a list.
        """
        old_basedir = self._basedir
        examples.walk(self)
        files = self.files
        self._basedir = old_basedir
        return files

    def pushdir(self, newdir):
        """ Appends the new directory to our basedir """
        self.basedir = join(self.basedir, newdir)

    def popdir(self, dir):
        """ Removes the last directory in basedir if it matches **dir** """
        root, end = split(self.basedir)
        if end == dir:
            self.basedir = root
        return
    
    def trunc_path(self, path):
        """ Returns a relative path to path from self.basedir.  This only
        works if path is a subdirectory of self.basedir.
        """
        if self._cached_length is None:
            length = len(self._basedir)
            if length > 0 and not self._basedir.endswith(SEPARATOR):
                length += 1
            self._cached_length = length
            
        if path.startswith(self._basedir):
            return path[self._cached_length:]
        else:
            return path

    def glob(self, pattern):
        """ Recursive glob implementation to handle directories & symlinks """
        candidates = glob.glob(pattern)
        files = []
        for candidate in candidates:
            if isdir(candidate):
                files.extend(self.glob(join(candidate, "*")))
            elif islink(candidate):
                files.extend(self.glob(os.readlink(candidate)))
            else:
                files.append(candidate)
        if SEPARATOR != os.sep and os.sep in pattern:
            return [f.translate(os.sep, SEPARATOR) for f in files]
        else:
            return files

    def __call__(self, section, key):
        """ Parses a particular key in a section. """
        if section.has_key('sourcedir'):
            if self.prev_sourcedir and\
                    self.prev_sourcedir != section.parent.get('sourcedir', None):
                self.popdir(self.prev_sourcedir)
            self.pushdir(section['sourcedir'])
            self.prev_sourcedir = section['sourcedir']
        elif key == 'files':
            value = section[key]
            if not isinstance(value, list):
                value = [value]
            for filespec in value:
                newfiles = self.glob(join(self.basedir, filespec))
                self.files.extend(newfiles)
        # TODO: Implement key == 'destdir', i.e. per-example destdirs
        return

    def _get_basedir(self):
        return self._basedir

    def _set_basedir(self, val):
        self._basedir = val
        self._cached_length = None
    
    basedir = property(_get_basedir, _set_basedir)


def safe_chained_get(d, key, val=None):
    """ Behaves like get() on dicts, except that **key** can be a string with
    dots representing a chain of attributes.  If any of the keys in the chain
    is not defined, then returns **val**.

    So, safe_chained_get(d, "foo/bar/baz", 3) will return foo["bar"]["baz"] if
    those keys are found, and will return 3 otherwise.

    The separator is '%s'.
    """ % SEPARATOR
    subkeys = key.split(SEPARATOR)
    obj = d
    for k in subkeys:
        if obj.has_key(k):
            obj = obj.get(k)
        else:
            return val
    return obj


def process_examples_map(dist):
    """ Parses the examples_map option in a distribution and adds all of 
    the example files to the distribution's data_files.

    Returns a ConfigObj that can be written to EGG-INFO/examples_map.
    """
    if dist.examples_map in (None, ''):
        return {}

    from configobj import ConfigObj, ConfigObjError
    try:
        examples = ConfigObj(dist.examples_map)
    except ConfigObjError:
        raise DistutilsError("Unable to parse examples_map file: '%s'" % \
                              dist.examples_map)
    walker = ConfigWalker(basedir=split(dist.examples_map)[0])
    files = walker.collect_filenames(examples)

    # Update the distribution's data_files list.  Create the right destination
    # path based on the destdir setting.
    if safe_chained_get(examples, "global/destdir"):
        destdir = examples["global"]["destdir"]
        make_dest_path = lambda f: join(destdir, walker.trunc_path(f))
    else:
        make_dest_path = walker.trunc_path

    if dist.data_files is None:
        dist.data_files = []
    dist.data_files.extend( [(make_dest_path(dirname(fn)), [fn]) for fn in files] )
    return examples


def process_examples(dist):
    """ Parses the **examples** option in a distribution and adds all of
    the example files to the distribution's data_files.

    Returns a ConfigObj that can be written to EGG-INFO/examples_map.
    """
    if dist.examples is None:
        return {}

    from configobj import ConfigObj, ConfigObjError
    try:
        examples = ConfigObj(dist.examples)
    except ConfigObjError, e:
        raise DistutilsError("Unable to collect examples: '%r'" % e)
    basedir = examples.pop("__basedir__", "")
    walker = ConfigWalker()
    files = walker.collect_filenames(examples)
    walker.basedir = basedir

    if safe_chained_get(examples, "global/destdir"):
        destdir = examples["global"]["destdir"]
        make_dest_path = lambda f: join(destdir, walker.trunc_path(f))
    else:
        make_dest_path = walker.trunc_path
    
    if dist.data_files is None:
        dist.data_files = []
    dist.data_files.extend( [(make_dest_path(dirname(fn)), [fn]) for fn in files] )
    return examples


def examples_writer(cmd, basename, filename):
    """ Command to write information about documentation to the
    docs.txt file in EGG-INFO.
    """
    
    # Look for examples and examples_map in the distribution
    dist = cmd.distribution

    # Parse the 'examples_map' option
    examples_map = process_examples_map(dist)

    # Parse the 'examples' option
    examples = process_examples(dist)

    if examples and examples_map:
        examples.merge(examples_map)
    elif examples_map:
        examples = examples_map
    elif not examples:
        return

    # Write out the examples config into the metadata.  
    examples.filename = None
    lines = examples.write()
    cmd.write_file("examples_map", filename, "\n".join(lines) + "\n")



