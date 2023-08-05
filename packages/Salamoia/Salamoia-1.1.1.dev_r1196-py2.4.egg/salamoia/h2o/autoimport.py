"""
'stolen' from http://starship.python.net/crew/zack/
 thanks: Zachary_Roadhouse@brown.edu
"""

class Autoimport:
    """Creates instance objects that automatically import the corresponding
       module when any attribute is referenced.
       
       Example:
               string = Autoimport('string', locals())
               if something:
	           # Module string gets imported only if the next statement
		   # gets executed
	           string.join(stringlist)
    """
       
    def __init__(self, name, dict):
        self.module_name = name
	self.dict = dict
	
    def __getattr__(self, item):
	exec("import %s" % self.module_name)
	module = locals()[self.module_name]

	# Insert module in caller's dictionary so future references
	# don't have to go through this class
	self.dict[self.module_name] = module

	attr = getattr(module,item)
	return attr
