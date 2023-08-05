"""
Command Template
"""

import sys
import os
import types
from distutils import log
from buildutils.cmd import Command
from distutils.cmd import Command as DistutilsCommand
from distutils.errors import *
from setuptools.command.setopt import edit_config, option_base

class addcommand(option_base):
    description = "Make a command available to this project"
    
    # list of (long name, short name, description) tuples
    user_options = [
        ('package=', 'p', 'Module of the command you want to add'),
        ('list-commands', 'l', 'List available commands'),
        ('force', 'f', 'Force it to succede'),
        ] + option_base.user_options
    
    boolean_options = ['list-commands', 'force'] + option_base.boolean_options

    def initialize_options(self):
        self.package = None
        self.list_commands = False
        self.force = False
        option_base.initialize_options(self)
    
    def finalize_options(self):
        if not self.list_commands and not self.force:
            self.check_command()
        option_base.finalize_options(self)

    def check_command(self):
        pkg_name = self.package
        if not self.package:
            raise DistutilsOptionError(
                "You must provide a --package option")
        try:
            pkg = self.import_module(pkg_name)
        except ImportError, e:
            log.debug("Error while importing %s: %s"
                      % (pkg_name, e))
            raise DistutilsOptionError(
                "There is no module with the name %r" % pkg_name)
        filename = pkg.__file__
        if not os.path.splitext(os.path.basename(filename))[0] == '__init__':
            raise DistutilsOptionError(
                "The command package %s is a module; you must give the package name" % pkg_name)
        dirname = os.path.dirname(pkg.__file__)
        found = False
        problems = []
        def debug(message):
            log.debug(message)
            problems.append(message)
        for command_name in self.sub_modules(pkg):
            if command_name == '__init__':
                continue
            mod_name = pkg_name + '.' + command_name
            try:
                mod = self.import_module(mod_name)
            except ImportError, e:
                debug(
                    "Could not import %s: %s"
                    % (mod_name, e))
                continue
            try:
                cls_obj = getattr(mod, command_name)
            except AttributeError, e:
                debug(
                    "Module %s has no %s attribute"
                    % (mod_name, command_name))
                continue
            if (not isinstance(cls_obj, types.ClassType)
                or not issubclass(cls_obj, DistutilsCommand)):
                debug(
                    "Class %s.%s is not a subclass of distutils.cmd.Command" % (mod_name, command_name))
                continue
            found = True
        if not found:
            err = "The command package %s contains no commands" % pkg_name
            for item in problems:
                err += "\n" + item
            raise DistutilsOptionError(err)

    def sub_modules(self, module):
        dirname = os.path.dirname(module.__file__)
        subs = []
        for filename in os.listdir(dirname):
            if not filename.endswith('.py'):
                continue
            subs.append(os.path.splitext(os.path.basename(filename))[0])
        return subs

    def import_module(self, mod_name):
        assert isinstance(mod_name, basestring), (
            "Bad value for mod_name: %r" % mod_name)
        __import__(mod_name)
        return sys.modules[mod_name]
    
    def run(self):
        if self.list_commands:
            return self.run_list_commands()
        dist = self.distribution
        cur_setting = []
        for opt, (src, val) in dist.get_option_dict('global').items():
            if src != self.filename:
                continue
            if opt == 'command_packages':
                cur_setting.extend(self.split(val))
        if self.package in cur_setting:
            if not self.force:
                raise DistutilsOptionError(
                    "The package %s is already listed in %s"
                    % (self.package, self.filename))
            else:
                log.debug(
                    "The package %s is already listed in %s"
                    % (self.package, self.filename))
                return
        cur_setting.append(self.package)
        settings = {'global': {'command_packages': ', '.join(cur_setting)}}
        edit_config(self.filename, settings, self.dry_run)

    def split(self, value):
        return [
            v.strip()
            for v in value.split(',')
            if v.strip()]

    def run_list_commands(self):
        import pkg_resources
        print '[buildutils.optional_commands]'
        for ep in pkg_resources.iter_entry_points('buildutils.optional_commands'):
            mod_name = ep.module_name
            pkg = ep.load()
            header = 'Package %s' % mod_name
            print header
            print '-'*len(header)
            commands = self.find_commands(mod_name)
            if not commands:
                print '  (no commands found)'
            else:
                for cmd in commands:
                    print '  %s:' % cmd.__name__
                    print '    %s' % cmd.description
            print
        print "Other commands may be available (but they aren't listed)"
        print 'Use "python setup.py addcommand -p PACKAGE" to make one of these available in this project'

    def find_commands(self, pkg_mod_name):
        pkg_mod = self.import_module(pkg_mod_name)
        cmds = []
        for mod_name in self.sub_modules(pkg_mod):
            if mod_name == '__init__':
                continue
            full_name = pkg_mod_name + '.' + mod_name
            try:
                mod = self.import_module(full_name)
            except ImportError, e:
                log.info(
                    "Cannot load %s: %s" % (full_name, e))
                continue
            try:
                cmd = getattr(mod, mod_name)
            except AttributeError:
                log.debug(
                    "Module %s contains no %s attribute"
                    % (full_name, mod_name))
            cmds.append(cmd)
        return cmds
