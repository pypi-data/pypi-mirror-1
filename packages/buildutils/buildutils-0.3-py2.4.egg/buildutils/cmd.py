"""
Command base class providing enhancements to `distutils.cmd`
"""

import sys
import os
import distutils.cmd
from string import Template

from distutils import log

class Command(distutils.cmd.Command):
    """
    Provides some extra functionality on top of the base
    `distutils.cmd.Command` class.
    """

    expanding_options = []
    
    def get_metadata_dict(self, **extra):
        """
        Return a dictionary containing the distibution metadata.
        
        The values in this dictionary are available during option
        expansion.
        """
        if not hasattr(self.distribution, '_metadata_dict'):
            m = {}
            dist = self.distribution
            for basename in dist.metadata._METHOD_BASENAMES:
                method_name = "get_" + basename
                m[basename] = getattr(dist, method_name)()
            dist._metadata_dict = m
        rslt = dist._metadata_dict.copy()
        if extra:
            rslt.update(extra)
        return rslt
        
    def expand_options(self, options=None, **extra):
        """
        Expand any of the options listed in `expanding_options`,
        filling in values from the distribution metadata.  The options use
        `string.Template` dollar substitution, like ``$author``
        """
        if options is None:
            options = self.expanding_options
        if isinstance(options, (str, unicode)):
            options = [options]
        else:
            assert isinstance(options, (list, tuple)), \
                   "options must be a string or sequence type"
        m = self.get_metadata_dict(**extra)
        for o in options:
            o = o.replace('-', '_')
            orig = getattr(self, o)
            if isinstance(orig, (str, unicode)):
                new = Template(orig).substitute(m)
            elif isinstance(orig, list):
                new = []
                for val in orig:
                    new.append(Template(val).substitute(m))
            elif orig is None:
                continue
            if new != orig:
                log.debug('expanded option %r: %r -> %r', o, orig, new)
                setattr(self, o, new)
    
    def find_files(self, include=['*'], exclude=[], basedir=None):
        from distutils.filelist import FileList
        from os.path import join
        basedir = basedir or os.curdir
        ls = FileList()
        ls.findall(basedir)
        if '*' in include:
            ls.files = ls.allfiles
        else:
            for p in include:
                ls.include_pattern(p, 0)
            ls.sort()
            ls.remove_duplicates()
        for p in exclude:
            ls.exclude_pattern(p, 0)
        files = ls.files
        if basedir:
            for i, p in zip(range(len(files)), files):
                files[i] = files[i][len(basedir)+1:]
        return files
    
    def require(self, dependencies, auto=1):
        """
        Require dependencies.
        """
        from pkg_resources import require, DistributionNotFound
        missing = []
        if isinstance(dependencies, (str, unicode)):
            dependencies = [dependencies]
        for dep in dependencies:
            try:
                require(dep)
            except DistributionNotFound, e:
                log.error('Missing dependency: %s' % dep)
                missing.append(dep)
        def bail():
            log.info("You may be able to install the dependencies using the following command:\n"
                         "easy_install.py '%s'", "' '".join(missing))
            raise SystemExit(1)
        if missing:
            if not auto:
                bail()
            answer = raw_input('Dependencies are missing. Try to install them? [Y/n] ')
            if answer in ('', 'Y', 'y'):
                self.easy_install(missing)
                self.require(missing, auto=0)
            else:
                bail()
        
    def easy_install(self, dependencies):
        log.info('installing dependencies: %r', dependencies)
        from setuptools.command.easy_install import easy_install
        from setuptools import setup
        setup(cmdclass={ 'easy_install' : easy_install },
              script_args=['-q', 'easy_install', '-v'] + list(dependencies))

    def write_file(self, name, contents):
        """
        Write a file respecting dry-run
        """
        if not os.path.exists(name):
            log.info("creating %s" % name)
        else:
            f = open(name, 'r')
            c = f.read()
            f.close()
            if c == contents:
                log.info("%s unchanged" % name)
                return
            else:
                log.info("writing %s" % name)
        if self.dry_run:
            return
        f = open(name, 'w')
        f.write(contents)
        f.close()
        
