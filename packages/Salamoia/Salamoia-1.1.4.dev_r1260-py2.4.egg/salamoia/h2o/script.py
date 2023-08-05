from salamoia.h2o.decorators import abstract

class Script(object):
    """
    Base class for all 'scripts'.
    A 'script' is an sub program called to do
    some physical work which cannot be handled
    with the configuration database or pam modules,
    such as creating apache virtual host configuration files,
    setting up permissions etc etc.

     These are called scripts because it's possible to write it
    in any scripting language (bash, etc).
     You can write them in python and take advantage of the
    salamoia frameworks.
     When written in python these 'scripts' can also be invoked
    directly by the nacl server or in a separate interpreted
    but shared among the scripts, allowing to share the database
    connection and config file parsing.

    In order to write a script in python you should subclass
    this class and implement the 'run' method.
    
    """
    
    destdir = '/var/lib/salamoia/output'

    @abstract
    def run(self):
        """
        script's entry point
        """

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
