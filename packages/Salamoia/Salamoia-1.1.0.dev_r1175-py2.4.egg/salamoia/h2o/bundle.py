"""
Implementation of salamoia bundles
"""

__all__ = ['Bundle']

from pkg_resources import resource_filename
from salamoia.h2o.pathelp import path as Path

from cStringIO import StringIO

class Bundle(object):
    """
    A bundle is a collection of packages
    """

    def __init__(self, egg):
        self.egg = egg

        self.description = BundleDescription(self.bundleMetadataWrapper())

    def filename(self, path):
        return self.egg.get_resource_filename(resource_filename.im_self, path)

    def resourceWrapper(self, path):
        """
        Return a wrapper for the named resource file
        """
        return ResourceWrapper(path, self)

    def metadataWrapper(self, name):
        """
        Return a wrapper for the named metadata
        """
        return MetadataWrapper(name, self)

    def bundleMetadataWrapper(self):
        """
        return a wrapper for salamoia_bundle.xml
        """
        return self.metadataWrapper("salamoia_bundle.xml")

    def activate(self):
        self.egg.activate()

class AbstractWrapper(object):
    def __init__(self, bundle):
        self.bundle = bundle

class MetadataWrapper(AbstractWrapper):
    def __init__(self, name, bundle=None):
        super(MetadataWrapper, self).__init__(bundle)

        self.name = name

    def open(self):        
        return StringIO(self.bundle.egg.get_metadata(self.name))

class ResourceWrapper(AbstractWrapper):
    """
    A resource wrapper helps using resources (files) inside bundles.
    When bundles are packaged as egg (zip) files, it transparently decompress them
    """

    def __init__(self, path, bundle=None):
        super(ResourceWrapper, self).__init__(bundle)

        self.path = Path(path)

    def filename(self):
        """
        If a bundle is specified in the resource wrapper then the filename is resolved
        relative to it, otherwise the plain path is returned.

        Useful in order to use ResourceWrapper as a replacement of a filename
        """

        if self.bundle:
            return self.bundle.filename(self.path)    
        return self.path

    def open(self):
        return open(self.filename())

# bundle descriptions

from salamoia.h2o.xmlparser import *
from salamoia.nacl.schema import Schema as SchemaDescription
from salamoia.h2o.service import ServiceDescription

class FeatureElement(Element):
    childClasses = {}
    attributes = ['path']

    parserClass = None

    def init(self):
        super(FeatureElement, self).init()

        #print "loading feature", self.path
        self.content = self.parserClass(self.filewrapper().bundle.resourceWrapper(self.path))

class SchemaElement(FeatureElement):
    parserClass = SchemaDescription

class ServiceElement(FeatureElement):
    parserClass = ServiceDescription

class BundleDescription(RootElement):
    """
    Root element of the XML bundle description found in salamoia_bundle.xml
    """

    childClasses = {'schema': SchemaElement,
                    'service': ServiceElement}
    attributes = ['name']

    rootElementName = 'bundle'
    dtd = 'bundle.dtd'        
