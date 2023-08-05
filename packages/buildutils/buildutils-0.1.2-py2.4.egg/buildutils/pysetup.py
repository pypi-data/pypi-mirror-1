#!/usr/bin/env python
"""
Buildutils command line utility (pbu)

The `main` method is invoked by the ``pbu`` wrapper script. For more
information about the ``pbu`` command, see the `User's Guide`_.

.. _User's Guide: guide.html#pbu

"""

import sys
import os
import os.path as path

from distutils import log
log.set_verbosity(1)
config_files = ['~/pydistutils.cfg', '~/.pydistutils.cfg',
                '~/pbu.cfg',
                'setup.cfg']
config = {}


def find_setup_py():
    log.debug("pbu: looking for 'setup.py'")
    cwd = os.getcwd()
    last = None
    while not path.exists(path.join(cwd, 'setup.py')):
        cwd = path.dirname(cwd)
        if not cwd or cwd == last:
            return None
        last = cwd
    setup_py = path.join(cwd, 'setup.py')
    log.debug("pbu: found %r" % setup_py)
    return setup_py

def parse_config(filenames=config_files):
    from ConfigParser import ConfigParser
    parser = ConfigParser()
    global config
    for filename in filenames:
        filename = path.expanduser(path.normpath(filename))
        if not path.exists(filename):
            continue
        log.debug('pbu: reading config %r', filename)
        parser.read(filename)
        if parser.has_section('pbu'):
            for n, v in parser.items('pbu'):
                config[n] = v
        parser.__init__()

def parse_argv(argv=sys.argv):
    """Look for --interpreter argument."""
    i = 1
    interpreter = ''
    while len(argv) > i:
        arg = argv[i]
        if not arg.startswith('-'):
            break
        elif arg in ('-q', '--quiet'):
            log.set_verbosity(0)
        elif arg in ('-v', '--verbose'):
            log.set_verbosity(2)
        elif arg.startswith('-i'):
            value = arg[2:]
            if not value and len(argv) >= i+1:
                value = argv[i+1]
                del argv[i+1]
            del argv[i]
            interpreter = value
            continue
        elif arg.startswith('--interpreter='):
            value = arg[len('--interpreter='):]
            del argv[i]
            continue
        i+= 1
    return interpreter and interpreter.strip("'\" \t\r\n")

if os.name == 'nt':
    def find_python(version):
        paths = ['C:\\Python%d.%d',
                 'C:\\Python%d%d',
                 'C:\\Program Files\\Python%d.%d',
                 'C:\\Program Files\\Python%d%d']
        for p in paths:
            p = path.join(p % version, 'python.exe')
            if path.exists(p):
                return p
elif path.exists('/Library/Frameworks/Python.framework'):
    # os x
    def find_python(version):
        p = '/Library/Frameworks/Python.framework/Versions/%d.%d/bin/python'\
            % version
        if path.exists(p):
            return p
else:
   def find_python(version):
       return None

def find_interpreters(versions):
    # fast path no version specified to use the current executable
    if not versions:
        return [sys.executable]
    interpreters = []
    from distutils.spawn import find_executable
    def parse_version(version):
        if '.' in version:
            major, minor = version.split('.', 1)
            try:
                major, minor = int(major), int(minor)
            except ValueError:
                pass
            else:
                return (major, minor)
        bail('pbu: bad interpreter version specifier: %r' % versions)
    def add_version(version):
        if isinstance(version, tuple):
            a, i = version
            python = 'python%d.%d' % (a, i)
            if config.has_key(python):
                cmd = find_executable(config[python])
            else:
                cmd = find_executable('python%d.%d' % (a, i))
            if not cmd:
                cmd = find_python((a, i))
        else:
            cmd = find_executable(version)
        if cmd:
            interpreters.append(cmd)
        else:
            log.info('pbu: no interpreter found for %r', version)
    for v in map(str.lower, versions.split(',')):
        if '/' in v or '\\' in v or v.startswith('python'):
            add_version(v)
        elif '-' in v:
            first, last = map(parse_version, v.split('-', 1))
            for j in range(first[1], last[1]+1):
                add_version((first[0], j))
        else:
            add_version(parse_version(v))
    return interpreters
    
def bail(msg=None, code=1):
    if msg:
        log.error(msg + '\n')
    sys.exit(code)

def main():
    versions = parse_argv()
    setup_py = find_setup_py()
    if not setup_py:
        bail('setup.py not found in this directory or parent directories.')
    setup_dir = path.dirname(setup_py)
    os.chdir(setup_dir)
    parse_config()
    interpreters = find_interpreters(versions)
    from distutils.spawn import spawn
    from distutils.errors import DistutilsExecError
    run = ';'.join(["import sys",
                    "sys.argv[0] = 'setup.py'",
                    "import buildutils",
                    "__file__ = 'setup.py'",
                    "execfile(__file__)"])
    args = [None, '-c', run] + sys.argv[1:]
    rslt = 0
    for i in interpreters:
        args[0] = i
        log.info('pbu: using %s', i)
        log.debug('pbu: %r', ' '.join(args))
        old = log.set_threshold(log.WARN)
        try:
            spawn(args, search_path=0, verbose=0)
        except DistutilsExecError, e:
            log.error(str(e))
            rslt = 1
        log.set_threshold(old)
    bail(code=rslt)
    
if __name__ == '__main__':
    main()
