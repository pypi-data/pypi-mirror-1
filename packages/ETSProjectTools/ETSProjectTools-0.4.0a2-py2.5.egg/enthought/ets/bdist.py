"""
Perform a build on the projects within a checkout.

Copyright (c) 2007 by Enthought, Inc.
License: BSD Style.

"""

# Standard library imports
import glob, os, shutil, subprocess, sys

# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand


class BDist(BaseSubcommand):
    """
    Perform a bdist on the projects within a checkout.

    """

    def __init__(self, subparsers):
        desc = ('Build "stable" ETS component eggs.  If no explicit '
            'directories are specified, then will scan the current directory '
            'tree looking for component directories to build / clean.')
        parser = subparsers.add_parser('bdist',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'A checkout to build',
            nargs = '*',
            )

        # Add common options
        parser.add_argument('-c', '--clean',
            action = 'store_true',
            dest = 'clean',
            help = 'perform a clean operation (prior to doing anything else)',
            )
        self.dry_run(parser)
        
        """ To Be Implemented
        parser.add_argument('-E', '--no-eggs',
            action = 'store_false',
            default = True,
            dest = 'eggs',
            help = 'suppress the building of eggs',
            )
        """
        
        parser.add_argument('-o', '--output-dir',
            default = 'dist',
            dest = 'dest',
            help = 'specify the destination directory for build output ' \
                '(defaults to %(default)s)',
            )
        parser.add_argument('-p', '--rpm',
            action = 'store_true',
            dest = 'rpm',
            help = 'build binaries in RPM format',
            )
        parser.add_argument('-r', '--release',
            action = 'store_true',
            dest = 'release',
            help = 'build release versions',
            )
        parser.add_argument('-s', '--sdist',
            action = 'store_true',
            dest = 'source',
            help = 'build source tarballs',
            )
        parser.add_argument('-t', '--test',
            action = 'store_true',
            dest = 'test',
            help = 'run tests as well as building',
            )
        parser.add_argument('-T', '--test-file',
            dest = 'test_file',
            default = 'tests.out',
            help = 'specify the file to write test output too. '
                '(defaults to %(default)s)',
            )
        parser.add_argument('-v', '--verbose',
            action = 'store_true',
            dest = 'verbose',
            help = 'show all output from the build commands'
            )

        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Build each project within a checkout.
        
        """
        
        # If no explicit directory specification provided, use all of the
        # component directories we can find.
        print ''
        if len(args.path) == 0:
            print 'Finding component directories to operate on...'
            args.path = self.find_component_dirs()
            print '...Done\n'
    
        # Perform a clean if the user requested it, otherwise build the target
        # eggs.
        if args.clean:
            self.clean(args.path, dest=args.dest)
        elif args.test:
            self.test(args.path, args.test_file, verbose=args.verbose)
        elif args.rpm:
            self.build_rpms(args.path, dest=args.dest, release=args.release,
                verbose=args.verbose)
        else:
            self.build_eggs(args.path, dest=args.dest, release=args.release,
                source=args.source, verbose=args.verbose)

        return
    
    def error(self, msg):
        bar = 78*'*'
        print '\n%s\nERROR: %s\n%s\n' % (bar, msg, bar)
    
        return
    
    
    def find_component_dirs(self):
        d = []
        for file in os.listdir('.'):
            if os.path.isdir(file):
                if os.path.exists(os.path.join(file, 'setup.py')):
                    d.append(file)
    
        d.sort()
    
        return d
    
    
    def build_eggs(self, dirs, dest='dist', release=False, source=False,
        verbose=False):
    
        # Ensure the destination directory exists.
        dest = os.path.abspath(dest)
        if not os.path.exists(dest):
            os.mkdir(dest)
    
        # Create the build command to be run.
        args = [sys.executable, 'setup.py']
        if not verbose:
            args.extend(['--quiet'])
        if release:
            args.extend(['release'])
        if source:
            args.extend(['egg_info', 'sdist'])
        else:
            args.extend(['build'])
            if sys.platform=='win32':
                args.extend(['--compiler=mingw32'])
            args.extend(['bdist_egg'])
        args.extend(['-d', dest])
    
        # Build an egg or source tarball out of each specified directory.
        for d in dirs:
            print "=" * 78
            print 'Building directory: %s\n' % d
    
            # Make sure the component directory exists.
            if not os.path.isdir(d):
                self.error('Can not find directory "%s"' % d)
                continue
    
            # Make sure the setup.py exists.
            if not os.path.exists(os.path.join(d, 'setup.py')):
                self.error('Can not find setup.py')
                continue
    
            # Run the build command.
            print "Executing: %s" % (" ".join(args))
            ret = subprocess.call(args, cwd=d)
            if ret != 0:
                self.error('Build error: exited with value = %s' % ret)
    
            print ''
    
        # Generate the egg_info files for Enstaller to use when browsing the
        # repo.
        if not source:
            try:
                from enthought.enstaller.egg import Egg
    
                print '\n\n' + '*'*78
                print 'Building egg_info files...'
                for file in glob.glob(os.path.join(dest, '*.egg')):
                    print '  %s' % file
                    egg = Egg(file)
                    egg.create_info_file()
            except Exception, e:
                print 'WARNING: Could not build egg.info files: %s' % e
    
        return
    
    
    def build_rpms(self, dirs, dest='dist', release=False, source=False,
        verbose=False):
    
        # Ensure the destination directory exists.
        dest = os.path.abspath(dest)
        if not os.path.exists(dest):
            os.mkdir(dest)
    
        # Create the build command to be run.
        args = [sys.executable, 'setup.py']
        if not verbose:
            args.extend(['--quiet'])
        if release:
            args.extend(['release'])
        args.extend(['build'])
        if sys.platform=='win32':
            args.extend(['--compiler=mingw32'])
        args.extend(['bdist_rpm'])
        args.extend(['-d', dest])
    
        # Build an rpm and srpm out of each specified directory.
        for d in dirs:
            print "=" * 78
            print 'Building directory: %s\n' % d
    
            # Make sure the component directory exists.
            if not os.path.isdir(d):
                self.error('Can not find directory "%s"' % d)
                continue
    
            # Make sure the setup.py exists.
            if not os.path.exists(os.path.join(d, 'setup.py')):
                self.error('Can not find setup.py')
                continue
    
            # Run the build command.
            print "Executing: %s" % (" ".join(args))
            ret = subprocess.call(args, cwd=d)
            if ret != 0:
                self.error('Build error: exited with value = %s' % ret)
    
            print ''
    
        return
    
    
    def clean(self, args, dest='dist'):
        for d in args:
            print "Cleaning: %s" % d
            try:
                shutil.rmtree(os.path.join(d, 'build'))
            except OSError:
                pass
            try:
                shutil.rmtree(os.path.join(d, 'dist'))
            except OSError:
                pass
            try:
                shutil.rmtree(os.path.join(d, '%s.egg-info' % d))
            except OSError:
                pass
    
        print 'Cleaning: %s' % dest
        try:
            shutil.rmtree(dest)
        except OSError:
            pass
    
        return
    
    def test(self, dirs, out, verbose=False):
    
        # Create the build command to be run.
        args = [sys.executable, 'setup.py']
        if not verbose:
            args.extend(['--quiet'])
        args.extend(['test'])
    
        # Track whether there were any build failures.
        had_failures = False
    
        # Create a file handle for the output file
        outfile = open(out, 'w')
        try:
    
            # Run the tests in each specified directory
            for d in dirs:
                print "=" * 78
                print 'Processing directory: %s\n' % d
    
                # Make sure the component directory exists.
                if not os.path.isdir(d):
                    self.error('Can not find directory "%s"' % d)
                    continue
    
                # Make sure the setup.py exists.
                if not os.path.exists(os.path.join(d, 'setup.py')):
                    self.error('Can not find setup.py')
                    continue
    
                # Add the name of the package tested to the output file:
                outfile.write("*" * 78 + "\n")
                outfile.write( "* " + d + "\n")
                outfile.write("*" * 78 + "\n")
                outfile.flush()
    
                # Run the command.
                print "Executing: %s" % (" ".join(args))
                ret = subprocess.call(args, cwd=d, stdout=outfile,
                    stderr=subprocess.STDOUT)
                if ret != 0:
                    self.error('TESTS FAILED!  Please look in %s for more ' \
                        'info.' % out)
                    had_failures = True
    
                print ''
    
        finally:
            outfile.close()
    
        print "V" * 78
        print "=" * 78
        print 'Test results are in %s' % out
        if had_failures:
            print ''
            print 'Please ensure all failures are known to the source ' \
                'providers!'
            print 'You can report errors through Enthought\'s Trac site at: '
            print '\thttps://svn.enthought.com/enthought'
            print 'Make sure to mention your platform and versions!'
        print "=" * 78
        print "^" * 78
    
    
        return

