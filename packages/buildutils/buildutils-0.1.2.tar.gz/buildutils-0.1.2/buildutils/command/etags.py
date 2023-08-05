"""
Generate TAGS file.

This command is most useful for Emacs users (although other tools read TAGS
files now too).
"""

from distutils.cmd import Command

class etags(Command):
    description = "generate Emacs TAGS file."
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('command=', 'c',
                     "the etags command [default: etags]"),
                    ('tags-file=', 't',
                     "where to write the TAGS file [default: TAGS]"),
                    ('force', 'f',
                     "force generation of TAGS file even if source files "
                     "haven't changed")]

    boolean_options = ['force']
    
    def initialize_options(self):
        self.command = 'etags'
        self.tags_file = 'TAGS'
        
    def finalize_options(self):
        self.ensure_string('command')
        self.ensure_string('tags_file')
        
    def run(self):
        # we use the build_py command because it provides a bunch
        # of functionality for resolving module names and whatnot
        from distutils.command.build_py import build_py
        base = build_py(self.distribution)
        base.initialize_options()
        base.finalize_options()
        files = base.get_source_files()
        def run_etags():
            args = [self.command, '-lpython', '-o%s' % self.tags_file]
            args += files
            self.spawn(args)
        self.make_file(files, self.tags_file, run_etags, (), 
                       exec_msg='tagging (%d) files...' % len(files))
        
