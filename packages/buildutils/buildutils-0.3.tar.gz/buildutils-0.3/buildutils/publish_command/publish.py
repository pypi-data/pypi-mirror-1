"""
Publish distributables using ``sftp``/``scp``.
"""

import sys
import os
import fnmatch
import md5

from buildutils.cmd import Command
from distutils import log
from distutils.errors import DistutilsOptionError, DistutilsFileError

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

def find_files(src_dir, match):
    from os import listdir
    from os.path import join, isdir
    files = []
    for p in listdir(src_dir):
        if p == '_last_upload_signatures.txt':
            continue
        full = join(src_dir, p)
        if isdir(full):
            files.extend(find_files(full, match))
            continue
        if match:
            for pattern in match:
                if fnmatch.fnmatch(p, pattern):
                    break
            else:
                # No matches
                continue
        files.append(full)
    return files

def filter_files(file_list, file_sigs):
    """
    Given a list of filenames ``file_list``, a dictionary of
    ``{filename: (file_size, file_hash)}``, check the current size and
    hash of those files against the values in that dictionary.

    Returns (files_that_dont_match, files_in_dict_that_arent_in_list,
    new_dictionary)

    Presumably files_that_dont_match should be uploaded,
    files_in_dict_that_arent_in_list should be deleted from the remote
    server, and new_dictionary should be used next time around.
    """
    result = []
    new_sigs = {}
    extra_file = {}
    file_sigs = file_sigs.copy()
    for src_file in file_list:
        matches = True
        if src_file in file_sigs:
            last_size, last_hash = file_sigs[src_file]
            del file_sigs[src_file]
        else:
            last_size = last_hash = None
        cur_size = os.stat(src_file).st_size
        f = open(src_file, 'rb')
        cur_hash = md5.new(f.read()).hexdigest()
        f.close()
        new_sigs[src_file] = (cur_size, cur_hash)
        if last_hash != cur_hash:
            result.append(src_file)
    return result, file_sigs.keys(), new_sigs

def read_sig_dictionary(filename):
    """
    Return a dictionary of data as read from ``filename``, for use in
    ``filter_files()``
    """
    if not os.path.exists(filename):
        return {}
    result = {}
    f = open(filename, 'r')
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        src_filename, size, hash = line.split('\t')
        size = int(size)
        result[src_filename] = (size, hash)
    f.close()
    return result

def write_sig_dictionary(d, filename):
    """
    Writes a dictionary for reading by ``read_sig_dictionary``.
    """
    f = open(filename, 'w')
    for src_filename, (size, hash) in d.items():
        f.write('%s\t%s\t%s\n' % (src_filename, size, hash))
    f.close()

def scp_handler(url, src_dir, spawn, make_dirs=0, verbose=0,
                match=None, force=False):
    (scheme, user, passwd, host, port, path) = parseurl(url)
    if not path.endswith('/'):
        path = path + '/'
    if user:
        host = '%s@%s' % (user, host)
    # preserve file times and modes
    all_files = find_files(src_dir, match)
    sig_filename = os.path.join(src_dir, '_last_upload_signatures.txt')
    sig_dict = read_sig_dictionary(sig_filename)
    files, deleted_files, new_sigs = filter_files(all_files, sig_dict)
    if force:
        files = all_files
    if deleted_files:
        log.warn('These files were deleted, but probably still exist on server:')
        for filename in deleted_files:
            log.warn('  %s' % filename)
    if not all_files:
        raise DistutilsFileError(
            "No files found in %s (matching pattern(s): %s)"
            % (src_dir, match and ','.join(match) or '*'))
    if not files:
        log.info('All files up-to-date')
        return
    files_by_dir = group_files_by_dir(files, base=src_dir)
    dirlist = files_by_dir.keys()
    dirlist.sort(lambda a, b: cmp(len(a), len(b)))
    if make_dirs:
        for dir in dirlist:
            args = ['ssh', host, 'mkdir -p %r' % (path+dir, )]
            spawn(args)
    for dest_dir, file_list in files_by_dir.items():
        args = (
            ['scp', '-pC'] + file_list +
            ['%s:%s%s' % (host, path, dest_dir)])
        spawn(args)
    log.debug('Writing file signatures to %s' % sig_filename)
    write_sig_dictionary(new_sigs, sig_filename)

def group_files_by_dir(files, base):
    result = {}
    for file in files:
        assert file.startswith(base)
        rel_base = file[len(base):].lstrip(os.path.sep)
        dir = os.path.dirname(rel_base)
        result.setdefault(dir, []).append(file)
    return result
    
def sftp_handler(url, src_dir, spawn, make_dirs=0, verbose=0,
                 match=None, force=False):
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
    if match:
        print "Warning: sftp doesn't support matches"
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
                     "the dest arg."),
                    ('match=', None,
                     "Publish only files that match the given wildcard pattern"),
                    ('force', 'f',
                     'Force files to be published, even if they should be up-to-date on server'),
                    ]
    
    boolean_options = ['protocol-list', 'make-dirs']
    expanding_options = ['dist-dest', 'doc-dest', 'dist-dir', 'doc-dir']
    
    def initialize_options(self):
        self.dist_dest = None
        self.dist_dir = 'dist'
        self.doc_dest = None
        self.doc_dir = None
        self.make_dirs = 0
        self.protocol_list = 0
        self.match = []
        self.force = 0
        
    def finalize_options(self):
        if self.protocol_list:
            return
        if not self.dist_dest and not self.doc_dest:
            raise DistutilsOptionError, \
                  ("Must specify a one of `dist-dest` or `doc-dest` "
                   "options (where to publish files).")
        self.expand_options()
        if self.dist_dest:
            self.ensure_dirname('dist_dir')
        if self.doc_dest:
            self.ensure_dirname('doc_dir')
        self.ensure_string_list('match')
    
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
            self.execute(handler, (dest, src, self.spawn, self.make_dirs,
                                   0, self.match, self.force))
    
