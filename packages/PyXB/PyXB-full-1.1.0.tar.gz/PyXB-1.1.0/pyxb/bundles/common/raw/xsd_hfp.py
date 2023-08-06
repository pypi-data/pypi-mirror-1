# ./pyxb/bundles/common/raw/xsd_hfp.py
# PyXB bindings for NamespaceModule
# NSM:c53ce1768a4a63294762e2dee968b656ae0d44d0
# Generated 2009-11-30 18:08:30.513731 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:a8203e00-de0d-11de-bb14-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI('http://www.w3.org/2001/XMLSchema-hasFacetAndProperty', create_if_missing=True)
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
class STD_ANON_1 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """
       
       
      """

    _ExpandedName = None
    _Documentation = u'\n       \n       \n      '
STD_ANON_1._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_1, enum_prefix=None)
STD_ANON_1.ordered = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'ordered')
STD_ANON_1.bounded = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'bounded')
STD_ANON_1.cardinality = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'cardinality')
STD_ANON_1.numeric = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'numeric')
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_enumeration)

# Atomic SimpleTypeDefinition
class STD_ANON_2 (pyxb.binding.datatypes.NMTOKEN, pyxb.binding.basis.enumeration_mixin):

    """
       
       
      """

    _ExpandedName = None
    _Documentation = u'\n       \n       \n      '
STD_ANON_2._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_2, enum_prefix=None)
STD_ANON_2.length = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'length')
STD_ANON_2.minLength = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'minLength')
STD_ANON_2.maxLength = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'maxLength')
STD_ANON_2.pattern = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'pattern')
STD_ANON_2.enumeration = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'enumeration')
STD_ANON_2.maxInclusive = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'maxInclusive')
STD_ANON_2.maxExclusive = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'maxExclusive')
STD_ANON_2.minInclusive = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'minInclusive')
STD_ANON_2.minExclusive = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'minExclusive')
STD_ANON_2.totalDigits = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'totalDigits')
STD_ANON_2.fractionDigits = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'fractionDigits')
STD_ANON_2.whiteSpace = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'whiteSpace')
STD_ANON_2.maxScale = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'maxScale')
STD_ANON_2.minScale = STD_ANON_2._CF_enumeration.addEnumeration(unicode_value=u'minScale')
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_enumeration)

# Complex type CTD_ANON_1 with content type EMPTY
class CTD_ANON_1 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_org2001XMLSchema_hasFacetAndProperty_CTD_ANON_1_name', STD_ANON_1, required=True)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute value uses Python identifier value_
    __value = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'value'), 'value_', '__httpwww_w3_org2001XMLSchema_hasFacetAndProperty_CTD_ANON_1_value', pyxb.binding.datatypes.normalizedString, required=True)
    
    value_ = property(__value.value, __value.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __name.name() : __name,
        __value.name() : __value
    }



# Complex type CTD_ANON_2 with content type EMPTY
class CTD_ANON_2 (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_org2001XMLSchema_hasFacetAndProperty_CTD_ANON_2_name', STD_ANON_2, required=True)
    
    name = property(__name.value, __name.set, None, None)


    _ElementMap = {
        
    }
    _AttributeMap = {
        __name.name() : __name
    }



hasProperty = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'hasProperty'), CTD_ANON_1, documentation=u'\n    \n    \n    \n   ')
Namespace.addCategoryObject('elementBinding', hasProperty.name().localName(), hasProperty)

hasFacet = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'hasFacet'), CTD_ANON_2, documentation=u'\n   \n   \n   \n   ')
Namespace.addCategoryObject('elementBinding', hasFacet.name().localName(), hasFacet)
