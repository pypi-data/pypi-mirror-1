"""Dump meta information about the current project."""

from distutils.cmd import Command

def name_email(name, email):
    if name and email:
        return '%s <%s>' % (name, email)
    else:
        return name or email

def lax_zip(seq1, seq2):
    len1, len2 = len(seq1), len(seq2)
    if len1 > len2:
        seq2 = seq2 + ([(None,None)] * (len1 - len2))
    elif len2 > len1:
        seq1 = seq1 + ([(None,None)] * (len2 - len1))
    return zip(seq1, seq2)

def dump(col1, col2=None):
    attr_len = col2 and 12 or 14
    value_len = 20
    rows = []
    if col2:
        for (n1, v1), (n2, v2) in lax_zip(col1, col2):
            if n1:
                rows.append(('%s:' % n1).ljust(attr_len))
                rows.append(str(v1).ljust(value_len))
            else:
                rows.append(' ' * (attr_len + value_len))
            if n2:
                rows.append(('%s:' % n2).ljust(attr_len))
                rows.append(str(v2).ljust(value_len))
            rows.append('\n')
    else:
        for n, v in col1:
            rows.append(('%s:' % n).ljust(attr_len))
            rows.append(str(v).ljust(value_len))
            rows.append('\n')
    print ''.join(rows)

class info(Command):
    description = "dump various bits of information about this package."
    
    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = []
    
    def initialize_options(self):
        pass
        
    def finalize_options(self):
        pass
        
    def run(self):
        # we use the build_py command because it provides a bunch
        # of functionality for resolving module names and whatnot
        from distutils.command.build_py import build_py
        base = build_py(self.distribution)
        base.initialize_options()
        base.finalize_options()
        self.build_py = base
        self.dump_info()
        
    def dump_info(self):
        # TODO: add keywords, trove classifiers, setuptools dependencies,
        #       
        dist = self.distribution
        print '%s - %s\n' % (dist.get_name(), dist.get_description())
        package_info = [('Name', dist.get_name()),
                        ('Version', dist.get_version()),
                        ('License', dist.get_license())]
        if dist.get_platforms() != ['UNKNOWN']:
            platforms = ', '.join(dist.get_platforms())
        else:
            platforms = 'All (not specified)'
        package_info.append(('Platforms', platforms))
        person_info = []
        if dist.get_author() != 'UNKNOWN':
            author = name_email(dist.get_author(), dist.get_author_email())
            person_info.append(('Author', author))
        if dist.get_maintainer() != 'UNKNOWN':
            maintainer = name_email(dist.get_maintainer(),
                                    dist.get_maintainer_email())
            person_info.append(('Maintainer', maintainer))
        if dist.get_contact() != 'UNKNOWN' and \
               dist.get_contact() != dist.get_author():
            contact = name_email(dist.get_contact(),
                                    dist.get_contact_email())
            person_info.append(('Contact', contact))
        url_info = []
        if dist.get_url():
            url_info.append(('Project URL', '<%s>' % dist.get_url()))
        if dist.get_download_url():
            url_info.append(('Download URL', '<%s>' % dist.get_download_url()))
        dump(package_info, person_info)
        dump(url_info)
        self.dump_trove_cats()
        if dist.get_long_description():
            print 'Description:\n'
            print '    ' + dist.get_long_description().replace('\n', '\n    ')

    
    def dump_trove_cats(self):
        classifiers = self.distribution.get_classifiers()
        if len(classifiers):
            print 'Trove Classifiers:\n'
            for c in classifiers:
                print '    ' + c
            print
