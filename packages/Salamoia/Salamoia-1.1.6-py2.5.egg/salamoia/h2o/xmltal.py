from salamoia.h2o.logioni import Ione
from salamoia.h2o.config import Config

from salamoia.tales.tales import Context, ExpressionEngine
from salamoia.tales.expressions import StringExpr, PathExpr, NotExpr, DeferExpr
from salamoia.tales.pythonexpr import PythonExpr

class QueryExpr(object):
    """
    Implements the "query: expr from searchspec" expression

    Search spects simply select the objects matching a given pattern but
    doesn't allow to selects specific attributes and operate on them.

    Describing the default and initial values in schemas is often necessary to find an objects
    (usually selected using a max() aggregate) and then operate on some attributes using
    an expression, for example:

    query: int(uidNumber) + 1 from one max(uidNumber) and type=user

    TODO: it would be nice to support multiple from search specifications.
       the problem is the if the two resultsets have attributes with the same name it is necessary to prefix them:

       query: min(int(U.maxEmail), int(C.maxEmail)) from type=user and min(creationTime) as U, type=config and key=baseConf as F

       it would also be nice if the result of one search could be used as a variabile in the next search spec, in order
       to quickly cascade searches and use powerful expressions.
    """

    def __init__(self, name, expr, engine):
        self._s = expr = expr.lstrip()
                    
    def __call__(self, econtext):
        """
        perhaps use a full blown tpg parser.
        """
        onlyOne = False
                
        service = econtext.getValue("context")._service
        (expr, spec) = self._s.split("from")

        spec = spec.lstrip();
        if spec.startswith("one"):
            spec = spec.lstrip("one")
            onlyOne = True

        frm = service.fetchPattern(spec)

        globs = {}

        if onlyOne:
            globs = frm[0].__dict__
        else:
            # construct for every attribute a list of values so that
            # attrName[N] = res[N].attrName
            for f in frm:
                for k in f.__dict__.keys():
                    if globs.has_key(k):
                        globs[k].append(f[k])
                    else:
                        globs[k] = [f[k]]
            
        if not frm:
            return None

        return eval(expr, globals(), globs)
                        
    def __repr__(self):
        return '<QueryExpr %s>' % `self._s`


class IntExpr(object):
    """
    Implements the "int:" expression
    """

    def __init__(self, name, expr, engine):
        self._s = expr = expr.lstrip()
                    
    def __call__(self, econtext):
        return int(self._s)
                        
    def __repr__(self):
        return '<IntExpr %s>' % `self._s`

class ConfigExpr(object):
    """
    Handle: 'config: [section] key : type | default'
    
    where everything except 'key' is optional.
    
    Upon execution this expression will call the function defined in the 'accessorMap'
    corresponding to the 'type', with the Config.currentConfig() instance, section, key and default 
    arguments

    'section' is the name of the ConfigParser section.
    """        

    accessorMap = {"string": Config.get,
                   "int": Config.getint,
                   "boolean": Config.getboolean,
                   "path": Config.getpath,
                   "paths": Config.getpaths}

    def __init__(self, name, expr, engine):
        components = [x.strip() for x in expr.split('|')]

        self.section = 'parameters'
        key = components[0]
        if key[0] == '[':
            self.section = key.split(']')[0][1:].strip()
            key = key.split(']')[1].strip()

        typeComponents = [x.strip() for x in key.split(':')]
        key = typeComponents[0]
        
        if len(typeComponents) < 2:
            typeComponents.append("string")
        self.accessor = self.accessorMap[typeComponents[1]]

        self.key = key
        
        self.default = ''
        if len(components) > 1:
            self.default =  components[1]

    def __call__(self, econtext):
        """
        accesses the configuration.

        the configuration is first searched for a value 'key' in the section named 'section'.
        then it's searched for a section named 'bundle::section' (if the context has an associated bundle)
        passing the previous value as default. Then it's searched again for a section named 'service/section';
        still the last value is passed as default.

        This allows the user to override config options with more specific sections.
        

        TODO: enhance with adapters
        """

        res = self.accessor(Config.defaultConfig(), self.section, self.key, self.default)

        # this two pieces of code allows to look in releated sections (bundle::section, service/section)
        context = econtext.getValue('context', None)
        try:
            bundle = context.filewrapper().bundle.egg.key
            if Config.defaultConfig().has_section("%s::%s" % (bundle, self.section)):
                section = "%s::%s" % (bundle, self.section)

                res = self.accessor(Config.defaultConfig(), section, self.key, res)
        except:
            pass

        try:
            service = context._service            
            if Config.defaultConfig().has_section("%s/%s" % (service.serviceName, self.section)):
                section = "%s/%s" % (service.serviceName, self.section)

                res = self.accessor(Config.defaultConfig(), section, self.key, res)
        except:
            pass

        return res

def Engine():
    """
    Returns a new engine with basic namespaces:

    path
    string
    python
    not
    defer
    int
    config

    defaults to 'path' namespace
    """

    e = ExpressionEngine()
    reg = e.registerType
    for pt in PathExpr._default_type_names:
        reg(pt, PathExpr)
    reg('string', StringExpr)
    reg('python', PythonExpr)
    reg('not', NotExpr)
    reg('defer', DeferExpr)
    reg('int', IntExpr)
    reg('query', QueryExpr)
    reg('config', ConfigExpr)
    #e.registerBaseName('modules', SimpleModuleImporter())
    return e

def StringEngine():
    """
    Like Engine() but returns an engine with 'string' default namespace
    """
    e = Engine()
    del e.types['standard']
    e.registerType('standard', StringExpr)
    return e

def PythonEngine():
    """
    Like Engine() but returns an engine with 'string' default namespace
    """
    e = Engine()
    del e.types['standard']
    e.registerType('standard', PythonExpr)
    return e

PythonEngine = PythonEngine()
StaticEngine = StringEngine()
StringEngine = StringEngine()
