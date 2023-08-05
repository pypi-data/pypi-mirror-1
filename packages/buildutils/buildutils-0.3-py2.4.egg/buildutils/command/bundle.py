import os
import sys
import shutil
import glob
from distutils import log
from distutils.cmd import Command
from distutils.errors import DistutilsSetupError
from setuptools.command import easy_install
import pkg_resources
import zipfile

ACTIVATE_EGGS = '''\
"""
execing this file (make sure to set __file__!) activates the eggs on this path
"""
import os
import sys
import pkg_resources
import site
here = os.path.dirname(os.path.abspath(__file__))
for fn in os.listdir(here):
    fn = os.path.join(here, fn)
    for dist in pkg_resources.find_distributions(fn, True):
        cur_dist = pkg_resources.working_set.by_key.get(dist.project_name)
        if cur_dist is not None:
            sys.path.remove(cur_dist.location)
            del pkg_resources.working_set.by_key[dist.project_name]
        pkg_resources.working_set.add(dist)
site.addsitedir(here)
'''

class bundle(Command):

    description = "Create a bundle from this package"

    # list of (long_name, short_name, description)
    user_options = [
        ('extra-requirements=', None, 'Any extra requirements you want installed as part of the bundle'),
        ]

    def initialize_options(self):
        if os.environ.get('WORKING_ENV'):
            # This isn't really compatible with workingenv.py
            raise DistutilsSetupError(
                "bdist_olpc_bundle is not compatible with an activated workingenv.py; please deactivate (and unset WORKING_ENV) before running this command")
        self.extra_requirements = None

    def finalize_options(self):
        if not self.extra_requirements:
            self.extra_requirements = []
        else:
            self.extra_requirements = self.extra_requirements.split()

    def run(self):
        dist = self.distribution
        log.info('Running egg_info/bdist_egg (creating egg)')
        #egg_info_cmd = self.get_finalized_command('egg_info')
        bundle_dir = os.path.join('dist', dist.metadata.name)
        bdist_egg_cmd = self.get_finalized_command('bdist_egg')
        bdist_egg_cmd.run()
        # This comes from pkg_resources; is it available here?
        self.dist_dir = bdist_egg_cmd.dist_dir
        egg_filename = bdist_egg_cmd.egg_output
        self.pkg_dist = pkg_resources.Distribution.from_location(egg_filename, os.path.basename(egg_filename))
        self.bundle_dir = os.path.splitext(egg_filename)[0] + '.bundle'
        if os.path.exists(self.bundle_dir):
            log.warn('Removing previous bundle in %s' % self.bundle_dir)
            shutil.rmtree(self.bundle_dir)
        os.mkdir(self.bundle_dir)
        egg_dir = os.path.join(self.bundle_dir, 'eggs')
        os.mkdir(egg_dir)
        bin_dir = os.path.join(self.bundle_dir, 'bin')
        os.mkdir(bin_dir)
        self.install_requirements(
            self.pkg_dist, egg_dir, bin_dir)
        self.bundle_zip = self.bundle_dir + '.zip'
        if os.path.exists(self.bundle_zip):
            log.warn('Removing old %s' % self.bundle_zip)
            os.unlink(self.bundle_zip)
        self.zip_bundle()

    def install_requirements(self, pkg_dist, egg_dir, bin_dir):
        # FIXME: should I use --record somehow?
        global patch_easy_install
        prev_on = egg_dir in sys.path
        if not prev_on:
            # easy_install gets whiny about installing somewhere
            # that isn't on the path:
            sys.path.append(egg_dir)
        easy_args = [
            '--upgrade', '--install-dir', egg_dir, '--script-dir', bin_dir,
            '-v', '--always-copy', '--always-unzip',
            '--local-snapshots-ok',
            '--site-dirs', egg_dir]
        log.info('Running easy_install %s %s' % (' '.join(easy_args), pkg_dist.location))
        patch_easy_install = True
        ## FIXME: all this commented-out stuff doesn't actually work
        ## it should keep easy_install from seeing existing packages here
        #old_working_set = pkg_resources.working_set
        #old_sys_path = list(sys.path)
        #self.trim_sys_path()
        try:
            #pkg_resources.working_set = pkg_resources.WorkingSet()
            easy_install.main(easy_args + [pkg_dist.location])
            for req in self.extra_requirements:
                log.info('Running easy_install %s %s'
                         % (' '.join(easy_args), req))
                easy_install.main(easy_args + [req])
        finally:
            #pkg_resources.working_set = old_working_set
            #sys.path = old_sys_path
            patch_easy_install = False
        if not prev_on:
            sys.path.remove(egg_dir)
        active_fn = os.path.join(egg_dir, 'activate-eggs.py')
        f = open(active_fn, 'w')
        f.write(ACTIVATE_EGGS)
        f.close()

    def trim_sys_path(self):
        for item in list(sys.path):
            if item.endswith('.egg'):
                if (not item.startswith('buildutils')
                    and not item.startswith('setuptools')):
                    sys.path.remove(item)
            else:
                if glob.glob(os.path.join(item, '*.egg-info')):
                    sys.path.remove(item)

    def zip_bundle(self):
        log.info('Writing zip file %s' % self.bundle_zip)
        zip_f = zipfile.ZipFile(self.bundle_zip, 'w', zipfile.ZIP_DEFLATED)
        base = os.path.abspath(self.bundle_dir)
        for dirpath, dirnames, filenames in os.walk(base):
            for filename in filenames:
                full = os.path.join(dirpath, filename)
                partial = full[len(base):]
                log.debug('Adding %s as %s' % (full, partial))
                zip_f.write(full, partial)
        zip_f.close()

normal_get_script_header = easy_install.get_script_header
patch_easy_install = False
                         
def patched_get_script_header(script_text, executable=easy_install.sys_executable, wininst=False):
    if not patch_easy_install:
        return normal_script_header(script_text, executable, wininst)
    from distutils.command.build_scripts import first_line_re
    first, rest = (script_text+'\n').split('\n',1)
    match = first_line_re.match(first)
    options = ''
    if match:
        script_text = rest
        options = match.group(1) or ''
        if options:
            options = ' '+options
    #if options.find('-S') == -1:
    #    options += ' -S'
    shbang = "#!%s%s\n" % (executable, options)
    shbang += ("import os\n"
               "egg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'eggs')\n"
               "active_fn = os.path.join(egg_dir, 'activate-eggs.py')\n"
               "execfile(active_fn, {'__file__': active_fn})\n"
               )
    return shbang

easy_install.get_script_header = patched_get_script_header

