from salamoia.h2o.xmlparser import Element
from salamoia.h2o.bundle import Description

from salamoia.nacl.schema import SchemaDescription
from salamoia.h2o.service import ServiceDescription

from salamoia.h2o.logioni import Ione

__all__ = ['BundleDescription']

class FeatureElement(Element):
    childClasses = {}
    attributes = ['path']

    parserClass = None

    def init(self):
        super(FeatureElement, self).init()

        self.content = self.parserClass(self.filewrapper().bundle.resourceWrapper(self.path))

class SchemaElement(FeatureElement):
    parserClass = SchemaDescription

class ServiceElement(FeatureElement):
    parserClass = ServiceDescription

class BundleDescription(Description):
    """
    Root element of the XML bundle description found in salamoia_bundle.xml
    """

    childClasses = {'schema': SchemaElement,
                    'service': ServiceElement}
    attributes = ['name']

    rootElementName = 'bundle'
    dtd = 'bundle.dtd'        

    def activate(self):
        for i in self.children:
            i.content.activate()

    def __repr__(self):
        return "<Bundle %s>" % (self.name)
