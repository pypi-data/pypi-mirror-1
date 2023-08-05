"""
'stolen' from http://starship.python.net/crew/zack/
 thanks: Zachary_Roadhouse@brown.edu
"""

class Autoreload:
    """Creates instance objects that automatically import the corresponding
       module when any attribute is referenced for the first time.  When
       the reference is next used, the module is reloaded.

       Example:
               string = Autoreload('string')
               if something:
	           # Module string gets imported only if the next statement
		   # gets executed
	           string.join(stringlist)

       If the optional dict arguement is used, a reference to the Autoreload
       object will be placed in that dictionary.
    """
       
    def __init__(self, name, dict = None):
	 self.module_name = name
	 self.module = None

	 if dict: dict[name] = self
	
    def __getattr__(self, item): 
	 if self.module:
	      locals()[self.module_name] = self.module
	      self.module = eval('reload(%s)' % self.module_name)
	 else:
	      exec("import " + self.module_name)
	      self.module = locals()[self.module_name]

	 attr = getattr(self.module,item)
	 return attr

# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
