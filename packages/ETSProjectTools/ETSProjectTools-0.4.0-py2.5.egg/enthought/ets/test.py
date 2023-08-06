"""
Perform tests for ETS projects.

Copyright (c) 2008 by Enthought, Inc.
All rights reserved.
License: BSD Style.
Author: Ilan Schnell <ischnell@enthought.com>

"""

# Standard library imports
import commands
import os
import re
import time


# Project library imports
from enthought.ets.base_subcommand import BaseSubcommand


class Test(BaseSubcommand):
    """
    Perform tests.

    """

    def __init__(self, subparsers):
        desc = (
            'Perform tests. If no path is explicitly specified, '
            'all the projects are tested.')
        parser = subparsers.add_parser('test',
            description = desc,
            help = '. . . %s' % desc,
            )

        # Add arguments
        parser.add_argument('path',
            default = [],
            help = 'Path to project to be tested.',
            nargs = '*',
            )

        # Add options
        parser.add_argument('-c', '--cmd',
            default = 'python setup.py test',
            dest = 'cmd',
            metavar = 'STR',
            help = 'Command executed in project folder. '
                   'The default is %(default)r.',
            )
        parser.add_argument('--html',
            action = 'store_true',
            dest = 'html',
            help = 'Store the results from running the tests in HTML format '
               'in the directory "ets_test_html".',
            )
        parser.add_argument('--json',
            action = 'store_true',
            dest = 'json',
            help = 'Store the results from running the tests in JSON format '
               'in the file "ets_test.json".',
            )
        parser.add_argument('--pkl',
            action = 'store_true',
            dest = 'pkl',
            help = 'Store the results from running the tests in the pickle '
               'file "ets_test.pkl".',
            )
        parser.set_defaults(func=self.main)

        return


    def main(self, args, cfg):
        """
        Run tests for projects.

        """
        # If no path was specified, test all projects.
        if args.path is None or len(args.path) < 1:
            import glob
            self.projects = [os.path.split(p)[0]
                             for p in glob.glob('*/setup.py')]
        else:
            self.projects = [os.path.normpath(p) for p in args.path]

        self.cmd = args.cmd
        self.verbose = True
        self.format = '%-25s %5s      %s'
        self.time_start = time.time()

        # The methods self.info_xxx() store the collected information
        # into the attribute self.dat
        self.dat = {}

        self.info_datetime()
        self.info_revision()
        self.info_tests()
        self.info_total()
        self.info_system()

        if args.pkl:
            self.store_pkl('ets_test.pkl')

        if args.json:
            self.store_json('ets_test.json')

        if args.html:
            self.store_html('ets_test_html')

        return


    def info_tests(self):
        """
        Run the tests for the projects given by attribute self.projects,
        and add all gathered results into self.dat.

        """
        if self.verbose:
            print self.format % ('Project', 'Tests', 'Result')
            print 70 * '-'

        dat = {}
        for project in sorted(self.projects):
            if project.startswith('ETS_'): continue
            if project.startswith('TraitsBackend'): continue

            d = self.run_cmd(project)
            d.update(self.extract_result(d['output']))
            d.update(self.extract_from_status(d['status']))
            d.update(self.extract_coverage(d['output']))

            if self.verbose:
                print self.format % (project, d['tests'], d['status'])
                print

            dat[project] = d

        self.dat['projects'] = dat

        return


    def info_total(self):
        """
        Calculate the total number of tests, skips, failues and errors.

        """
        words = ['tests', 'skip', 'failures', 'errors']
        dat = {}
        for w in words:
            dat[w] = 0

        for v in self.dat['projects'].values():
            for w in words:
                dat[w] += v[w]

        dat['testtime'] = '%.3f sec' % (time.time() - self.time_start)

        if self.verbose:
            print 70 * '-'
            print self.format % ('Total number of tests:', dat['tests'], '')
            print

        self.dat['total'] = dat

        return


    def run_cmd(self, project):
        """
        Given the name of a project, run the test command specified in
        in self.cmd and return the command that was run and it's stdout.

        """
        project_path = os.path.join(os.getcwd(), project)

        cmd = 'cd %s; %s' % (project_path, self.cmd)
        out = commands.getoutput(cmd)

        return {'cmd': cmd, 'output': '$ %s\n%s' % (cmd, out)}


    def extract_result(self, output):
        """
        Given the output from running a test, return the number tests,
        the duration of the test in seconds, and the status,
        in a dictionary.

        """
        pat = re.compile(r'''Ran\s+(\d+)\s+tests?\s+in\s+(\d+[.]\d+)s(?:ec)?
                             \s{2,}
                             ([^\n\r]+)
                             ''', re.I | re.X)

        matches = pat.findall(output + '\n')
        if matches:
            # Get the result information from the LAST of the found matches.
            tests, sec, status = matches[-1]
        else:
            tests, sec, status = 0, 0, 'Error: could not run tests'

        return {'tests'   : int(tests),
                'testtime': '%.3f sec' % float(sec),
                'status'  : status.strip() }


    def extract_coverage(self, output):
        """
        Given the output from running a test, return the coverage
        in a dictionary.

        """
        pat = re.compile(r'-{20,}\s+TOTAL\s+\d+\s+\d+\s+(\d+)%\s+-{20,}')

        match = pat.search(output + '\n')
        if match:
            # Get the result information from the LAST of the found matches.
            cov = '%s %%' % (match.group(1))
        else:
            cov = '???'

        return {'coverage' : cov}


    def extract_from_status(self, status):
        """
        Given the status from running a test,
        return the number of skips, failures and errors, in a dictionary.

        """
        res = {}
        for word in ('skip', 'failures', 'errors'):
            match = re.search(word + r'\s*=\s*(\d+)', status, re.I)
            if match:
                res[word] = int(match.group(1))
            else:
                res[word] = 0

        return res


    def info_datetime(self):
        """
        Obtain the current date and time, and add it into self.dat.

        """
        dat = time.strftime("%Y-%m-%d %H:%M:%S %Z")

        if self.verbose:
            print 'Time of testing:', dat
            print

        self.dat['datetime'] = dat


    def info_revision(self):
        """
        Obtain current SVN revision, and add it into self.dat.

        """
        pat = re.compile(r'^revision[ ]*:[ ]*(\d+)', re.I | re.M)

        match = pat.search(commands.getoutput('svn info ETS_*'))
        if match:
            dat = int(match.group(1))
        else:
            dat = -1

        if self.verbose:
            print 'Revision:', dat
            print

        self.dat['revision'] = dat


    def info_system(self):
        """
        Obtain system information, and add it into self.dat.

        """
        import sys, platform

        dat = {'python'  : re.sub(r'\s+', ' ', sys.version),
               'environ' : dict(os.environ),
               'sys.argv': sys.argv,
               'platform': {
                   'machine'  : platform.machine(),
                   'bits'     : platform.architecture()[0],
                   'platform' : platform.platform(),
                   'processor': platform.processor(),
                   'system'   : platform.system() } }

        modules = {}
        try:
            import nose
            modules['nose'] = nose.__version__
        except ImportError:
            modules['nose'] = 'ImportError'

        try:
            import coverage
            modules['coverage'] = coverage.__version__
        except ImportError:
            modules['coverage'] = 'ImportError'

        try:
            import numpy
            modules['numpy'] = numpy.__version__
        except ImportError:
            modules['numpy'] = 'ImportError'

        try:
            import scipy
            modules['scipy'] = scipy.__version__
        except ImportError:
            modules['scipy'] = 'ImportError'

        try:
            import wx
            modules['wx'] = wx.__version__
        except ImportError:
            modules['wx'] = 'ImportError'

        dat['modules'] = modules

        if self.verbose:
            for kv in sorted(dat.items()):
                if isinstance(kv[1], str):
                    print '%s: %r' % kv

        self.dat['system'] = dat


    def store_pkl(self, filename):
        """
        Store the object self.dat into a pickle file.

        """
        import cPickle

        fo = open(filename, 'w')
        cPickle.dump(self.dat, fo)
        fo.close()


    def store_json(self, filename):
        """
        Store the object self.dat into a JSON file named filename.

        """
        import pprint

        def clean(obj):
            """
            Recursively replace quotes and doublequote with ` and ``
            in all strings occurring in the object.
            """
            if isinstance(obj, str):
                return obj.replace("'", '`').replace('"', '``')

            elif isinstance(obj, dict):
                res = {}
                for k, v in obj.iteritems():
                    res[clean(k)] = clean(v)
                return res

            elif isinstance(obj, list):
                return [clean(elt) for elt in obj ]

            elif isinstance(obj, int):
                return obj

            raise TypeError('Object %r of unexcepted type %s.' %
                            (obj, type(obj)))

        pp = pprint.PrettyPrinter(indent=2, width=20)
        json = pp.pformat(clean(self.dat)).replace("'", '"')
        fo = open(filename, 'w')
        fo.write(json)
        fo.write('\n')
        fo.close()


    def store_html(self, dirname):
        """
        Create a directory 'dirname' which contains information about
        the tests (object self.dat) in browsable form.

        Note:
          Unfortunately the code in this function is somewhat hard to read.
          Makeing the code such clearer, would require a templating engine.
          However, being about to run the handy HTML overview option without
          another dependency was important.
        """
        try:
            os.mkdir(dirname)
        except OSError:
            pass

        def htmlspecial(s):
            """
            Creates HTML entities for special characters.
            """
            for a, b in [('&',  '&amp;'), ('<',  '&lt;'), ('>',  '&gt;')]:
                s = s.replace(a, b)
            return s

        fo = open(os.path.join(dirname, 'index.html'), 'w')

        datetime = self.dat['datetime']
        revision = self.dat['revision']

        rows = []
        for proj, result in sorted(self.dat['projects'].items()):
            d = dict(result)
            d['proj'] = htmlspecial(proj)
            d['class'] = ['err', 'ok'][int(d['status'].startswith('OK'))]
            rows.append(d)

        tot_tests = self.dat['total']['tests']

        testrows = '\n'.join('''\
    <tr>
      <td><a href="%(proj)s.txt">%(proj)s</a></td>
      <td class="ar">%(tests)i</td>
      <td class="%(class)s">%(status)s</td>
    </tr>''' % d for d in rows)

        python_version = htmlspecial(self.dat['system']['python'])
        sysargv = htmlspecial(repr(self.dat['system']['sys.argv']))

        def get_table(key):
            return '<table>\n%s\n  </table>' % \
                   '\n'.join('    <tr><td>%s</td><td>%s</td></tr>' %
                             (k, htmlspecial(v)) for k, v in
                             self.dat['system'][key].items())

        modules = get_table('modules')
        platform = get_table('platform')

        fo.write('''\
<html>
<head>
  <title>ETS Test Results</title>
  <style type="text/css">
.ar { text-align: right; }
.ok { background-color: #AAFF99; }
.err { background-color: #FFAA99; }
table td { padding: .2em; color: black; background-color: #E7E7E7; }
table th { padding: .2em; color: white; background-color: #777777; }
  </style>
</head>
<body>
  <h2>ETS Tests</h2>
  <p>Time of testing: %(datetime)s</p>
  <p>Revision: %(revision)i</p>
  <table>
    <tr><th>Project</th><th>Tests</th><th>Status</th></tr>
%(testrows)s
    <tr><td>Total:</td><td class="ar">%(tot_tests)s</td></tr>
  </table>
  <h3>Test system:</h3>
  <p>%(python_version)s</p>
  <p>sys.argv = %(sysargv)s</p>

  <h4>Python modules:</h4>
  %(modules)s

  <h4>Platform:</h4>
  %(platform)s

</body>
</html>
''' % locals())
        fo.close()

        # Write the stdout in .txt files in the directory 'dirname',
        # These files linked to the project names in the table.
        for k, v in self.dat['projects'].iteritems():
            fo = open(os.path.join(dirname, '%s.txt' % k), 'w')
            fo.write(v['output'])
            fo.close()


        return
