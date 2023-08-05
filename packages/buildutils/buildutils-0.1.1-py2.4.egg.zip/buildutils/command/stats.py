"""
Dump high level code statistics.
"""

from distutils.cmd import Command
from distutils import log

class stats(Command):
    description = ("show high level statistics "
                   "(number of files, modules, packages, lines)")
    user_options = [('exclude-tests', 't',
                     "don't include modules that start with 'test_'")]
    
    def initialize_options(self):
        self.exclude_tests = 0
        
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
        modules = self.build_py.find_all_modules()
        line_counts = []
        m = Formatter()
        format = '%8s%8s%8s%8s%8s  %s'
        print format % ('lines', 'code', 'doc', 'comment', 'blank', 'file')
        print format % ((('-' * 7, ) * 5) + ('-' * 35, ))
        for (package, module, file) in modules:
            if module.startswith('test_') \
                   or package.endswith('.test') \
                   or package == 'test':
                log.debug('skipping test module: %r', file)
            try:
                fo = open(file, 'r')
            except IOError, details:
                log.error("%s: %s", details, file)
            else:
                try:
                    lines = crunch(fo.readline, file, m)
                    print format % lines
                    line_counts.append(lines)
                finally:
                    fo.close()
        totals = [0] * 5
        for lines in line_counts:
            totals = [t + n for t, n in zip(totals, lines[0:5])]
        print format % tuple(totals + ['[total]'])
        print 
        return totals
