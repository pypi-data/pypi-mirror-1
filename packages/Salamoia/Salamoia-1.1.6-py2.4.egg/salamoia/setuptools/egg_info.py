"""
This module implements extensions for setuptools setup() keywords
"""
from cStringIO import StringIO
import os

from distutils.errors import DistutilsSetupError

__all__ = ['check_salamoia_bundle','write_salamoia_bundle']

def check_salamoia_bundle(dist, attr, value):
    """
    This function checks to see if the salamoia_bundle value is in the correct format, ie
    a dictionary of lists of strings
    
    """

    def check():
        if not isinstance(value, dict):
            return False
        for x in value.keys():
            if not isinstance(value[x], list):
                return False
                
            for y in value[x]:
                if not (isinstance(y, str) or isinstance(y, dict)):
                    return False
        return True

    if not check():
        raise DistutilsSetupError(
            "%r must be a dictionary of lists of strings or dicts (got %r)" % (attr,value)
            )


def write_salamoia_bundle(cmd, basename, filename):
    """
    This function creates a basic  salamoia_bundle.xml file from a dictionary
    """
    argname = os.path.splitext(basename)[0]
    value = getattr(cmd.distribution, argname, None)

    if value is None:
        return

    s = StringIO()

    print >>s, '<bundle name="%s">' % (cmd.distribution.get_name())
    for k in value:
        for p in value[k]:
            if isinstance(p, dict):
                attrs = ['%s="%s"' % (a,p[a]) for a in p]
                print >>s, '  <%s %s/>' % (k, ' '.join(attrs))
            else:
                print >>s, '  <%s path="%s"/>' % (k, p)
    print >>s, "</bundle>"

    cmd.write_or_delete_file(argname, filename, s.getvalue())


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
