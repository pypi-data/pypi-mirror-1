"""
This script is used to execute all tests in the salamoia distribution
"""
try:
    from pkg_resources import require, resource_listdir, resource_isdir, resource_exists, resource_filename
    
    import sys, unittest, doctest
    
    from salamoia.h2o.functional import partial, rpartial, negp
    import fnmatch

    from optparse import OptionParser
except:
    print "FAILED: loading test_all %s: %s" % (sys.exc_info()[0].__name__, sys.exc_info()[1])
    sys.exit()

def flat(tree, scalarp):
    """
    Move it somewhere
    """
    for node in tree:
        if scalarp(node): 
            yield node
        else:
            for x in flat(node, scalarp):
                yield x

class TestAllTestCase(unittest.TestCase):
    def testUnitFinder(self):
        pass

class UnitFinder(object):
    """
    This class finds every 'tests' package
    """

    def __init__(self, base, excludePackages=[]):
        self.base = base
        self.excludePackages = list(excludePackages)
        self.packages = None

    def _find(self):
        if not self.packages:
            self.packages = self.flatten(self.findPackages(self.base))

    def findModules(self):
        self._find()        
        return self.flatten([self.allModules(x) for x in self.packages if x.endswith('.tests')])

    def findDocFiles(self):
        self._find()        
        return self.flatten([self.allDocFiles(x) for x in self.packages])

    def findDocTestModules(self):
        self._find()        
        return self.flatten([self.allModules(x) for x in self.packages if not x.endswith('.tests')])

    def allModules(self, package):
        return [package+"."+x[:-3] for x in fnmatch.filter(resource_listdir(package, '.'), '*.py') if x != '__init__.py']

    def allDocFiles(self, package):
        return [resource_filename(package, x) for x in fnmatch.filter(resource_listdir(package, '.'), '*.txt')]

    def flatten(self, tree):
        """
        Play some functional-python tricks:

        >>> pred = rpartial(negp(isinstance), list) 

        returns a "predicate" function that returns true
        if the argument is not a list:

        >>> pred(1)
        True
        >>> pred([1])
        False

        the crazy thing is that it works also written this way:
        >>> pred = negp(rpartial(isinstance, list))
        >>> pred(1)
        True
        >>> pred([1])
        False
        
        TODO: move this docstring to functional.py

        (rpartial returns a true function, which can be composed to other functions, and negp does
        a composition with operator.not_)

        """
        return list(flat(tree, rpartial(negp(isinstance), list)))

    def findPackages(self, pack):
        children = [self.findPackages(pack+"."+i) for i in self.dirs(pack)]
        return [pack] + children

    def dirs(self, pack):
        return [x for x in resource_listdir(pack, '.') if self.isPackage(pack, x)]

    def isPackage(self, pack, x):
        return (resource_isdir(pack, x)
                and x not in self.excludePackages 
                and resource_exists(pack, x+'/__init__.py'))

def load_suite():
    finder = UnitFinder('salamoia', ['frontends'])
    suite = unittest.TestLoader().loadTestsFromNames(finder.findModules())

    docFiles = finder.findDocFiles()
    #print "doc", docFiles
    docFileSuites = [doctest.DocFileSuite(file, module_relative=False) for file in docFiles]
    suite.addTests(docFileSuites)

    docTestModules = finder.findDocTestModules()
    for module in docTestModules:
        try:
            suite.addTest(doctest.DocTestSuite(module))
            print "Importing doctest", module
        except ValueError, msg:
            if msg[1] != "has no tests":
                raise
        except ImportError, msg:            
            try:
                from salamoia.h2o.logioni import Ione
                Ione.setLogMode('stderr')
                Ione.exception('Error importing doctest', module, traceback=True)
            except ImportError:
                print "Error importing doctest", module, msg
            raise

    return suite

def run_tests():
    """
    Find test unit modules
    """
    suite = load_suite()

    unittest.TextTestRunner(verbosity=2).run(suite)

def test_all():
    try:
        run_tests()
    except:
        import traceback
        traceback.print_exc()
        print "FAILED: uncatched exception %s: %s" % (sys.exc_info()[0].__name__, sys.exc_info()[1])

def debug_all():
    suite = load_suite()

    import pdb
    #pdb.runcall(suite.debug)
    try:
        suite.debug()

    except doctest.UnexpectedException, unex:
        pdb.post_mortem(unex.exc_info[2])
    except:
        pdb.post_mortem(sys.exc_info()[2])
        

if __name__ == '__main__':
    opt = OptionParser()
    opt.add_option('-d', '--debug', action="store_true", dest="debug", default=False, help="run in pdb")

    options, args = opt.parse_args()

    if options.debug:
        debug_all()
    else:
        test_all()

