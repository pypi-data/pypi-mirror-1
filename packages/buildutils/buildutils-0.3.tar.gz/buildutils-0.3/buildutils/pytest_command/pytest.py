"""
Run a suite of ``py.test`` based unit tests.
"""

import os

from distutils import log
from buildutils.cmd import Command

class pytest(Command):
    description = "run py.test unit tests."
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('tests=', 't',
                     "list of directories/files containing tests."),
                    ('exitfirst', 'x',
                     "exit instantly on first error or failed test."),
                    ('no-capture', 's',
                     "disable catching of sys.stdout/stderr output."),
                    ('showlocals', 'l',
                     "show locals in tracebacks."),
                    ('pdb', None,
                     "start pdb (The Python Debugger) on errors."),
                    ('fulltrace', None,
                     "don't cut any tracebacks (default is to cut)"),
                    ('no-magic', None,
                     "refrain from using magic as much as possible"),
                    ('collectonly', None,
                     "show what tests are collected but do not run them."),
                    ('traceconfig', None,
                     "trace considerations of conftest.py files"),
                    ('tkinter', None,
                     "use tkinter test session frontend."),
                    ('looponfailing', 'f',
                     "loop on failing test set.")]
    
    boolean_options = ['exitfirst', 'no-capture', 'showlocals', 'pdb',
                       'fulltrace', 'no-magic', 'collectonly', 'traceconfig',
                       'tkinter', 'looponfailing']
    expanding_options = ['tests']
    
    def initialize_options(self):
        self.tests = None
        self.exitfirst = 0
        self.no_capture = 0
        self.showlocals = 0
        self.pdb = 0
        self.fulltrace = 0
        self.no_magic = 0
        self.collectonly = 0
        self.traceconfig = 0
        self.tkinter = 0
        self.looponfailing = 0
        self.versions = [None]
        
    def finalize_options(self):
        self.ensure_string_list('tests')
        self.expand_options()
        if not self.tests:
            self.tests = self.get_default_tests()
        
    def get_default_tests(self):
        from glob import glob
        tests = glob('test*.py')
        tests += glob('test/*test*.py')
        dist = self.distribution
        for p in dist.packages:
            if '.' in p or p == 'test' or p.startswith('test.'):
                # we should pick these up elsewhere
                continue
            if dist.package_dir and dist.package_dir.has_key(p):
                p = dist.package_dir[p]
            else:
                p = p.replace('.', os.sep)
            tests.append(p)
        return tests
    
    def run(self):
        #self.require('py')
        import py
        argv = []
        for (lopt, sopt, desc) in self.user_options:
            if lopt.endswith('='):
                lopt = lopt[0:-1]
            lopt = lopt.replace('-', '_')
            if lopt == 'tests':
                continue
            val = getattr(self, lopt)
            if lopt.replace('_', '-') in self.boolean_options:
                if val != 0:
                    argv.append('--%s' % lopt.replace('_', ''))
            else:
                val = getattr(self, lopt)
                if val is not None:
                    argv.append('--%s=%s' % (lopt.replace('_', ''), val))
        versions = self.versions or [None]
        baseargv = argv
        for ver in versions:
            argv = baseargv[:]
            if ver is not None:
                argv.append('--exec=python%s' % ver)
            if self.tests:
                argv += self.tests
            log.debug('executing py.test %s', ' '.join(argv))
            config, args = py.test.Config.parse(argv)
            config.option.verbose = self.verbose
            sessionclass = config.getsessionclass()
            session = sessionclass(config)
            try: 
                failures = session.main(args)
                if failures: 
                    raise SystemExit, 1 
            except KeyboardInterrupt: 
                if not config.option.verbose: 
                    print
                    print "KeyboardInterrupt"
                    raise SystemExit, 2
                else:
                    raise
