"""
Command Template
"""

import re
import os
from distutils import log
from buildutils.cmd import Command
from distutils.errors import *

name_re = re.compile(r'^[a-z][a-z0-9_]*$', re.I)

class customcommand(Command):
    description = "Start a custom command for this project"
    
    # list of ("long-name=?" (= for commands that take an argument), "s" (short name), description) tuples
    user_options = [
        ('name=', 'c', 'Name of the new command'),
        ('package=', 'p', 'Package for the command (default: .command)'),
        ]

    # list of ["long-name"] options that take no arguments
    boolean_options = []
    

    def initialize_options(self):
        self.name = None
        self.package = '.command'

    def finalize_options(self):
        # raise DistutilsOptionError if a problem
        if not self.name:
            raise DistutilsOptionError(
                "You must give a --name option")
        if not name_re.search(self.name):
            raise DistutilsOptionError(
                "The command name must start with a letter and contain only letters, numbers, and _ (you gave: %r)" % self.name)
        if self.package.startswith('.'):
            self.resolve_package()

    def resolve_package(self):
        extra = self.package
        current_pkgs = list(self.distribution.packages)
        current_pkgs.sort(lambda a, b: cmp(len(a), len(b)))
        base = current_pkgs[0]
        self.package = base + extra

    def run(self):
        dir = self.make_package()
        command_fn = os.path.join(dir, self.name+'.py')
        template_fn = os.path.join(os.path.dirname(__file__), 'command_template')
        f = open(template_fn)
        content = f.read()
        f.close()
        content = content.replace('COMMAND_NAME', self.name)
        self.write_file(command_fn, content)
        cmd_obj = self.distribution.get_command_obj('addcommand')
        cmd_obj.package = self.package
        cmd_obj.force = True
        cmd_obj.ensure_finalized()
        cmd_obj.run()
        log.info('Edit %s to create your command' % template_fn)

    def make_package(self):
        pkg_name = self.package
        base = self.distribution.package_dir or '.'
        pkg_name = pkg_name.replace('.', os.path.sep)
        dirname = os.path.join(base, pkg_name)
        if not os.path.exists(dirname):
            self.mkpath(dirname)
            self.write_file(os.path.join(dirname, '__init__.py', '#'))
        return dirname
