# ./pyxb/bundles/wssplat/raw/whttp.py
# PyXB bindings for NamespaceModule
# NSM:b6d8cfb74f55bcb68c30cab97a9555b1fa1c0cfa
# Generated 2009-11-30 18:08:44.116099 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b0324476-de0d-11de-ada0-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsdl20

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/ns/wsdl/http', create_if_missing=True)
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
class STD_ANON_1 (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_1._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_1, enum_prefix=None)
STD_ANON_1.any = STD_ANON_1._CF_enumeration.addEnumeration(unicode_value=u'#any')
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_enumeration)

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_2 (pyxb.binding.basis.STD_union):

    """Simple type that is a union of pyxb.binding.datatypes.int, STD_ANON_1."""

    _ExpandedName = None
    _Documentation = None

    _MemberTypes = ( pyxb.binding.datatypes.int, STD_ANON_1, )
STD_ANON_2._CF_pattern = pyxb.binding.facets.CF_pattern()
STD_ANON_2._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_2)
STD_ANON_2.any = u'#any'                          # originally STD_ANON_1.any
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_pattern,
   STD_ANON_2._CF_enumeration)

# Atomic SimpleTypeDefinition
class queryParameterType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'queryParameterType')
    _Documentation = None
queryParameterType._CF_length = pyxb.binding.facets.CF_length(value=pyxb.binding.datatypes.nonNegativeInteger(1L))
queryParameterType._CF_pattern = pyxb.binding.facets.CF_pattern()
queryParameterType._CF_pattern.addPattern(pattern=u"[&;a-zA-Z0-9\\-\\._~!$'\\(\\):@/\\?\\*\\+,]{1,1}")
queryParameterType._InitializeFacetMap(queryParameterType._CF_length,
   queryParameterType._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'queryParameterType', queryParameterType)

# Atomic SimpleTypeDefinition
class STD_ANON_3 (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = None
    _Documentation = None
STD_ANON_3._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_3, enum_prefix=None)
STD_ANON_3.basic = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'basic')
STD_ANON_3.digest = STD_ANON_3._CF_enumeration.addEnumeration(unicode_value=u'digest')
STD_ANON_3._InitializeFacetMap(STD_ANON_3._CF_enumeration)

# Atomic SimpleTypeDefinition
class httpTokenType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'httpTokenType')
    _Documentation = None
httpTokenType._CF_pattern = pyxb.binding.facets.CF_pattern()
httpTokenType._CF_pattern.addPattern(pattern=u"[!#-'*+\\-.0-9A-Z^-z|~]+")
httpTokenType._InitializeFacetMap(httpTokenType._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'httpTokenType', httpTokenType)

# Atomic SimpleTypeDefinition
class versionType (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'versionType')
    _Documentation = None
versionType._CF_pattern = pyxb.binding.facets.CF_pattern()
versionType._CF_pattern.addPattern(pattern=u'[0-9]+\\.[0-9]+')
versionType._InitializeFacetMap(versionType._CF_pattern)
Namespace.addCategoryObject('typeBinding', u'versionType', versionType)

# Complex type CTD_ANON_1 with content type ELEMENT_ONLY
class CTD_ANON_1 (pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'required'), 'required', '__httpwww_w3_orgnswsdlhttp_CTD_ANON_1_required', pyxb.binding.datatypes.boolean)
    
    required = property(__required.value, __required.set, None, None)

    
    # Attribute type uses Python identifier type
    __type = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'type'), 'type', '__httpwww_w3_orgnswsdlhttp_CTD_ANON_1_type', pyxb.binding.datatypes.QName, required=True)
    
    type = property(__type.value, __type.set, None, None)

    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'name'), 'name', '__httpwww_w3_orgnswsdlhttp_CTD_ANON_1_name', httpTokenType, required=True)
    
    name = property(__name.value, __name.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))

    _ElementMap = pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __required.name() : __required,
        __type.name() : __type,
        __name.name() : __name
    })



header = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'header'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', header.name().localName(), header)


CTD_ANON_1._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/ns/wsdl'), u'documentation'))),
    ])
})
