"""
Build documentation using Pudge.
"""

import glob

from buildutils.cmd import Command
from distutils.errors import *
from distutils import log

class pudge(Command):
    description = "build project documentation using pudge."
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('dest=', 'd',
                    "directory where documentation should be generated."),
                    ('docs=', 'i',
                     "list of restructured text documents to include in "
                     "generated documentation."),
                    ('doc-base=', None,
                     "The base directory for your documents (without this all documents will be written to a flat directory)"),
                    ('force', 'f',
                     "force creation of documentation even if files have not"
                     " been modified"),
                    ('license=', None,
                     "include a standard license document. Current options"
                     " are 'gnu' for the GNU Free Documentation License and"
                     " 'cc' for a Creative Commands Attribution, NonCommercial,"
                     " copyleft license."),
                    ('modules=', 'm',
                     "list of module/package names that should be documented."),
                    ('open', 'o',
                     "open a web browser to view documentation after it has"
                     " been built."),
                    ('pages=', 'p',
                     "list of pages that should be opened in the browser"
                     " when using the --open argument [default: index.html]"),
                    ('stages=', None,
                     "list of generation stages to perform. available"
                     " stages are: copy, docs, reference, index, and source."),
                    ('title=', None,
                     "the title of the documentation set."),
                    ('template-dir=', None,
                     'the directory to look for templates in.'),
                    ('theme=', None,
                     "the name of a theme to use for styling doc."),
                    ('xhtml', 'x',
                     "output documentation as XHTML 1.0 instead of HTML 4.01."
                     " HTML 4.01 is recommended due to browser compatibility issues"
                     " with XHTML 1.0."),
                    ('blog-url=', None,
                     "where you blog about this project"),
                    ('syndication-url=', None,
                     "syndication feed (RSS, Atom) for this project."),
                    ('trac-url=', None,
                     "trac or other issue tracking system"),
                    ('mailing-list-url=', None,
                     "mailing list discussing this project."),
                    ('organization=', None,
                     "your organization name (if applicable)."),
                    ('organization-url=', None,
                     "your organization's url (if applicable)."),
                    ('settings=', None,
                     "settings for the template; one variable assignment per line"),
                    ('exclude-modules=', 'x',
                     "Modules that should be excluded"),
                    ('profile', None,
                     "Profile (time) the commands (use twice to do more detailed profiling)"),
                    ]

    boolean_options = ['xhtml', 'open', 'fragment']
    expanding_options = ['organization-url', 'organization',
                         'mailing-list-url', 'trac-url', 'syndication-url',
                         'blog-url', 'template-dir', 'theme', 'title', 'pages', 'docs',
                         'dest']
    
    def initialize_options(self):
        dist = self.distribution
        self.modules = (dist.packages or []) + (dist.py_modules or [])
        self.dest = 'build/doc'
        self.docs = []
        self.exclude_modules = []
        self.title = dist.name
        self.license = None
        self.xhtml = 0
        self.fragment = 0
        self.force = 0
        self.open = 0
        self.pages = ['index.html']
        self.stages = None
        self.template_dir = None
        self.theme = None
        self.organization = None
        self.organization_url = None
        self.blog_url = None
        self.syndication_url = None
        self.trac_url = None
        self.mailing_list_url = None
        self.doc_base = None
        self.settings = None
        self.profile = 0
        
    def finalize_options(self):
        self.ensure_string_list('modules')
        self.ensure_string_list('docs')
        self.ensure_string_list('pages')
        self.ensure_string_list('stages')
        self.ensure_string_list('exclude_modules')
        self.ensure_string('license')
        self.ensure_string('template_dir')
        self.ensure_string('theme')
        self.ensure_string('organization')
        self.ensure_string('organization_url')
        self.ensure_string('blog_url')
        self.ensure_string('syndication_url')
        self.ensure_string('trac_url')
        self.ensure_string('mailing_list_url')
        self.ensure_string('doc_base')
        if self.settings:
            settings = self.settings
            self.settings = {}
            for line in settings.splitlines():
                line = line.strip()
                if not line:
                    continue
                name, value = line.split('=', 1)
                self.settings[name] = value

        self.require('pudge')
        # we have to use __import__ because of the relative module resolution
        # crap
        self.pudge_module = __import__('pudge.generator')

        allowed_stages = self.pudge_module.generator.Generator.stages
        for item in self.stages or []:
            if item and item not in allowed_stages:
                raise DistutilsArgError(
                    "Stage is unknown: %r (should be one of: %s)"
                    % (item, ', '.join(allowed_stages)))
        
    def run(self):
        pudge = self.pudge_module
        from os.path import isdir, exists
        from os import makedirs
        pudge.log = log
        if not exists(self.dest):
            makedirs(self.dest)
        def generate():
            g = pudge.generator.Generator(self.modules, self.dest,
                                          self.force)
            g.title = self.title or g.title
            # Expand wildcards in docs.
            docs = []
            for filespec in '\n'.join(self.docs).split():
                filenames = glob.glob(filespec)
                filenames.sort()
                docs.extend(filenames)
            g.document_files = docs
            g.stages = self.stages or g.stages
            for opt in ('organization', 'organization_url', 'syndication_url',
                        'trac_url', 'license', 'template_dir', 'theme', 'blog_url',
                        'mailing_list_url', 'doc_base', 'settings',
                        'exclude_modules', 'profile', 'xhtml', 'fragment'):
                setattr(g, opt, getattr(self, opt))
            g.generate()
            if self.open:
                import webbrowser
                from os.path import abspath, join, normpath
                from urllib import pathname2url
                for page in self.pages:
                    url = 'file:'+pathname2url(abspath(join(self.dest, page)))
                    try:
                        webbrowser.open(url)
                    except:
                        log.warn("could not open %r in browser...", url)
        self.execute(generate, (), msg='generating documentation') 
        
