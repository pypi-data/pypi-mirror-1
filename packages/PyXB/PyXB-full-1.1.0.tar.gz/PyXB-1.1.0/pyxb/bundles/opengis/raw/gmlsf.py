# ./pyxb/bundles/opengis/raw/gmlsf.py
# PyXB bindings for NamespaceModule
# NSM:ffd885422e381c03fb347f9c1941318d96f0b846
# Generated 2009-11-30 18:11:21.368611 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:0dfa4ffe-de0e-11de-9f98-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.opengis.net/gmlsf', create_if_missing=True)
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


# Atomic SimpleTypeDefinition
class STD_ANON_1 (pyxb.binding.datatypes.integer, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_1._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_1, enum_prefix=None)
STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'0')
STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'1')
STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'2')
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_enumeration)

ComplianceLevel = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'ComplianceLevel'), STD_ANON_1, documentation=u'\n            Level 0 = no complex-valued properties and minOccurs,maxOccurs\n                      have a value domain of 0 or 1\n            Level 1 = complex-valued properties with no restriction on\n                      minOccurs and maxOccurs\n            Level 2 = no restrictions on type of non-spatial scalar properties \n                      but must only support spatial properties declared in\n                      clause 8\n         ')
Namespace.addCategoryObject('elementBinding', ComplianceLevel.name().localName(), ComplianceLevel)

GMLProfileSchema = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'GMLProfileSchema'), pyxb.binding.datatypes.anyURI, documentation=u'\n            This URI references the profile schema to which a GML\n            application schema conforms.\n         ')
Namespace.addCategoryObject('elementBinding', GMLProfileSchema.name().localName(), GMLProfileSchema)
