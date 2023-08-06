# ./pyxb/bundles/opengis/iso19139/raw/gss.py
# PyXB bindings for NamespaceModule
# NSM:e923ac0ba46b21357f20abada700559c6cbc6ea6
# Generated 2009-11-30 18:09:11.167362 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:bad804a6-de0d-11de-a8dc-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.bundles.opengis.raw._nsgroup

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.isotc211.org/2005/gss', create_if_missing=True)
Namespace.configureCategories(['typeBinding', 'elementBinding'])
ModuleRecord = Namespace.lookupModuleRecordByUID(_GenerationUID, create_if_missing=True)
ModuleRecord._setModule(sys.modules[__name__])

def CreateFromDocument (xml_text, default_namespace=None):
    """Parse the given XML and use the document element to create a Python instance."""
    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement)
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=Namespace.fallbackNamespace())
    handler = saxer.getContentHandler()
    saxer.parse(StringIO.StringIO(xml_text))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, _fallback_namespace=default_namespace)

from pyxb.bundles.opengis.raw._nsgroup import GM_Object_PropertyType # {http://www.isotc211.org/2005/gss}GM_Object_PropertyType
from pyxb.bundles.opengis.raw._nsgroup import GM_Point_PropertyType # {http://www.isotc211.org/2005/gss}GM_Point_PropertyType
