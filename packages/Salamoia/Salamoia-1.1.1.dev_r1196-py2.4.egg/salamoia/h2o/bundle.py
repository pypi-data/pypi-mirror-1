"""
Implementation of salamoia bundles
"""

__all__ = ['Bundle', 'Description', 'BundleDescription']

from pkg_resources import resource_filename
from salamoia.h2o.pathelp import path as Path

from cStringIO import StringIO

class Bundle(object):
    """
    A bundle is a collection of packages
    """

    def __init__(self, egg):
        # chicken in egg...
        from bundledescription import BundleDescription

        self.egg = egg

        self.description = BundleDescription(self.bundleMetadataWrapper())

    def filename(self, path):
        """
        Given a file path relative to this bundle this method will return an
        absolute path of the (eventually) unzipped resource.
        """
        return self.egg.get_resource_filename(resource_filename.im_self, path)

    def resourceWrapper(self, path):
        """
        Return a ResourceWrapper wrapper for the named resource file
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
        self.description.activate()

    def __repr__(self):
        return "<Bundle %s: %s>" % (self.egg.key, self.egg.location)

class AbstractWrapper(object):
    def __init__(self, bundle):
        self.bundle = bundle

class MetadataWrapper(AbstractWrapper):
    """
    Like ResourceWrapper but for egg metadata.

    Egg metadata are treated with a slightly different api at setuptools level.
    """

    def __init__(self, name, bundle=None):
        super(MetadataWrapper, self).__init__(bundle)

        self.name = name

    def open(self):        
        return StringIO(self.bundle.egg.get_metadata(self.name))

class ResourceWrapper(AbstractWrapper):
    """
    A resource wrapper helps using resources (files) inside bundles.
    When bundles are packaged as egg (zip) files, it transparently decompress them.

    Wrappers keep a reference to the path and to the associated bundle, so that relative paths
    can be easly computed.

    The convenience `open` method is provided to abstract the need to access a filesystem path.
    In future a more direct way to get a stream to an archived file decompressed on fly (zlib for example)
    without the need of temporary storage. Using `open` will handle that transparently.

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

from salamoia.h2o.xmlparser import *

class Description(RootElement):
    """
    This is the abstract class for top level xml description files (like schema, service etc)
    """
    def activate(self):
        """
        This method will be called when the bundle is activated.
        Usually here the feature will be registered in the system
        """
        pass


