from salamoia.h2o.xmlparser import Element, RootElement

from salamoia.tales.engine import Engine
from salamoia.tales.tales import Context
from salamoia.tales.expressions import StringExpr, PathExpr
from salamoia.tales.pythonexpr import PythonExpr


#from salamoia.macina.backend import Backend
#from salamoia.macina.ldap.object import LDAPObject


class Action(Element):
    attributes = ['name', 'arguments', 'type']

class Check(Element):
    childClasses = {'aaction': Action}

    attributes = ['name', 'type']


class Procedure(Element):
    childClasses = {'command': Command, 'check': Check}

    attributes = ['name', 'pid', 'version', 'arguments', 'type']

class Task(Element):
    childClasses = {'procedure': Procedure, 'check': Check}

    def init(self):
        """
        eventualmente se si deve fare qualcosa durante l'init overraidare
        "init" non "__init__" perche durante __init__ non sono ancora pronti i self.children
        """
        super(Task, self).init()

class Machine(RootElement):
    childClasses = {'task': Task}

    attributes = ['name', 'ip']

    dtd = "tasks.dtd"
