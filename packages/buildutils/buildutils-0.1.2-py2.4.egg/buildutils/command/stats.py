"""
Dump high level code statistics.
"""

from distutils.cmd import Command
from distutils import log
import re

class stats(Command):
    description = ("show high level statistics "
                   "(number of files, modules, packages, lines)")
    user_options = [('exclude-tests', 't',
                     "don't include modules that start with 'test_'"),
                    ('extra-packages=', 'p',
                     "Also count code from the given packages"),
                    ('totals', None,
                     "Show only the totals"),
                    ]
    
    def initialize_options(self):
        self.exclude_tests = 0
        self.extra_packages = ''
        self.totals = 0
        
    def finalize_options(self):
        pass
        
    def run(self):
        # we use the build_py command because it provides a bunch
        # of functionality for resolving module names and whatnot
        from distutils.command.build_py import build_py
        base = build_py(self.distribution)
        base.initialize_options()
        base.finalize_options()
        self.build_py = base
        self.dump_stats()
        
    def dump_stats(self):
        package_count = len(self.distribution.packages or [])
        module_count = len(self.build_py.find_all_modules())
        package_s = package_count > 1 and 's' or ''
        module_s = module_count > 1 and 's' or ''
        totals = self.dump_line_counts()
        line_count = totals[1]
        print('%d lines of code, %d module%s, %d package%s.'
              % (line_count, module_count, module_s, package_count,
                 package_s))
        
    def dump_line_counts(self):
        # bring in pycount for some statistics
        from buildutils.pycount import crunch, Formatter
        dist = self.distribution
        if self.extra_packages:
            mods = self.extra_packages.split(',')
            if self.build_py.packages is not None:
                self.build_py.packages.extend(mods)
            else:
                self.build_py.packages = mods
        modules = self.build_py.find_all_modules()
        modules.sort(lambda a, b: cmp(a[2], b[2]))
        line_counts = []
        test_line_counts = []
        m = Formatter()
        format = '%8s%8s%8s%8s%8s  %s'
        format_test = '%8s%8s%8s%8s%8s  %s *'
        print format % ('lines', 'code', 'doc', 'comment', 'blank', 'file')
        print format % ((('-' * 7, ) * 5) + ('-' * 35, ))
        for (package, module, file) in modules:
            is_test = 0
            if testing_module(module) or testing_module(package):
                if self.exclude_tests:
                    log.debug('skipping test module: %r', file)
                    continue
                is_test = 1
            try:
                fo = open(file, 'r')
            except IOError, details:
                log.error("%s: %s", details, file)
            else:
                try:
                    lines = crunch(fo.readline, file, m)
                    if not self.totals:
                        if is_test:
                            print format_test % lines
                        else:
                            print format % lines
                    line_counts.append(lines)
                    if is_test:
                        test_line_counts.append(lines)
                finally:
                    fo.close()
        totals = [0] * 5
        for lines in line_counts:
            totals = [t + n for t, n in zip(totals, lines[0:5])]
        print format % tuple(totals + ['[total]'])
        if test_line_counts:
            test_code = sum([l[1] for l in test_line_counts])
            all_code = sum([l[1] for l in line_counts])
            other_code = all_code-test_code
            print 'Test code: %s  other code: %s  ratio: %s code to tests' % (
                test_code, other_code, ratio_string(test_code, other_code))
        print 
        return totals

def ratio_string(a, b):
    """
    Format the ratio of a:b
    """
    if a > b:
        a, b = float(b) / float(a), 1
    else:
        a, b = 1, float(a) / float(b)
    return '%s:%s' % (format_float(a), format_float(b))

def format_float(f):
    if f == int(f):
        return str(f)
    if f < 0.1:
        return '%0.2f' % f
    else:
        return '%0.1f' % f

def testing_module(mod_name):
    """
    Is the named module considered a test?
    """
    # If the module name has .test[s]., or .tests_* in it (roughly)
    # then it is considered a test module:
    return re.search(r'\btests?\b|\btest_', mod_name)
