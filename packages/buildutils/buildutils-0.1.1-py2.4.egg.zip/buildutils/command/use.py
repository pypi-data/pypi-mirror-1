"""
Use a development version of another project.
"""

import os

from distutils import log
from buildutils.cmd import Command

class use(Command):
    description = "use a development version of another project."
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('devel-dir=', 'd',
                     "list of directories containing development projects."),
                    ('projects=', 'p',
                     "list of projects that should be used."),
                    ('scripts-to=', 's',
                     "put wrapper scripts in this directory "
                     "[default: .]"),
                    ('eggs-to=', 'e',
                     "put eggs in this directory [default: .]"),
                    ('stop', 'x',
                     "stop using the projects specified.")]
    
    boolean_options = ['stop']
    expanding_options = ['devel-dir', 'projects']
    
    def initialize_options(self):
        self.devel_dir = ['~/devel', '~/projects', '~/src']
        self.projects = []
        self.scripts_to = '.'
        self.eggs_to = '.'
        self.stop = 0
        
    def finalize_options(self):
        self.ensure_string_list('devel_dir')
        self.ensure_string_list('projects')
        self.ensure_string('scripts_to')
        self.ensure_string('eggs_to')
        # figure out development dirs
        from os.path import normpath, expanduser, exists
        self.expand_options()
        dirs = []
        for x in self.devel_dir:
            x = normpath(expanduser(x))
            if exists(x):
                dirs.append(x)
            else:
                log.debug('ignoring non-existant directory: %r', x)
        self.devel_dir = dirs
        
    def get_projects(self):
        from os.path import join, exists
        for p in self.projects:
            for x in self.devel_dir:
                project_dir = join(x, p)
                if exists(project_dir):
                    yield project_dir
                    break
            else:
                log.error('project not found: %r' % p)

    def develop(self, project_dir, unlink=0):
        from os.path import abspath, join, normpath
        this_dir = abspath(os.getcwd())
        egg_dir = normpath(join(this_dir, self.eggs_to))
        scripts_dir = normpath(join(this_dir, self.scripts_to))
        filename = join(project_dir, 'setup.py')
        args = ['develop', '-m',
                '--install-dir=%s' % egg_dir,
                '--script-dir=%s' % scripts_dir]
        if unlink:
            args.append('--uninstall')
        def run_develop():
            os.chdir(project_dir)
            from distutils.core import run_setup
            try:
                return run_setup('setup.py', args)
            finally:
                os.chdir(this_dir)
        self.execute(run_develop, (),
                     msg='%sing: %s' % (unlink and 'unlink' or 'link',
                                        project_dir))
        
    def use(self):
        from os.path import split, exists, join
        for p in self.get_projects():
            dist = self.develop(p)
    
    def unuse(self):
        for p in self.get_projects():
            dist = self.develop(p, unlink=1)
        
    def run(self):
        (self.stop and self.unuse or self.use)()
    
