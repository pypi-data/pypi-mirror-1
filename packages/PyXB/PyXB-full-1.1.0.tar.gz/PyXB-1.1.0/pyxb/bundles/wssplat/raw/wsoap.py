# ./pyxb/bundles/wssplat/raw/wsoap.py
# PyXB bindings for NamespaceModule
# NSM:3a38467dbfe17f8bf02ac4151ad87deda2d076d0
# Generated 2009-11-30 18:08:51.830211 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b4ccf652-de0d-11de-9f5d-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes
import pyxb.bundles.wssplat.wsdl20

Namespace = pyxb.namespace.NamespaceForURI(u'http://www.w3.org/ns/wsdl/soap', create_if_missing=True)
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
class TokenAny (pyxb.binding.datatypes.token, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TokenAny')
    _Documentation = None
TokenAny._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TokenAny, enum_prefix=None)
TokenAny.any = TokenAny._CF_enumeration.addEnumeration(unicode_value=u'#any')
TokenAny._InitializeFacetMap(TokenAny._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'TokenAny', TokenAny)

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_1 (pyxb.binding.basis.STD_union):

    """Simple type that is a union of pyxb.binding.datatypes.QName, TokenAny."""

    _ExpandedName = None
    _Documentation = None

    _MemberTypes = ( pyxb.binding.datatypes.QName, TokenAny, )
STD_ANON_1._CF_pattern = pyxb.binding.facets.CF_pattern()
STD_ANON_1._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_1)
STD_ANON_1.any = u'#any'                          # originally TokenAny.any
STD_ANON_1._InitializeFacetMap(STD_ANON_1._CF_pattern,
   STD_ANON_1._CF_enumeration)

# List SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_2 (pyxb.binding.basis.STD_list):

    """Simple type that is a list of pyxb.binding.datatypes.QName."""

    _ExpandedName = None
    _Documentation = None

    _ItemType = pyxb.binding.datatypes.QName
STD_ANON_2._InitializeFacetMap()

# Union SimpleTypeDefinition
# superclasses pyxb.binding.datatypes.anySimpleType
class STD_ANON_3 (pyxb.binding.basis.STD_union):

    """Simple type that is a union of TokenAny, STD_ANON_2."""

    _ExpandedName = None
    _Documentation = None

    _MemberTypes = ( TokenAny, STD_ANON_2, )
STD_ANON_3._CF_pattern = pyxb.binding.facets.CF_pattern()
STD_ANON_3._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=STD_ANON_3)
STD_ANON_3.any = u'#any'                          # originally TokenAny.any
STD_ANON_3._InitializeFacetMap(STD_ANON_3._CF_pattern,
   STD_ANON_3._CF_enumeration)

# Complex type CTD_ANON_1 with content type ELEMENT_ONLY
class CTD_ANON_1 (pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'required'), 'required', '__httpwww_w3_orgnswsdlsoap_CTD_ANON_1_required', pyxb.binding.datatypes.boolean)
    
    required = property(__required.value, __required.set, None, None)

    
    # Attribute mustUnderstand uses Python identifier mustUnderstand
    __mustUnderstand = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'mustUnderstand'), 'mustUnderstand', '__httpwww_w3_orgnswsdlsoap_CTD_ANON_1_mustUnderstand', pyxb.binding.datatypes.boolean)
    
    mustUnderstand = property(__mustUnderstand.value, __mustUnderstand.set, None, None)

    
    # Attribute element uses Python identifier element
    __element = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'element'), 'element', '__httpwww_w3_orgnswsdlsoap_CTD_ANON_1_element', pyxb.binding.datatypes.QName, required=True)
    
    element = property(__element.value, __element.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))

    _ElementMap = pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __required.name() : __required,
        __mustUnderstand.name() : __mustUnderstand,
        __element.name() : __element
    })



# Complex type CTD_ANON_2 with content type ELEMENT_ONLY
class CTD_ANON_2 (pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = None
    # Base type is pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType
    
    # Element documentation ({http://www.w3.org/ns/wsdl}documentation) inherited from {http://www.w3.org/ns/wsdl}DocumentedType
    
    # Attribute required uses Python identifier required
    __required = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'required'), 'required', '__httpwww_w3_orgnswsdlsoap_CTD_ANON_2_required', pyxb.binding.datatypes.boolean)
    
    required = property(__required.value, __required.set, None, None)

    
    # Attribute ref uses Python identifier ref
    __ref = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, u'ref'), 'ref', '__httpwww_w3_orgnswsdlsoap_CTD_ANON_2_ref', pyxb.binding.datatypes.anyURI, required=True)
    
    ref = property(__ref.value, __ref.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://www.w3.org/ns/wsdl'))

    _ElementMap = pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType._ElementMap.copy()
    _ElementMap.update({
        
    })
    _AttributeMap = pyxb.bundles.wssplat.wsdl20.ExtensibleDocumentedType._AttributeMap.copy()
    _AttributeMap.update({
        __required.name() : __required,
        __ref.name() : __ref
    })



header = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'header'), CTD_ANON_1)
Namespace.addCategoryObject('elementBinding', header.name().localName(), header)

module = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'module'), CTD_ANON_2)
Namespace.addCategoryObject('elementBinding', module.name().localName(), module)


CTD_ANON_1._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_1._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/ns/wsdl'), u'documentation'))),
    ])
})


CTD_ANON_2._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=1, element_use=CTD_ANON_2._UseForTag(pyxb.namespace.ExpandedName(pyxb.namespace.NamespaceForURI(u'http://www.w3.org/ns/wsdl'), u'documentation'))),
    ])
})
