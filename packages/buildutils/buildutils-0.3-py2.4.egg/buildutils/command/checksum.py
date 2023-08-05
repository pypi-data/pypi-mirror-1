"""
Create MD5 and/or SHA checksum files for distributables.
"""
import os.path as path

from buildutils.cmd import Command
from distutils import log

bufsize = (2 ** 13)  # 8K blocks

def file_checksum(file, algorithm):
    m = algorithm.new()
    fo = open(file, 'r')
    try:
        buf = fo.read(bufsize)
        while buf:
            m.update(buf)
            buf = fo.read(bufsize)
    finally:
        fo.close()
    return m.hexdigest()
    
def md5_checksum(file):
    import md5
    return file_checksum(file, md5)
    
def sha_checksum(file):
    import sha
    return file_checksum(file, sha)

class checksum(Command):
    description = "create md5 and/or sha checksum files for distributables."
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('dist-dir=', 'd',
                    "directory where distribution archive(s) live."),
                    ('per-file', 'p',
                     "generate a checksum file for each distributable instead of putting all checksums in a single file."),
                    ('sha', None,
                     "generate SHA-1 checksums (default)"),
                    ('no-sha', 's',
                     "don't generate SHA-1 checksums"),
                    ('md5', 'm',
                     "generate MD5 checksums"),
                    ('no-md5', None,
                     "don't generate MD5 checksums."),
                    ('force', 'f',
                     "force generation of checksum files even if they "
                     "exist and are up to date"),
                    ('sign', None,
                     "generate signed versioned of checksum files using gpg "
                     "(note: you must have gnupg and a secret key.")]
    
    boolean_options = ['sha', 'md5', 'force', 'sign']
    negative_opt = {'no-sha' : 'sha',
                    'no-md5': 'md5'}
    
    def initialize_options(self):
        self.dist_dir = 'dist'
        self.dist_extensions = ['*.tar', '*.tar.gz', '*.tar.bz', '*.tgz',
                                '*.zip', '*.tar.Z', '*.egg', '*.exe', '*.rpm']
        self.sha = 1
        self.md5 = 0
        self.per_file = 0
        self.sign = 0
        
    def finalize_options(self):
        self.ensure_string_list('dist_extensions')
        self.ensure_dirname('dist_dir')
        dist_files = self.find_files(basedir=self.dist_dir,
                                     include=self.dist_extensions)
        log.debug('checksum found %d files: %r' % (len(dist_files),
                                                   dist_files))
        self.dist_files = dist_files
    
    def run(self):
        if self.sha:
            import sha
            self.generate_checksums(sha)
        if self.md5:
            import md5
            self.generate_checksums(md5)
                
    def generate_checksums(self, algorithm):
        checksums = []
        algorithm_name = algorithm.__name__
        dist_dir = self.dist_dir
        for f in self.dist_files:
            full_path = path.join(self.dist_dir, f)
            digest = file_checksum(full_path, algorithm)
            checksums.append((digest, f))
            log.info('%s checksum: %s  %s' % (algorithm_name.upper(),
                                              digest, f))
            if self.per_file:
                checksum_file = '%s.%s' % (full_path, algorithm_name)
                def write_checksum():
                    fo = open(checksum_file, 'w')
                    fo.write('%s  %s\n' % (digest, f))
                    fo.close()
                self.make_file(full_path, checksum_file,
                               write_checksum, (),
                               exec_msg='checksum written to %r' % checksum_file)
                if self.sign:
                    signed_file = checksum_file + '.asc'
                    self.make_file(checksum_file, signed_file,
                                   self.spawn, (['gpg', '--clearsign',
                                                 checksum_file],),
                                   exec_msg='signing checksum file...')
                
        if not self.per_file:
            checksum_file = '%s.%s' % (self.distribution.get_fullname(),
                                                 algorithm_name)
            checksum_file = path.join(self.dist_dir, checksum_file)
            def write_file():
                fo = open(checksum_file, 'w')
                fo.write('\n'.join(['%s  %s' % c for c in checksums]))
                fo.write('\n')
                fo.close()
            inputs = [path.join(self.dist_dir, c[1]) for c in checksums]
            self.make_file(inputs, checksum_file,
                           write_file, (),
                           exec_msg='checksums written to %r' % checksum_file)
            if self.sign:
                signed_file = checksum_file + '.asc'
                self.make_file(checksum_file, signed_file,
                               self.spawn, (['gpg', '--clearsign',
                                             checksum_file],),
                               exec_msg='signing checksum file...')
            
