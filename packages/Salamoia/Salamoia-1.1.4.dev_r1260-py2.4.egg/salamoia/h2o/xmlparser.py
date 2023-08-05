from pkg_resources import resource_filename
from xml.dom.ext import Print
from xml.dom.ext.reader.Sax import Reader
from xml.dom import Node
from cStringIO import StringIO
from salamoia.h2o.exception import UnknownXMLChildException

class Element(object):
    """
    This is the base class of the XML parsing helper elements

    One element will be designed as Root element and should be derived from the RootElement class.

    This class's constructor handles recursive walking, automatic child node construction and the <include> directive
    which allows inclusion of single elements or entire xml fragments.
    
    """

    fragmentTagName = "fragment"

    childClasses = {}
    attributes = []
    
    dtd = None

    def childElements(self, root):
        """
        Return all child elements nodes, skipping cdata, comments etc.

        Handle special <include> elemenents.
        Include paths are relative to the path of the containing element.
        Each element carries it's ResourceWrapper (el.filewrapper). When a new file is included
        each of its elements will have a "filewrapper" attribute with a the new path as a base path.
        The carried information is not only the file path but the whole resource wrapper so that includes
        could also spawn bundle boundary.
    
        """

	children = root.childNodes
	for ch in children:
	    if ch.nodeType == Node.ELEMENT_NODE and ch.tagName == "include":
                wrapper = self.filewrapper()
		path = wrapper.path[0:-1] / ch.getAttribute("path") 

                # currentWrapper will be the new reference wrapper for all the included element
                currentWrapper = wrapper.bundle.resourceWrapper(path)

		r = Reader()
                try:
                    doc = r.fromStream(currentWrapper.open(), root.ownerDocument)
                except:
                    print "ERROR including from", path
                    raise

                if doc.firstChild.tagName == self.fragmentTagName:
                    elements = [x for x in doc.firstChild.childNodes if x.nodeType == Node.ELEMENT_NODE]
                else:
                    elements = [doc.firstChild]
                
                for el in elements:
                    el.filewrapper = currentWrapper
                    root.insertBefore(el, ch)

                root.removeChild(ch)

	return [x for x in root.childNodes if x.nodeType == Node.ELEMENT_NODE]

    def root(self):
        if not self.parent:
            return self
        return self.parent.root()

    def filename(self):
        """
        return the path component of the filewrapper    
        """
        return self.filewrapper().path

    def filewrapper(self):
        """
        returns the filewrapper of the current fragment. It walks up the parent chain and finds
        the first element with a _filewrapper attribute. If no <include> directives were used
        then only the root element provides the _filewrapper attribute
        """
        if hasattr(self, "_filewrapper"):
            return self._filewrapper
        return self.parent.filewrapper()

    def buildChild(self, element):
        if not self.childClasses.has_key(element.tagName):
            raise UnknownXMLChildException, "Unknown schema object %s" % (element.tagName)

        # list search non hashed! may be slow. TODO
        res = self.childClasses[element.tagName](element, self)
        if hasattr(element, 'filewrapper'):
            res._filewrapper = element.filewrapper

        res.init()
        return res


    def buildChildren(self):
        self.children = [self.buildChild(x) for x in self.childElements(self.element)]

    def __init__(self, element, parent):
        self.parent = parent

        self.element = element
        self.tagName = element.tagName

        for attr in self.attributes:
            setattr(self, attr, self.getAttribute(attr))

    def init(self):
        self.buildChildren()

    def getAttribute(self, name):
        return self.element.getAttribute(name)

    def findChild(self, type):
        """
        Find first child whose type matches `type`
        """
        for i in self.children:
            if isinstance(i, type):
                return i
        return None

class RootElement(Element):
    """
    This is the class of the root element of the tree

    The main difference from other elements is that it's constructor takes
    the xml filewrapper instead of the dom element.

    The other difference is that it is the only element which has "self.parent == None".
    It can be accessed with "self.root()" from within its children's methods.

    The filewrapper is stored in the @_filewrapper instance variable. Normal children doesn't have a @_filewrapper
    instance variable, but they can ovverride their base if included with a <include> directive. 
    The filewrapper() method will find the correct value, walking upstairs.
    """

    rootElementName = None
    validable = True

    def __init__(self, filewrapper, validate=True):
        if not self.validable:
            validate = False

        self._filewrapper = filewrapper
        stream = filewrapper.open()

        r = Reader(validate=0)
        doc = r.fromStream(stream)
        self.document = doc

        super(RootElement, self).__init__(doc.documentElement, None)

        self.init()

        if validate:
            self.validate()

    def validate(self):
        """
        This method validates the current in-memory xml document against a DTD.
        The DTD name is taken from the @dtd class variable. The file is searched 
        in the package where the root element class is defined. 
        """
        sio = StringIO()

        # ehehe hack
        print >>sio, '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE %s SYSTEM "%s">' % (
            self.rootElementName or self.__class__.__name__.lower(),
            resource_filename(self.__class__.__module__, self.dtd)
            )
        
        Print(self.document.documentElement, sio)
        
        sio.seek(0)
        vr = Reader(validate=1)
        try:
            vr.fromStream(sio)
        except:
            print "XML validation error"
            print "SCHEMA", sio.getvalue()
            raise
        #print "SCHEMA", sio.getvalue()


# -- run the doc tests in this document if invoked as a script
from salamoia.tests import *; runDocTests()
# --
