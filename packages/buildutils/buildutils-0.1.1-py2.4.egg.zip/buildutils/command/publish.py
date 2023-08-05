"""
Publish distributables using ``sftp``/``scp``.
"""

import sys

from buildutils.cmd import Command
from distutils import log
from distutils.errors import DistutilsOptionError

def register_url_schemes():
    from urlparse import uses_relative, uses_netloc 
    uses_netloc += ['sftp', 'scp']
    uses_relative += ['sftp', 'scp']
    sys.modules[__name__].register_url_schemes = lambda : None

def parseurl(url, cache={}):
    if not cache.has_key(url):
        register_url_schemes()
        from urllib import splituser, splitpasswd, splittype, splithost, splitport
        (scheme, rest) = splittype(url)
        (host, path) = splithost(rest)
        (auth, host) = splituser(host)
        (host, port) = splitport(host)
        (user, passwd) = splitpasswd(auth)
        cache[url] = (scheme, user, passwd, host, port, path)
    return cache[url]

def handler_for_url(url):
    scheme = parseurl(url)[0]
    try:
        return publish_handlers[scheme]
    except KeyError:
        return None

def scp_handler(url, src_dir, spawn, make_dirs=0, verbose=0):
    from os.path import join
    from os import listdir
    (scheme, user, passwd, host, port, path) = parseurl(url)
    if user:
        host = '%s@%s' % (user, host)
    # preserve file times and modes
    if make_dirs:
        args = ['ssh', host, 'mkdir -p %r' % (path, )]
        spawn(args)
    files = [join(src_dir, p) for p in listdir(src_dir)]
    args = ['scp', '-rp'] + files + ['%s:%s' % (host, path)]
    spawn(args)
    
def sftp_handler(url, src_dir, spawn, make_dirs=0, verbose=0):
    import os
    from os.path import join
    (scheme, user, passwd, host, port, path) = parseurl(url)
    if user:
        host = '%s@%s' % (user, host)
    script = ['version']
    # preserve file times and modes
    if make_dirs:
        script.append('cd /')
        for part in path.split('/'):
            if part:
                script.append('-mkdir %s' % part)
                script.append('cd %s' % part)
    else:
        script.append('cd %s' % path)
    script.append('put -P %s/*' % src_dir)
    batch_file = '.buildutils-sftp-batch'
    script = '\n'.join(script)
    fo = open(batch_file, 'w')
    fo.write(script)
    fo.close()
    log.debug('sftp script:\n%s', script)
    args = ['sftp']
    if not verbose:
        args += ['-oLogLevel=QUIET']
    args += ['-b%s' % batch_file, host]
    spawn(args)
    os.unlink(batch_file)

publish_handlers = { 'scp' : scp_handler,
                     'sftp' : sftp_handler }

class publish(Command):

    description = "push distributables to a remote site."
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('dist-dir=', 'd',
                     "directory containing distributables [default: dist]."),
                    ('dist-dest=', 't',
                     "destination directory URL for distributables."),
                    ('doc-dir=', None,
                     "directory containing documentation to publish."),
                    ('doc-dest=', None,
                     "destination directory URL for documentation."),
                    ('make-dirs', 'm',
                     "try to create remote directories"),
                    ('protocol-list', None,
                     "show the list of available URL types available for "
                     "the dest arg.")]
    
    boolean_options = ['protocol-list', 'make-dirs']
    expanding_options = ['dist-dest', 'doc-dest', 'dist-dir', 'doc-dir']
    
    def initialize_options(self):
        self.dist_dest = None
        self.dist_dir = 'dist'
        self.doc_dest = None
        self.doc_dir = None
        self.make_dirs = 0
        self.protocol_list = 0
        
    def finalize_options(self):
        if self.protocol_list:
            return
        if not self.dist_dest and not self.doc_dest:
            raise DistutilsOptionError, \
                  ("Must specify a one of `dist-dest` or `doc-dest` "
                   "options (where to publish files).")
        self.expand_options()
        self.ensure_dirname('dist_dir')
        self.ensure_dirname('doc_dir')
    
    def list_protocols(self):
        if self.protocol_list:
            log.info('supported destination URL schemes: %s',
                     ', '.join(publish_handlers.keys()))
            return 1
        
    def run(self):
        # list protocols
        if self.list_protocols():
            return
        for (src, dest) in [(self.dist_dir, self.dist_dest),
                            (self.doc_dir, self.doc_dest)]:
            if not dest:
                continue
            handler = handler_for_url(dest)
            if not handler:
                raise DistutilsOptionError, \
                      'No handler available for %r URLs' % self.scheme
            self.execute(handler, (dest, src, self.spawn, self.make_dirs))
    
