"""
Per ora l'idea di interfaccia e' puramente a sfondo dichiarativo, in modo da poter comunicare astrattamente con altri
mondi senza esporre il nome della classe.

Un'interfaccia puo' essere implementata da una classe sola (in futuro ogni backend avra' un suo scope)

In pratica riveste il ruole che prima aveva TypeSpec.typeMap. Non poteva mantenere il nome "type" perche confliggeva
con un builtin python quindi ho pensato di rendere omaggio a zope con "implements" ma fondamentalmente e' la stessa cosa; 
in effetti ora TypeSpec usa interafce.classMap per implementare la typeMap. 

Il codice normale dovrebbe per ora continuare ad usare TypeSpec e usare di questo modulo solo "implements" che si puo importare 
comodamente da nacl:

from salamoia.nacl import implements

cosi' questo modulo potra' essere libero di cambiare

TODO: generalize out of nacl

"""

from advice import addClassAdvisor
import sys

classMap = {}
reverseClassMap = {}

# ldap object class
objectClassMap = {}
reverseObjectClassMap = {}

def implements(interfaceName):
    frame = sys._getframe(1)
    locals = frame.f_locals

    if (locals is frame.f_globals) or (
        ('__module__' not in locals) and sys.version_info[:3] > (2, 2, 0)):
        raise TypeError(name+" can be used only from a class definition.")

    locals['__implements_advice_data__'] = interfaceName
    addClassAdvisor(_implements_advice, depth=2)

def _implements_advice(cls):
    interfaceName = cls.__dict__['__implements_advice_data__']
    del cls.__implements_advice_data__

    return classImplements(cls, interfaceName)

def classImplements(cls, interfaceName):    
    classMap[interfaceName] = cls
    reverseClassMap[cls] = interfaceName

    objectClassMap[interfaceName] = cls.primaryObjectClass
    reverseObjectClassMap[cls.primaryObjectClass] = interfaceName

    ramap = {}
    for k in cls.attributeMap.keys():
        ramap[cls.attributeMap[k]] = k
    cls.reverseAttributeMap = ramap

    return cls
