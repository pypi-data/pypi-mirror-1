# ./pyxb/bundles/wssplat/raw/wsu.py
# PyXB bindings for NamespaceModule
# NSM:e2891a804ace8fbcc4a500f1dbc94cf01e38e023
# Generated 2009-11-30 18:08:46.167875 by PyXB version 1.1.0
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import StringIO
import pyxb.utils.utility
import pyxb.utils.domutils
import sys

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:b17795a2-de0d-11de-ab1f-001cc05930fc')

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

Namespace = pyxb.namespace.NamespaceForURI(u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd', create_if_missing=True)
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
class tTimestampFault (pyxb.binding.datatypes.QName, pyxb.binding.basis.enumeration_mixin):

    """
This type defines the fault code value for Timestamp message expiration.
          """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'tTimestampFault')
    _Documentation = u'\nThis type defines the fault code value for Timestamp message expiration.\n          '
tTimestampFault._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=tTimestampFault, enum_prefix=None)
tTimestampFault.wsuMessageExpired = tTimestampFault._CF_enumeration.addEnumeration(unicode_value=u'wsu:MessageExpired')
tTimestampFault._InitializeFacetMap(tTimestampFault._CF_enumeration)
Namespace.addCategoryObject('typeBinding', u'tTimestampFault', tTimestampFault)

# Complex type AttributedDateTime with content type SIMPLE
class AttributedDateTime (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.string
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedDateTime')
    # Base type is pyxb.binding.datatypes.string
    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_AttributedDateTime_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'AttributedDateTime', AttributedDateTime)


# Complex type TimestampType with content type ELEMENT_ONLY
class TimestampType (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'TimestampType')
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Created uses Python identifier Created
    __Created = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Created'), 'Created', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_TimestampType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdCreated', False)

    
    Created = property(__Created.value, __Created.set, None, u'\nThis element allows a creation time to be applied anywhere element wildcards are present.\n            ')

    
    # Element {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Expires uses Python identifier Expires
    __Expires = pyxb.binding.content.ElementUse(pyxb.namespace.ExpandedName(Namespace, u'Expires'), 'Expires', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_TimestampType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdExpires', False)

    
    Expires = property(__Expires.value, __Expires.set, None, u'\nThis element allows an expiration time to be applied anywhere element wildcards are present.\n            ')

    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_TimestampType_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))
    _HasWildcardElement = True

    _ElementMap = {
        __Created.name() : __Created,
        __Expires.name() : __Expires
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'TimestampType', TimestampType)


# Complex type AttributedURI with content type SIMPLE
class AttributedURI (pyxb.binding.basis.complexTypeDefinition):
    _TypeDefinition = pyxb.binding.datatypes.anyURI
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_SIMPLE
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, u'AttributedURI')
    # Base type is pyxb.binding.datatypes.anyURI
    
    # Attribute {http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}Id uses Python identifier Id
    __Id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(Namespace, u'Id'), 'Id', '__httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsd_AttributedURI_httpdocs_oasis_open_orgwss200401oasis_200401_wss_wssecurity_utility_1_0_xsdId', pyxb.binding.datatypes.ID)
    
    Id = property(__Id.value, __Id.set, None, u'\nThis global attribute supports annotating arbitrary elements with an ID.\n          ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))

    _ElementMap = {
        
    }
    _AttributeMap = {
        __Id.name() : __Id
    }
Namespace.addCategoryObject('typeBinding', u'AttributedURI', AttributedURI)


Timestamp = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Timestamp'), TimestampType, documentation=u'\nThis element allows Timestamps to be applied anywhere element wildcards are present,\nincluding as a SOAP header.\n            ')
Namespace.addCategoryObject('elementBinding', Timestamp.name().localName(), Timestamp)

Expires = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), AttributedDateTime, documentation=u'\nThis element allows an expiration time to be applied anywhere element wildcards are present.\n            ')
Namespace.addCategoryObject('elementBinding', Expires.name().localName(), Expires)

Created = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Created'), AttributedDateTime, documentation=u'\nThis element allows a creation time to be applied anywhere element wildcards are present.\n            ')
Namespace.addCategoryObject('elementBinding', Created.name().localName(), Created)



TimestampType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Created'), AttributedDateTime, scope=TimestampType, documentation=u'\nThis element allows a creation time to be applied anywhere element wildcards are present.\n            '))

TimestampType._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, u'Expires'), AttributedDateTime, scope=TimestampType, documentation=u'\nThis element allows an expiration time to be applied anywhere element wildcards are present.\n            '))
TimestampType._ContentModel = pyxb.binding.content.ContentModel(state_map = {
      1 : pyxb.binding.content.ContentModelState(state=1, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=2, element_use=TimestampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Created'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TimestampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))),
    ])
    , 2 : pyxb.binding.content.ContentModelState(state=2, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, element_use=TimestampType._UseForTag(pyxb.namespace.ExpandedName(Namespace, u'Expires'))),
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))),
    ])
    , 3 : pyxb.binding.content.ContentModelState(state=3, is_final=True, transitions=[
        pyxb.binding.content.ContentModelTransition(next_state=3, term=pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=(pyxb.binding.content.Wildcard.NC_not, u'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd'))),
    ])
})
