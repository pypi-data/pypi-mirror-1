def enumerite(arg, base=1):
    """
    like enumerate() but starts counting from
    an arbitrary number (defaults 1)
    """
    for (c,i) in enumerate(arg):
        yield (c+base, i)


def enumboolate(arg, start=True):
    """
    takes [a,b,c,...] and returns [(1,a),(0,b),(1,c),...]
    useful in: for high, i in enumbolite(objects): ....
    for alternated patterns of things
    """
    for (c,i) in enumerate(arg):
        yield (start ^ (c % 2), i)

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
