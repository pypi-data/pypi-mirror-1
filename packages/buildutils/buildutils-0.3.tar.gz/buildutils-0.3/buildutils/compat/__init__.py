"""Python 2.2 Backward Compatibility Layer"""

# string.Template
import string
try:
    string.Template
except AttributeError:
    import string_template
    string.Template = string_template.Template

# support for enumerate
try:
    enumerate
except:
    import __builtin__
    __builtin__.enumerate = lambda seq: zip(xrange(len(seq)), seq)

# set type in python 2.3
try:
    set
except:
    import __builtin__
    import sets
    __builtin__.set = sets.Set
    __builtin__.frozenset = sets.ImmutableSet
